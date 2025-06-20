import chromadb
from sentence_transformers import SentenceTransformer
import os
import json
import re
from typing import List, Dict, Tuple

# Initialize the embedding model and ChromaDB client
# We'll use a small, efficient model for demonstration purposes.
# For production, consider larger models or fine-tuning.
model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(model_name)

# Define the path for the ChromaDB persistent storage
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db')

def get_chroma_client():
    """Initializes and returns a ChromaDB client."""
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client

def get_or_create_collection(client, collection_name="k8s_docs"):
    """Gets or creates a ChromaDB collection."""
    collection = client.get_or_create_collection(name=collection_name)
    return collection

def semantic_chunker(
    document_text: str, source: str, max_chunk_size: int = 800, overlap: int = 100
) -> List[Tuple[str, Dict]]:
    """
    Splits a document into semantic chunks based on headings and paragraphs.

    Args:
        document_text: The raw text of the document.
        source: The source identifier for the document (e.g., file path).
        max_chunk_size: The target maximum size for a chunk (in characters).
        overlap: The number of characters to overlap between chunks.

    Returns:
        A list of tuples, where each tuple contains the chunk text and its metadata.
    """
    chunks = []
    # Split by markdown headings (###, ##, #)
    # This regex will split the text by headings but keep the headings with the following text
    sections = re.split(r'(^#+\s.*$)', document_text, flags=re.MULTILINE)
    
    current_heading = "General"
    chunk_id_counter = 0

    # The first element might be content before the first heading
    content_accumulator = sections[0].strip() if sections[0].strip() else ""
    
    # Process the document in pairs of (heading, content)
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i+1].strip()

        # If there was content before this heading, process it under the previous heading
        if content_accumulator:
            # Further split by paragraphs
            paragraphs = content_accumulator.split('\n\n')
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph) > max_chunk_size:
                    # If a paragraph is too long, split it further by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    sub_chunk = ""
                    for sentence in sentences:
                        if len(sub_chunk) + len(sentence) > max_chunk_size:
                            chunks.append((
                                sub_chunk.strip(),
                                {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}"}
                            ))
                            chunk_id_counter += 1
                            sub_chunk = sub_chunk[-overlap:] + " " + sentence
                        else:
                            sub_chunk += " " + sentence
                    if sub_chunk.strip():
                        chunks.append((
                            sub_chunk.strip(),
                            {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}"}
                        ))
                        chunk_id_counter += 1
                elif paragraph:
                    chunks.append((
                        paragraph,
                        {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}"}
                    ))
                    chunk_id_counter += 1
        
        # Start new section with the current heading
        current_heading = heading.lstrip('#').strip()
        content_accumulator = content

    # Process any remaining content
    if content_accumulator:
        paragraphs = content_accumulator.split('\n\n')
        for paragraph in paragraphs:
             if paragraph:
                chunks.append((
                    paragraph,
                    {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}"}
                ))
                chunk_id_counter += 1

    return chunks

