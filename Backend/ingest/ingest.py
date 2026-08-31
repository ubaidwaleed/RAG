"""Chunk documents and upsert their embeddings into Pinecone.

CLI usage (ingests data/* into the default namespace): uv run python -m ingest.ingest
"""

from pathlib import Path

from google.genai import types

from clients import gemini_client, pinecone_index
from config import settings
from ingest.parsers import extract_text

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def chunk_text(text: str) -> list[str]:
    size, overlap = settings.chunk_size, settings.chunk_overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = gemini_client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dimension),
    )
    return [e.values for e in result.embeddings]


def upsert_document(source: str, text: str, namespace: str = "") -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    vectors = [
        {
            "id": f"{source}-{i}",
            "values": vector,
            "metadata": {"text": chunk, "source": source},
        }
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings))
    ]

    pinecone_index.upsert(vectors=vectors, namespace=namespace)
    return len(vectors)


def main() -> None:
    total = 0
    for path in DATA_DIR.iterdir():
        if not path.is_file():
            continue
        try:
            text = extract_text(path.name, path.read_bytes())
        except ValueError:
            continue
        total += upsert_document(path.name, text)

    if not total:
        print(f"No supported files found in {DATA_DIR}")
        return

    print(f"Upserted {total} chunks into '{settings.pinecone_index_name}'")


if __name__ == "__main__":
    main()
