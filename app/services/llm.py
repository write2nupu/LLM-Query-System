import os
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from app.db.pinecone_handler import query_pinecone

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_response(user_query: str):
    # Embed query and get top results from Pinecone
    results = query_pinecone(user_query)

    context_chunks = "\n\n".join([
    match.metadata["text"]
    for match in results
    if match.metadata and "text" in match.metadata
])

    prompt = f"""You are an intelligent assistant for insurance policy Q&A.

Policy content:
{context_chunks}

User question: {user_query}

Answer the question clearly. Extract exact clause numbers if available. Respond in this format:
{{
  "answer": "...",
  "clauses": ["Clause X", "Clause Y"],
  "rationale": "..."
}}
"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    response_json = completion.choices[0].message.content.strip()
    return eval(response_json)  # NOTE: use `json.loads` if response is a valid JSON string
