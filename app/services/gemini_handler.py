import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Use the correct model
model = genai.GenerativeModel(model_name="models/gemini-pro")

def generate_gemini_response(query: str, context: str):
    prompt = f"""
You are a helpful assistant. Given the following context from a PDF document, answer the user's query.

Context:
{context}

Question:
{query}

Answer:"""

    response = model.generate_content(prompt)
    return {"answer": response.text.strip()}
