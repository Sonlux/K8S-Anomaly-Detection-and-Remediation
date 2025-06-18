
-- Enable the pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for chat conversations
CREATE TABLE public.chat_conversations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL DEFAULT 'New Chat',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create table for chat messages
CREATE TABLE public.chat_messages (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES public.chat_conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create table for Kubernetes cluster data
CREATE TABLE public.cluster_data (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  cluster_name TEXT NOT NULL DEFAULT 'minikube',
  data_type TEXT NOT NULL, -- 'nodes', 'pods', 'services', 'deployments', etc.
  data JSONB NOT NULL,
  content_text TEXT, -- For now, we'll use text search instead of vector embeddings
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create table for chat context and knowledge base
CREATE TABLE public.chat_embeddings (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  source_type TEXT NOT NULL, -- 'kubernetes_docs', 'cluster_data', 'troubleshooting'
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security (but allow all operations since no auth)
ALTER TABLE public.chat_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cluster_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_embeddings ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for all tables (no authentication required)
CREATE POLICY "Allow all operations on chat_conversations" ON public.chat_conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on chat_messages" ON public.chat_messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on cluster_data" ON public.cluster_data FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on chat_embeddings" ON public.chat_embeddings FOR ALL USING (true) WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX idx_chat_messages_conversation_id ON public.chat_messages(conversation_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at);
CREATE INDEX idx_cluster_data_type ON public.cluster_data(data_type);
CREATE INDEX idx_cluster_data_cluster_name ON public.cluster_data(cluster_name);
CREATE INDEX idx_chat_embeddings_source_type ON public.chat_embeddings(source_type);

-- Enable full text search on content
CREATE INDEX idx_cluster_data_content_text ON public.cluster_data USING gin(to_tsvector('english', content_text));
CREATE INDEX idx_chat_embeddings_content ON public.chat_embeddings USING gin(to_tsvector('english', content));

-- Insert some sample Kubernetes knowledge for RAG
INSERT INTO public.chat_embeddings (content, source_type, metadata) VALUES 
('Kubernetes pods are the smallest deployable units in Kubernetes. Each pod contains one or more containers that share storage and network.', 'kubernetes_docs', '{"topic": "pods"}'),
('To debug a pod, use kubectl describe pod <pod-name> to see events and kubectl logs <pod-name> to see container logs.', 'troubleshooting', '{"topic": "debugging"}'),
('Kubernetes services provide stable network endpoints for pods. Types include ClusterIP, NodePort, and LoadBalancer.', 'kubernetes_docs', '{"topic": "services"}'),
('CPU and memory limits can be set on containers to prevent resource starvation. Use resources.limits in pod specifications.', 'kubernetes_docs', '{"topic": "resources"}'),
('Kubernetes deployments manage replica sets and provide declarative updates for pods and replica sets.', 'kubernetes_docs', '{"topic": "deployments"}'),
('kubectl get pods shows all pods in the current namespace. Use -o wide for more details.', 'troubleshooting', '{"topic": "kubectl"}'),
('Persistent volumes provide storage that persists beyond pod lifecycle. Use PVCs to claim storage.', 'kubernetes_docs', '{"topic": "storage"}'),
('Ingress controllers manage external access to services. Configure rules for routing traffic.', 'kubernetes_docs', '{"topic": "ingress"}'),
('ConfigMaps store configuration data as key-value pairs. Secrets store sensitive data like passwords.', 'kubernetes_docs', '{"topic": "config"}'),
('Kubernetes namespaces provide logical isolation between different environments or teams.', 'kubernetes_docs', '{"topic": "namespaces"}');
