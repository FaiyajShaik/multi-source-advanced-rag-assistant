from pathlib import Path

from docx import Document
from pypdf import PdfReader


def load_text_file(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def load_pdf_file(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def load_docx_file(file_path: str) -> str:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n\n".join(paragraphs)


def load_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        return load_text_file(file_path)

    if extension == ".pdf":
        return load_pdf_file(file_path)

    if extension == ".docx":
        return load_docx_file(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )