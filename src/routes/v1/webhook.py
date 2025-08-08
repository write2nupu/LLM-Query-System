from __future__ import annotations

import asyncio
from typing import List

from fastapi import APIRouter

from src.models import HackRxData, HackRxResponse
from src.utils import EmbeddingGenerator, GenAI, PDFParser

router = APIRouter(prefix="/hackrx")
pdf_parser = PDFParser()
gen_ai = GenAI()
embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")


async def find_answer(question: str) -> str:
    results = await embedding_generator.query_embeddings(question)
    contexts = [match["metadata"]["text"] for match in results["matches"]]  # type: ignore

    answer = await gen_ai.generate_answer(question, contexts)
    return answer.answer or "No answer found."


@router.post("/run", response_model=HackRxResponse)
async def run_hackrx(data: HackRxData) -> HackRxResponse:
    """
    Process the HackRx data and return answers to the questions.
    """

    answers: List[str] = []
    text = await pdf_parser.parse_pdf(data.documents)
    if not text:
        return HackRxResponse(answers=answers)

    await embedding_generator.upsert_embeddings(text)
    result = []
    for i in range(0, len(data.questions), 10):
        batch_questions = data.questions[i : i + 10]
        tasks = [find_answer(question) for question in batch_questions]
        result.extend(await asyncio.gather(*tasks))

    answers.extend(result)

    return HackRxResponse(answers=answers)
