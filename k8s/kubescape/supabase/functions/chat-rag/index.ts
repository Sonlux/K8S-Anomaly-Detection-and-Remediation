
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  console.log('Function called with method:', req.method)
  
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { message, conversationId } = await req.json()
    console.log('Received message:', message, 'conversationId:', conversationId)
    
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    )

    // Search for relevant context using full-text search
    const { data: contextData } = await supabaseClient
      .from('chat_embeddings')
      .select('content, source_type, metadata')
      .textSearch('content', message, {
        type: 'websearch',
        config: 'english'
      })
      .limit(5)

    // Get recent cluster data that might be relevant
    const { data: clusterData } = await supabaseClient
      .from('cluster_data')
      .select('data_type, data, content_text')
      .textSearch('content_text', message, {
        type: 'websearch',
        config: 'english'
      })
      .limit(3)

    // Build context for the AI
    let context = "You are a Kubernetes expert assistant. Use the following information to answer questions:\n\n"
    
    if (contextData && contextData.length > 0) {
      context += "Kubernetes Knowledge:\n"
      contextData.forEach(item => {
        context += `- ${item.content}\n`
      })
      context += "\n"
    }

    if (clusterData && clusterData.length > 0) {
      context += "Current Cluster Data:\n"
      clusterData.forEach(item => {
        context += `- ${item.data_type}: ${item.content_text || JSON.stringify(item.data).substring(0, 200)}\n`
      })
      context += "\n"
    }

    context += "Please provide helpful, accurate information about Kubernetes based on this context. If you don't have specific information, provide general Kubernetes best practices."

    const nvidiaApiKey = Deno.env.get('NVIDIA_API_KEY')
    console.log('NVIDIA API Key exists:', !!nvidiaApiKey)
    
    if (!nvidiaApiKey) {
      throw new Error('NVIDIA API key not configured')
    }

    // Call NVIDIA API with Llama 3.3 70B Instruct
    console.log('Calling NVIDIA API...')
    const nvidiaResponse = await fetch('https://integrate.api.nvidia.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${nvidiaApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'meta/llama-3.3-70b-instruct',
        messages: [
          { role: 'system', content: context },
          { role: 'user', content: message }
        ],
        max_tokens: 500,
        temperature: 0.7,
      }),
    })

    console.log('NVIDIA API response status:', nvidiaResponse.status)
    const nvidiaData = await nvidiaResponse.json()
    console.log('NVIDIA API response:', nvidiaData)
    
    if (!nvidiaResponse.ok) {
      console.error('NVIDIA API error:', nvidiaData)
      throw new Error(`NVIDIA API error: ${nvidiaData.error?.message || 'Unknown error'}`)
    }

    const aiResponse = nvidiaData.choices[0]?.message?.content || "I'm sorry, I couldn't generate a response."

    // Save the conversation
    if (conversationId) {
      // Save user message
      await supabaseClient
        .from('chat_messages')
        .insert({
          conversation_id: conversationId,
          role: 'user',
          content: message
        })

      // Save AI response
      await supabaseClient
        .from('chat_messages')
        .insert({
          conversation_id: conversationId,
          role: 'assistant',
          content: aiResponse
        })
    }

    console.log('Returning successful response')
    return new Response(
      JSON.stringify({ response: aiResponse }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('Error in chat-rag function:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})
