"""Basic RAG agent: embed the query with Gemini, retrieve context from Pinecone, ask Groq."""

from google import genai
from google.genai import types
from groq import Groq
from pinecone import Pinecone

from config import settings

_client = genai.Client(api_key=settings.gemini_api_key)
_groq_client = Groq(api_key=settings.groq_api_key)
_pc = Pinecone(api_key=settings.pinecone_api_key)
_index = _pc.Index(settings.pinecone_index_name)

PROMPT_TEMPLATE = """Answer the question using only the context below. \
If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}
"""


def retrieve(query: str) -> list[str]:
    query_embedding = _client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dimension),
    ).embeddings[0].values

    results = _index.query(vector=query_embedding, top_k=settings.top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]


def answer_query(query: str) -> str:
    chunks = retrieve(query)
    context = "\n\n".join(chunks) if chunks else "No relevant context found."

    prompt = PROMPT_TEMPLATE.format(context=context, question=query)
    completion = _groq_client.chat.completions.create(
        model=settings.groq_llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content
