import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import os
import json
import re
from typing import List, Dict, Tuple
import datetime
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize the embedding model and ChromaDB client
# We'll use a small, efficient model for demonstration purposes.
# For production, consider larger models or fine-tuning.
model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(model_name)

# Define the path for the ChromaDB persistent storage
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db')

# Global BM25 index and mapping
BM25_INDEX = None
BM25_CHUNKS = []
BM25_IDS = []
BM25_METADATAS = []

# Initialize cross-encoder for re-ranking
CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

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
    document_text: str, source: str, resource_type: str = "documentation", max_chunk_size: int = 800, overlap: int = 100
) -> List[Tuple[str, Dict]]:
    """
    Splits a document into semantic chunks based on headings, paragraphs, and sentences, and adds rich metadata.

    Args:
        document_text: The raw text of the document.
        source: The source identifier for the document (e.g., file path).
        resource_type: The type of resource (e.g., documentation, log, metric, etc.).
        max_chunk_size: The target maximum size for a chunk (in characters).
        overlap: The number of characters to overlap between chunks.

    Returns:
        A list of tuples, where each tuple contains the chunk text and its metadata.
    """
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk.tokenize import sent_tokenize

    chunks = []
    # Split by markdown headings (###, ##, #)
    sections = re.split(r'(^#+\s.*$)', document_text, flags=re.MULTILINE)
    current_heading = "General"
    chunk_id_counter = 0
    timestamp = datetime.datetime.utcnow().isoformat()
    content_accumulator = sections[0].strip() if sections[0].strip() else ""
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i+1].strip()
        if content_accumulator:
            paragraphs = [p for p in content_accumulator.split('\n\n') if p.strip()]
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph) > max_chunk_size:
                    sentences = sent_tokenize(paragraph)
                    sub_chunk = ""
                    for sentence in sentences:
                        if len(sub_chunk) + len(sentence) > max_chunk_size:
                            chunks.append((
                                sub_chunk.strip(),
                                {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}",
                                 "resource_type": resource_type, "timestamp": timestamp}
                            ))
                            chunk_id_counter += 1
                            sub_chunk = sub_chunk[-overlap:] + " " + sentence
                        else:
                            sub_chunk += " " + sentence
                    if sub_chunk.strip():
                        chunks.append((
                            sub_chunk.strip(),
                            {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}",
                             "resource_type": resource_type, "timestamp": timestamp}
                        ))
                        chunk_id_counter += 1
                else:
                    chunks.append((
                        paragraph,
                        {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}",
                         "resource_type": resource_type, "timestamp": timestamp}
                    ))
                    chunk_id_counter += 1
        current_heading = heading.lstrip('#').strip()
        content_accumulator = content
    if content_accumulator:
        paragraphs = [p for p in content_accumulator.split('\n\n') if p.strip()]
        for paragraph in paragraphs:
            chunks.append((
                paragraph,
                {"source": source, "heading": current_heading, "chunk_id": f"{source}-{chunk_id_counter}",
                 "resource_type": resource_type, "timestamp": timestamp}
            ))
            chunk_id_counter += 1
    return chunks

def add_documents_to_knowledge_base(collection, documents: list[str], metadatas: list[dict], ids: list[str], dedup_threshold: float = 0.95):
    """
    Chunks documents semantically and adds them to the ChromaDB collection, skipping near-duplicate chunks.
    """
    all_chunks = []
    all_metadatas = []
    all_ids = []
    all_embeddings = []
    for doc, meta, doc_id in zip(documents, metadatas, ids):
        source = meta.get("source", doc_id)
        resource_type = meta.get("resource_type", "documentation")
        chunked_data = semantic_chunker(doc, source, resource_type=resource_type)
        for i, (chunk_text, chunk_meta) in enumerate(chunked_data):
            chunk_embedding = embedding_model.encode([chunk_text])[0]
            is_duplicate = False
            if all_embeddings:
                sims = cosine_similarity([chunk_embedding], all_embeddings)[0]
                if np.max(sims) > dedup_threshold:
                    is_duplicate = True
            if not is_duplicate:
                all_chunks.append(chunk_text)
                all_metadatas.append(chunk_meta)
                all_ids.append(f"{doc_id}_chunk_{i}")
                all_embeddings.append(chunk_embedding)
    if not all_chunks:
        print("No unique chunks were generated from the documents.")
        return
    embeddings = [embedding_model.encode([chunk])[0].tolist() for chunk in all_chunks]
    collection.add(
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
    print(f"Added {len(all_chunks)} unique chunks from {len(documents)} documents to the knowledge base.")

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

def build_bm25_index(collection):
    """Builds a BM25 index over all documents in the collection."""
    global BM25_INDEX, BM25_CHUNKS, BM25_IDS, BM25_METADATAS
    all_docs = collection.get(include=["documents", "metadatas", "ids"])
    BM25_CHUNKS = all_docs["documents"]
    BM25_IDS = all_docs["ids"]
    BM25_METADATAS = all_docs["metadatas"]
    tokenized_corpus = [doc.split() for doc in BM25_CHUNKS]
    BM25_INDEX = BM25Okapi(tokenized_corpus)
    print(f"BM25 index built with {len(BM25_CHUNKS)} chunks.")

def bm25_query(query_text: str, n_results: int = 5):
    """Query the BM25 index for top-n results."""
    global BM25_INDEX, BM25_CHUNKS, BM25_IDS, BM25_METADATAS
    if BM25_INDEX is None:
        return []
    tokenized_query = query_text.split()
    scores = BM25_INDEX.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
    results = []
    for idx in top_indices:
        results.append({
            "document": BM25_CHUNKS[idx],
            "metadata": BM25_METADATAS[idx],
            "id": BM25_IDS[idx],
            "score": scores[idx],
            "retriever": "bm25"
        })
    return results

def cross_encoder_rerank(query_text: str, candidates: list, top_k: int = 5):
    """Re-rank candidates using a cross-encoder."""
    pairs = [(query_text, c["document"]) for c in candidates]
    scores = cross_encoder.predict(pairs)
    for i, c in enumerate(candidates):
        c["cross_score"] = float(scores[i])
    candidates.sort(key=lambda c: c["cross_score"], reverse=True)
    return candidates[:top_k]

def query_knowledge_base(collection, query_text: str, n_results: int = 5, hybrid: bool = True, rerank: bool = True):
    """
    Hybrid query: retrieves from both dense (ChromaDB) and sparse (BM25) retrievers, merges, deduplicates, and returns top results, optionally re-ranked by cross-encoder.
    """
    # Dense retrieval
    query_embedding = embedding_model.encode([query_text]).tolist()
    dense_results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=['documents', 'metadatas', 'distances', 'ids']
    )
    dense_chunks = [
        {
            "document": doc,
            "metadata": meta,
            "id": id_,
            "score": 1.0 - dist if dist is not None else 0.0,
            "retriever": "dense"
        }
        for doc, meta, id_, dist in zip(
            dense_results["documents"][0],
            dense_results["metadatas"][0],
            dense_results["ids"][0],
            dense_results["distances"][0]
        )
    ]
    # Sparse retrieval
    if hybrid:
        bm25_results = bm25_query(query_text, n_results)
    else:
        bm25_results = []
    
    # Merge and deduplicate by id
    all_results = {r["id"]: r for r in dense_chunks}
    for r in bm25_results:
        if r["id"] not in all_results:
            all_results[r["id"]] = r
        else:
            # If document retrieved by both methods, boost the score
            all_results[r["id"]]["score"] = all_results[r["id"]]["score"] * 1.2
            all_results[r["id"]]["retriever"] = "hybrid"
    
    # Convert back to list and sort by score
    merged_results = list(all_results.values())
    merged_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Apply cross-encoder reranking if requested
    if rerank and merged_results:
        merged_results = cross_encoder_rerank(query_text, merged_results, top_k=n_results)
    
    # Ensure we don't return more than n_results
    return merged_results[:n_results]

