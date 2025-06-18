import chromadb
from sentence_transformers import SentenceTransformer
import os
import json

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

def add_documents_to_knowledge_base(collection, documents: list[str], metadatas: list[dict], ids: list[str]):
    """Adds documents to the ChromaDB collection.

    Args:
        collection: The ChromaDB collection object.
        documents (list[str]): List of text documents to add.
        metadatas (list[dict]): List of metadata dictionaries for each document.
        ids (list[str]): List of unique IDs for each document.
    """
    # Generate embeddings for the documents
    embeddings = embedding_model.encode(documents).tolist()
    
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Added {len(documents)} documents to the knowledge base.")

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

def query_knowledge_base(collection, query_text: str, n_results: int = 3):
    """Queries the knowledge base for relevant documents.

    Args:
        collection: The ChromaDB collection object.
        query_text (str): The query string.
        n_results (int): Number of top results to retrieve.

    Returns:
        list: A list of retrieved documents.
    """
    query_embedding = embedding_model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=['documents', 'metadatas']
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

    query_2 = "How to scale my application automatically?"
    results_2 = query_knowledge_base(collection, query_2)
    print(f"\nQuery: '{query_2}'")
    print("Retrieved Documents:")
    for i, doc in enumerate(results_2['documents'][0]):
        print(f"  {i+1}. {doc}")
        print(f"     Metadata: {results_2['metadatas'][0][i]}")
