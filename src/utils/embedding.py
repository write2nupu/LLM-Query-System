from __future__ import annotations

import os
from hashlib import sha256
from typing import cast

import nltk
from dotenv import load_dotenv
from pinecone import IndexModel, Metric, PineconeAsyncio, ServerlessSpec, Vector
from pinecone.db_data import IndexAsyncio
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
nltk.download("punkt")
nltk.download("punkt_tab")

from nltk.tokenize import sent_tokenize

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]


def split_text_naturally(text: str, max_len=512):
    sentences = sent_tokenize(text)
    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_len:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


class EmbeddingGenerator:
    pinecone: PineconeAsyncio = PineconeAsyncio(api_key=PINECONE_API_KEY)
    index: IndexModel

    def __init__(self, model_name: str):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self._cached_chunks: list[str] = []

    def generate_vectors(self, text: str):
        return self.embeddings.embed_query(text)

    async def create_index(self, index_name: str = "hackrx-embeddings"):
        if not await self.pinecone.has_index(index_name):
            self.index = await self.pinecone.create_index(
                name=index_name,
                dimension=384,
                metric=Metric.DOTPRODUCT,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                ),
            )
        self.index = await self.pinecone.describe_index(index_name)
        print(self.index.to_dict())

    async def upsert_embeddings(self, text: str):
        chunks = split_text_naturally(text)

        if not hasattr(self, "index"):
            await self.create_index()
        if not self.pinecone:
            self.pinecone = PineconeAsyncio(api_key=PINECONE_API_KEY)

        if not self.index:
            await self.create_index()

        chunks = [chunk.strip() for chunk in chunks if chunk not in self._cached_chunks]
        if not chunks:
            return

        self._cached_chunks.extend(chunks)

        vectors = [self.generate_vectors(chunk) for chunk in chunks if chunk.strip()]

        await IndexAsyncio(PINECONE_API_KEY, self.index.to_dict()["host"]).upsert(
            vectors=[
                Vector(id=sha256(chunk.encode()).hexdigest(), values=cast(list[float], vector), metadata={"text": chunk})
                for chunk, vector in zip(chunks, vectors)
                if chunk.strip()
            ]
        )

    async def query_embeddings(self, query: str, top_k: int = 5):
        query_vector = self.generate_vectors(query)
        results = await IndexAsyncio(PINECONE_API_KEY, self.index.to_dict()["host"]).query(
            vector=query_vector, top_k=top_k, include_metadata=True
        )
        return results
