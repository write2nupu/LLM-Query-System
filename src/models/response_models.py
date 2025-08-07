from __future__ import annotations

from typing import List

from pydantic import BaseModel


class HackRxData(BaseModel):
    documents: str
    questions: List[str]


class HackRxResponse(BaseModel):
    answers: List[str]
