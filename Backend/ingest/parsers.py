"""Text extraction for uploaded documents."""

from io import BytesIO
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix in (".txt", ".md"):
        return content.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        document = DocxDocument(BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(f"Unsupported file type: {suffix}")
