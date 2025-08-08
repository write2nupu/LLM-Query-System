from __future__ import annotations

import os
from json import loads
from typing import List, Optional

from dotenv import load_dotenv
from google import genai
from google.genai.types import Content, GenerateContentConfig, Part
from pydantic import BaseModel

load_dotenv()


class GeminiAnswer(BaseModel):
    answer: Optional[str] = None


class GenAI:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.api_key = os.environ["GEMINI_API_KEY"]
        self.client = genai.Client(vertexai=False, api_key=self.api_key)

    async def generate_answer(self, question: str, contexts: List[str]) -> GeminiAnswer:
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=[
                Content(
                    parts=[
                        Part.from_text(text="Query: " + question),
                    ]
                )
            ],
            config=GenerateContentConfig(
                system_instruction=f"You are a helpful assistant that answers questions based on the provided context. Give verbose one liner answer if possible. Available contexts: {'. '.join(contexts)}",
                response_mime_type="application/json",
                response_schema=GeminiAnswer,
            ),
        )

        if response:
            return GeminiAnswer(**loads(response.text or "{}"))

        return GeminiAnswer(answer=None)
