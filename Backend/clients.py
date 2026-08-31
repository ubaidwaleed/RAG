"""Shared provider clients, instantiated once and imported everywhere else."""

from google import genai
from groq import Groq
from pinecone import Pinecone, ServerlessSpec

from config import settings

gemini_client = genai.Client(api_key=settings.gemini_api_key)
groq_client = Groq(api_key=settings.groq_api_key)

_pc = Pinecone(api_key=settings.pinecone_api_key)


def _get_or_create_index():
    existing = [idx["name"] for idx in _pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        _pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return _pc.Index(settings.pinecone_index_name)


pinecone_index = _get_or_create_index()
