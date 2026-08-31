"""Basic RAG agent: embed the query with Gemini, retrieve context from Pinecone, ask Groq."""

from google.genai import types

from clients import gemini_client, groq_client, pinecone_index
from config import settings

PROMPT_TEMPLATE = """Answer the question using only the context below. \
If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}
"""


def retrieve(query: str, namespace: str = "") -> list[str]:
    query_embedding = gemini_client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dimension),
    ).embeddings[0].values

    results = pinecone_index.query(
        vector=query_embedding,
        top_k=settings.top_k,
        include_metadata=True,
        namespace=namespace,
    )
    return [match["metadata"]["text"] for match in results["matches"]]


def answer_query(query: str, namespace: str = "") -> str:
    chunks = retrieve(query, namespace)
    context = "\n\n".join(chunks) if chunks else "No relevant context found."

    prompt = PROMPT_TEMPLATE.format(context=context, question=query)
    completion = groq_client.chat.completions.create(
        model=settings.groq_llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content
