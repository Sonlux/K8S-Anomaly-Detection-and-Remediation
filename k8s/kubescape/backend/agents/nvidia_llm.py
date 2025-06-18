from openai import OpenAI
import os
import logging
import json
import traceback
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nvidia_llm")

class NvidiaLLM:
    """Wrapper for NVIDIA's LLM API using Llama 3.3 70B Instruct model"""
    
    def __init__(self, api_key=None):
        """Initialize the NVIDIA LLM client.
        
        Args:
            api_key: NVIDIA API key (default: reads from NVIDIA_API_KEY env var)
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA API key not provided and NVIDIA_API_KEY env var not set")
        
        if not self.api_key.startswith("nvapi-"):
            logger.warning("NVIDIA API key should typically start with 'nvapi-'")
        
        # Initialize the client
        try:
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.api_key
            )
            logger.info("NVIDIA LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NVIDIA LLM client: {str(e)}")
            raise
        
    def generate(self, prompt, model="meta/llama-3.3-70b-instruct", 
                 temperature=0.2, max_tokens=1024, stream=False, top_p=0.7):
        """Generate a response from the NVIDIA LLM.
        
        Args:
            prompt: The prompt to send to the model
            model: The model ID (default: meta/llama-3.3-70b-instruct)
            temperature: Sampling temperature (default: 0.2)
            max_tokens: Maximum tokens to generate (default: 1024)
            stream: Whether to stream the response (default: False)
            top_p: Top-p sampling parameter (default: 0.7)
            
        Returns:
            Generated text if stream=False, or a generator yielding text chunks if stream=True
        """
        try:
            logger.debug(f"Generating response with model: {model}, temperature: {temperature}, top_p: {top_p}")
            logger.debug(f"Prompt: {prompt[:100]}...")
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Return a generator that yields text chunks
                def generate_stream():
                    for chunk in completion:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content
                        else:
                            logger.debug(f"Received chunk with no content in delta")
                return generate_stream()
            else:
                # Return the full response
                try:
                    return completion.choices[0].message.content
                except Exception as e:
                    logger.error(f"Unexpected response structure: {e}")
                    logger.error(f"Response structure: {json.dumps(completion.model_dump(), default=str)}")
                    raise ValueError("Failed to extract content from response")
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            raise
            
    def analyze_k8s_metrics(self, metrics_data, prediction_result):
        """Analyze Kubernetes metrics and provide recommendations.
        
        Args:
            metrics_data: Dictionary containing pod metrics
            prediction_result: Dictionary containing prediction results
            
        Returns:
            Analysis text from the LLM
        """
        prompt = f"""As a Kubernetes expert, analyze these pod metrics and anomaly prediction:

METRICS:
{metrics_data}

PREDICTION:
{prediction_result}

Provide a concise analysis explaining:
1. What's happening with this pod
2. Potential root causes for any detected issues
3. Specific, actionable recommendations to resolve the problems
4. Priority level of the issue (Critical, High, Medium, Low)

If events are present, explain how the event age and count relate to the detected issues.
"""
        
        try:
            return self.generate(prompt, max_tokens=1024, temperature=0.3)
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {str(e)}")
            return f"Error analyzing metrics: {str(e)}"

# Example usage
if __name__ == "__main__":
    try:
        # Read API key from environment or provide directly
        api_key = os.environ.get("NVIDIA_API_KEY")
        
        # Initialize the client
        llm = NvidiaLLM(api_key=api_key)
        
        # Example metrics
        sample_metrics = {
            'CPU Usage (%)': 0.012098631,
            'Memory Usage (%)': 4.747099786,
            'Pod Restarts': 370,
            'Memory Usage (MB)': 18.47939985,
            'Network Receive Bytes': 0.014544437,
            'Network Transmit Bytes': 0.122316709,
            'FS Reads Total (MB)': 0.000586664,
            'FS Writes Total (MB)': 0.000836434,
            'Network Receive Packets Dropped (p/s)': 0,
            'Network Transmit Packets Dropped (p/s)': 0,
            'Ready Containers': 0,
            'Event Reason': 'BackOff',
            'Event Message': 'Back-off restarting failed container',
            'Event Age (minutes)': 120,
            'Event Count': 45
        }
        
        sample_prediction = {
            'predicted_anomaly': 1,
            'anomaly_probability': 0.96,
            'anomaly_type': 'crash_loop'
        }
        
        # Generate analysis
        print("\nGenerating analysis...")
        analysis = llm.analyze_k8s_metrics(sample_metrics, sample_prediction)
        print("\nAnalysis Result:")
        print(analysis)
        
        # Example streaming response
        print("\nStreaming example response:")
        prompt = "What are the most common causes of CrashLoopBackOff in Kubernetes?"
        stream = llm.generate(prompt, stream=True)
        for text in stream:
            print(text, end="")
            
    except Exception as e:
        print(f"Error in example: {str(e)}")