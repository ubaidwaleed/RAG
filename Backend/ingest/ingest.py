"""Basic ingestion script: chunk .txt files in data/ and upsert their embeddings into Pinecone.

Run from Backend/ with: uv run python -m ingest.ingest
"""

from pathlib import Path

from google import genai
from google.genai import types
from pinecone import Pinecone, ServerlessSpec

from config import settings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_documents() -> list[tuple[str, str]]:
    return [(p.name, p.read_text(encoding="utf-8")) for p in DATA_DIR.glob("*.txt")]


def chunk_text(text: str) -> list[str]:
    size, overlap = settings.chunk_size, settings.chunk_overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def get_or_create_index(pc: Pinecone):
    existing = [idx["name"] for idx in pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(settings.pinecone_index_name)


def embed(client: genai.Client, texts: list[str]) -> list[list[float]]:
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dimension),
    )
    return [e.values for e in result.embeddings]


def main() -> None:
    client = genai.Client(api_key=settings.gemini_api_key)
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = get_or_create_index(pc)

    vectors = []
    for filename, text in load_documents():
        chunks = chunk_text(text)
        embeddings = embed(client, chunks)
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            vectors.append(
                {
                    "id": f"{filename}-{i}",
                    "values": vector,
                    "metadata": {"text": chunk, "source": filename},
                }
            )

    if not vectors:
        print(f"No .txt files found in {DATA_DIR}")
        return

    index.upsert(vectors=vectors)
    print(f"Upserted {len(vectors)} chunks into '{settings.pinecone_index_name}'")


if __name__ == "__main__":
    main()