def hybrid_search(collection, query_text: str, n_results: int = 5, rerank_top_n: int = 10):
    """
    Enhanced hybrid search with reciprocal rank fusion and cross-encoder reranking.
    
    Args:
        collection: ChromaDB collection
        query_text: Query text
        n_results: Number of results to return
        rerank_top_n: Number of top results to rerank
    
    Returns:
        List of search results with documents, metadata, scores
    """
    # Get more initial results for better fusion and reranking
    initial_n = max(n_results * 3, 10)
    
    # Dense retrieval (embeddings)
    query_embedding = embedding_model.encode([query_text]).tolist()
    dense_results = collection.query(
        query_embeddings=query_embedding,
        n_results=initial_n,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format dense results
    dense_chunks = [
        {
            "document": doc,
            "metadata": meta,
            "id": f"dense_{i}",  # Generate synthetic IDs if needed
            "dense_score": 1.0 - dist if dist is not None else 0.0,
            "dense_rank": i + 1,
            "retriever": "dense"
        }
        for i, (doc, meta, dist) in enumerate(zip(
            dense_results["documents"][0],
            dense_results["metadatas"][0],
            dense_results["distances"][0]
        ))
    ]
    
    # Sparse retrieval (BM25)
    bm25_results = bm25_query(query_text, initial_n)
    for i, result in enumerate(bm25_results):
        result["sparse_score"] = result.pop("score", 0.0)
        result["sparse_rank"] = i + 1
    
    # Merge and deduplicate by document content since IDs might not match
    merged_results = {}
    
    # Add dense results first
    for result in dense_chunks:
        doc_content = result["document"]
        merged_results[doc_content] = result
    
    # Add or merge BM25 results
    for result in bm25_results:
        doc_content = result["document"]
        if doc_content in merged_results:
            # Merge with existing result
            existing = merged_results[doc_content]
            existing["sparse_score"] = result["sparse_score"]
            existing["sparse_rank"] = result["sparse_rank"]
            existing["retriever"] = "hybrid"
        else:
            # Add new BM25 result
            result["dense_score"] = 0.0
            result["dense_rank"] = initial_n + 1  # Rank it after all dense results
            merged_results[doc_content] = result
    
    # Apply reciprocal rank fusion
    k = 60  # Constant to mitigate outlier ranks
    for result in merged_results.values():
        dense_rank = result.get("dense_rank", initial_n + 1)
        sparse_rank = result.get("sparse_rank", initial_n + 1)
        
        # Calculate reciprocal rank fusion score
        result["rrf_score"] = 1 / (k + dense_rank) + 1 / (k + sparse_rank)
    
    # Convert to list and sort by RRF score
    results_list = list(merged_results.values())
    results_list.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
    
    # Apply cross-encoder reranking to top candidates
    top_candidates = results_list[:rerank_top_n]
    if top_candidates:
        reranked_results = cross_encoder_rerank(query_text, top_candidates, top_k=n_results)
        
        # Combine reranked results with the rest
        final_results = reranked_results + [r for r in results_list[rerank_top_n:] if r["document"] not in [c["document"] for c in reranked_results]]
        return final_results[:n_results]
    
    return results_list[:n_results]

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
