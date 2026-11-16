
from pathlib import Path

from app.rag.ingestion import process_document


DOCUMENTS_DIRECTORY = Path("data/documents")

DOCUMENTS_TO_INDEX = [
    {
        "filename": "test_second.txt",
        "document_id": "812725694678a99a39440b50d8a6f33d66f1d9a5cccd82ec4be19c8576131009",
    },
    {
        "filename": "test.txt",
        "document_id": None,
    },
    {
        "filename": "test_policy.docx",
        "document_id": None,
    },
    {
        "filename": "test_policy.pdf",
        "document_id": None,
    },
]


def main():
    for item in DOCUMENTS_TO_INDEX:
        filename = item["filename"]
        file_path = DOCUMENTS_DIRECTORY / filename

        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        print(f"\nIndexing: {filename}")

        try:
            chunks_indexed = process_document(
                file_path=str(file_path),
                document_id=item["document_id"],
                source_type="knowledge_base",
            )

            print(
                f"Successfully indexed {filename}: "
                f"{chunks_indexed} chunks"
            )

        except Exception as exc:
            print(f"Failed to index {filename}: {exc}")


if __name__ == "__main__":
    main()
