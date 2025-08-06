import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Get Pinecone credentials from .env
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Connect to existing index
index = pc.Index(pinecone_index_name)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def store_embeddings(text: str):
    # Split text into chunks
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    embeddings = model.encode(chunks).tolist()

    # Create vectors with metadata
    vectors = [
        {
            "id": f"chunk-{i}",
            "values": embeddings[i],
            "metadata": {"text": chunks[i]}
        }
        for i in range(len(chunks))
    ]

    # Upsert into Pinecone
    index.upsert(vectors=vectors)

    return [v["id"] for v in vectors]

def query_pinecone(query: str, top_k=5):
    embedding = model.encode(query).tolist()
    response = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    return response.matches