def add_documents_to_knowledge_base(collection, documents: list[str], metadatas: list[dict], ids: list[str]):
    """
    Chunks documents semantically and adds them to the ChromaDB collection.
    """
    all_chunks = []
    all_metadatas = []
    all_ids = []

    for doc, meta, doc_id in zip(documents, metadatas, ids):
        source = meta.get("source", doc_id)
        # Use semantic_chunker to split the document
        chunked_data = semantic_chunker(doc, source)
        
        for i, (chunk_text, chunk_meta) in enumerate(chunked_data):
            all_chunks.append(chunk_text)
            all_metadatas.append(chunk_meta)
            # Create a unique ID for each chunk
            all_ids.append(f"{doc_id}_chunk_{i}")

    if not all_chunks:
        print("No chunks were generated from the documents.")
        return

    # Generate embeddings for the chunks
    embeddings = embedding_model.encode(all_chunks).tolist()
    
    # Add chunks to the collection
    collection.add(
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
    print(f"Added {len(all_chunks)} chunks from {len(documents)} documents to the knowledge base.")

def load_documents_from_json(file_path: str):
    """Loads documents, metadatas, and ids from a JSON file.

    The JSON file should be a list of objects, each with 'document', 'metadata', and 'id' fields.
    """
    documents = []
    metadatas = []
    ids = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                documents.append(item['content']) # Changed from 'document' to 'content'
                metadatas.append(item['metadata'])
                ids.append(item['id'])
        print(f"Successfully loaded {len(documents)} documents from {file_path}.")
        return documents, metadatas, ids
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return [], [], []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return [], [], []
    except KeyError as e:
        print(f"Error: Missing key in JSON data: {e}")
        return [], [], []

def query_knowledge_base(collection, query_text: str, n_results: int = 5):
    """
    Queries the knowledge base for relevant document chunks.
    Now retrieves more chunks to provide richer context.
    """
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    return results

if __name__ == "__main__":
    # Example Usage:
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    # Sample Kubernetes documentation snippets
    sample_docs = [
        "Kubernetes Pods are the smallest deployable units of computing that you can create and manage in Kubernetes.",
        "A Kubernetes Deployment ensures that a specified number of pod replicas are running at any given time.",
        "Kubernetes Services enable network access to a set of Pods. Services can be exposed in different ways, like ClusterIP, NodePort, and LoadBalancer.",
        "If a Pod is stuck in Pending state, it might be due to insufficient resources (CPU, memory) or a problem with the scheduler.",
        "To troubleshoot a CrashLoopBackOff error in a Pod, check the container logs using `kubectl logs <pod-name>` and describe the pod using `kubectl describe pod <pod-name>`.",
        "Horizontal Pod Autoscaler (HPA) automatically scales the number of pod replicas in a Deployment or ReplicaSet based on observed CPU utilization or other select metrics.",
        "PersistentVolumes (PV) are pieces of storage in the cluster that have been provisioned by an administrator or dynamically provisioned using StorageClasses.",
        "PersistentVolumeClaims (PVC) are requests for storage by a user. They consume PV resources.",
        "Minikube is a tool that makes it easy to run Kubernetes locally. It runs a single-node Kubernetes cluster inside a VM on your laptop.",
        "To start Minikube, use the command `minikube start`. You can specify resources with `minikube start --cpus=4 --memory=8192`.",
        "To access services in Minikube, use `minikube service <service-name>` which will open the service URL in your browser.",
        "For accessing the Kubernetes dashboard in Minikube, run `minikube dashboard` which will open the dashboard in your browser.",
        "To enable addons in Minikube such as metrics-server, run `minikube addons enable metrics-server`.",
        "To access Prometheus in Minikube, first ensure the addon is enabled with `minikube addons enable prometheus`, then use port-forwarding with `kubectl port-forward -n monitoring service/prometheus-server 9090:80`."
    ]
    sample_metadatas = [
        {"source": "k8s_docs", "type": "concept"},
        {"source": "k8s_docs", "type": "concept"},
        {"source": "k8s_docs", "type": "concept"},
        {"source": "k8s_troubleshooting", "type": "issue"},
        {"source": "k8s_troubleshooting", "type": "solution"},
        {"source": "k8s_docs", "type": "concept"},
        {"source": "k8s_docs", "type": "concept"},
        {"source": "k8s_docs", "type": "concept"},
        {"source": "minikube_docs", "type": "concept"},
        {"source": "minikube_docs", "type": "command"},
        {"source": "minikube_docs", "type": "command"},
        {"source": "minikube_docs", "type": "command"},
        {"source": "minikube_docs", "type": "command"},
        {"source": "minikube_docs", "type": "command"}
    ]
    sample_ids = [f"doc{i}" for i in range(len(sample_docs))]

    add_documents_to_knowledge_base(collection, sample_docs, sample_metadatas, sample_ids)

    # Example Usage: Load documents from a JSON file
    # Create a sample JSON file named 'k8s_knowledge.json' in the data directory
    # with content like: 
    # [
    #   {"document": "Text of doc 1", "metadata": {"source": "k8s_docs", "type": "concept"}, "id": "doc1"},
    #   {"document": "Text of doc 2", "metadata": {"source": "runbook", "type": "troubleshooting"}, "id": "doc2"}
    # ]
    
    # The add_documents_to_knowledge_base function will now automatically chunk these documents.
    add_documents_to_knowledge_base(collection, sample_docs, sample_metadatas, sample_ids)

    # Example Usage: Load documents from a JSON file
    # The loaded documents will also be chunked automatically.
    knowledge_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'k8s_knowledge.json')
    if os.path.exists(knowledge_file_path):
        new_docs, new_metadatas, new_ids = load_documents_from_json(knowledge_file_path)
        if new_docs:
            add_documents_to_knowledge_base(collection, new_docs, new_metadatas, new_ids)
    else:
        print(f"Knowledge file not found: {knowledge_file_path}. Skipping loading from file.")

    # Test query
    query = "Pod is not starting, what should I do?"
    results = query_knowledge_base(collection, query)

    print(f"\nQuery: '{query}'")
    print("Retrieved Documents:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"  {i+1}. {doc}")
        print(f"     Metadata: {results['metadatas'][0][i]}")
        print(f"     Distance: {results['distances'][0][i]}")

    query_2 = "How to scale my application automatically?"
    results_2 = query_knowledge_base(collection, query_2)
    print(f"\nQuery: '{query_2}'")
    print("Retrieved Documents:")
    for i, doc in enumerate(results_2['documents'][0]):
        print(f"  {i+1}. {doc}")
        print(f"     Metadata: {results_2['metadatas'][0][i]}")
        print(f"     Distance: {results_2['distances'][0][i]}")
