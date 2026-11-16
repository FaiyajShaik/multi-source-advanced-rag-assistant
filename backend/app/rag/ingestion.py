
import hashlib

from pathlib import Path
from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.rag.document_loader import load_document
from app.rag.chunker import split_text
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import (
    client,
    COLLECTION_NAME,
    create_collection,
)
from app.rag.website_loader import load_website


ALLOWED_SOURCE_TYPES = {
    "knowledge_base",
    "upload",
    "website",
}


def generate_document_id(file_path: str) -> str:
    return hashlib.sha256(
        file_path.encode("utf-8")
    ).hexdigest()


def process_document(
    file_path: str,
    document_id: str | None = None,
    source_type: str = "knowledge_base",
    display_filename: str | None = None,
    content_hash: str | None = None,
):
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"Invalid source type: {source_type}")

    page_title = None

    if source_type == "website":
        website_data = load_website(file_path)
        text = website_data["text"]
        page_title = website_data["page_title"]
    else:
        text = load_document(file_path)

    chunks = split_text(text)

    if not chunks:
        raise ValueError("No text content found in the document.")

    create_collection()

    if document_id is None:
        document_id = generate_document_id(file_path)

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        wait=True,
    )

    filename = display_filename or Path(file_path).name

    points = []

    for chunk in chunks:
        embedding = generate_embedding(chunk)

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": file_path,
                    "source_type": source_type,
                    "document_id": document_id,
                    "chunk_id": str(uuid4()),
                    "page_title": page_title,
                    "filename": filename,
                    "content_hash": (
                        content_hash
                        if source_type == "upload"
                        else None
                    ),
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )

    return len(points)
