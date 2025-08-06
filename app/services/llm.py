from app.services.gemini_handler import generate_gemini_response

def generate_response(query: str):
    # You can also enhance this by pulling relevant chunks from Pinecone
    dummy_context = "This is a placeholder context from your PDF embedding search."
    return generate_gemini_response(query, dummy_context)
