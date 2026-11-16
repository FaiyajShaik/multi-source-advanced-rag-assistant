
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
)


# Load environment variables from the backend/.env file.
BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV_PATH)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError(
        "QDRANT_URL and QDRANT_API_KEY must be configured in backend/.env."
    )


# Connect to Qdrant Cloud.
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=30,
)

COLLECTION_NAME = "documents"


def create_collection():
    """
    Create the documents collection if it does not exist.
    Ensure required keyword payload indexes exist.

    Existing collection data is preserved.
    """
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE,
            ),
        )

    # Required for filtering uploads and websites by source_type.
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="source_type",
        field_schema=PayloadSchemaType.KEYWORD,
        wait=True,
    )

    # Required for filtering documents by document_id.
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="document_id",
        field_schema=PayloadSchemaType.KEYWORD,
        wait=True,
    )

def recreate_collection():
    """
    Delete and recreate the collection.

    WARNING:
    This permanently deletes all documents and vectors
    stored in the collection. Do not call during normal use.
    """
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    create_collection()


def calculate_file_hash(file_path: str | Path) -> str:
    """
    Calculate the SHA-256 hash of a file's actual contents.
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def document_content_exists(content_hash: str) -> bool:
    """
    Check whether an uploaded document with the same content
    already exists in Qdrant.

    Supports older uploaded documents that do not have a
    content_hash stored in their Qdrant payload.
    """
    if not client.collection_exists(COLLECTION_NAME):
        return False

    points = _scroll_all_points(source_type="upload")

    checked_documents = set()

    for point in points:
        payload = point.payload or {}

        document_id = payload.get("document_id")

        if not document_id or document_id in checked_documents:
            continue

        checked_documents.add(document_id)

        # Check the hash stored in the Qdrant payload first.
        existing_hash = payload.get("content_hash")

        if existing_hash:
            if existing_hash == content_hash:
                return True

            continue

        # Fallback for documents uploaded before hash tracking
        # was implemented.
        source = payload.get("source")

        if not source:
            continue

        source_path = Path(source)

        try:
            if source_path.is_file():
                existing_hash = calculate_file_hash(source_path)

                if existing_hash == content_hash:
                    return True

        except (OSError, PermissionError):
            continue

    return False


def search_vectors(
    query_embedding: list[float],
    limit: int = 3,
    source_types: list[str] | None = None,
    document_ids: list[str] | None = None,
):
    """
    Search Qdrant Cloud using dense vector similarity.

    Supports filtering by source type and document IDs.
    """
    must_conditions = []

    if source_types:
        must_conditions.append(
            FieldCondition(
                key="source_type",
                match=MatchAny(any=source_types),
            )
        )

    if document_ids:
        must_conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchAny(any=document_ids),
            )
        )

    query_filter = (
        Filter(must=must_conditions)
        if must_conditions
        else None
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=limit,
    )

    points = results.points

    if not points:
        return []

    scores = [point.score for point in points]

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        normalized_scores = [1.0] * len(scores)
    else:
        normalized_scores = [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]

    return [
        {
            "text": point.payload["text"],
            "source": point.payload["source"],
            "source_type": point.payload.get("source_type", "unknown"),
            "page_title": point.payload.get("page_title"),
            "document_id": point.payload.get("document_id"),
            "chunk_id": point.payload.get("chunk_id"),
            "filename": point.payload.get("filename"),
            "score": normalized_score,
        }
        for point, normalized_score in zip(points, normalized_scores)
    ]


def _scroll_all_points(source_type: str | None = None):
    """
    Retrieve all points from the documents collection,
    optionally filtering by source type.
    """
    if not client.collection_exists(COLLECTION_NAME):
        return []

    query_filter = None

    if source_type:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value=source_type),
                )
            ]
        )

    all_points = []
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=query_filter,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        all_points.extend(results)

        if next_offset is None:
            break

        offset = next_offset

    return all_points


def get_all_documents():
    """
    Return all indexed document chunks.
    """
    points = _scroll_all_points()

    return [
        {
            "text": point.payload["text"],
            "source": point.payload["source"],
            "source_type": point.payload.get("source_type", "unknown"),
            "page_title": point.payload.get("page_title"),
            "document_id": point.payload.get("document_id"),
            "chunk_id": point.payload.get("chunk_id"),
            "filename": point.payload.get("filename"),
        }
        for point in points
        if point.payload and point.payload.get("text")
    ]


def _group_documents(source_type: str):
    """
    Group indexed chunks by their original document.
    """
    points = _scroll_all_points(source_type=source_type)
    grouped = {}

    for point in points:
        payload = point.payload or {}

        document_id = payload.get("document_id")
        source = payload.get("source")

        if not document_id or not source:
            continue

        if document_id not in grouped:
            grouped[document_id] = {
                "document_id": document_id,
                "source": source,
                "filename": payload.get("filename") or Path(source).name,
                "page_title": payload.get("page_title"),
                "chunks_count": 0,
            }

        grouped[document_id]["chunks_count"] += 1

        if (
            not grouped[document_id]["page_title"]
            and payload.get("page_title")
        ):
            grouped[document_id]["page_title"] = payload["page_title"]

    return list(grouped.values())


def get_uploaded_documents():
    """
    Return uploaded documents grouped by document ID.
    """
    return sorted(
        _group_documents("upload"),
        key=lambda document: document["filename"].lower(),
    )


def get_indexed_websites():
    """
    Return indexed websites grouped by document ID.
    """
    return sorted(
        _group_documents("website"),
        key=lambda website: website["source"].lower(),
    )


def delete_temporary_documents():
    """
    Delete only temporary uploads and websites.

    Permanent Knowledge Base records are deliberately excluded.
    """
    if not client.collection_exists(COLLECTION_NAME):
        return 0

    temporary_filter = Filter(
        must=[
            FieldCondition(
                key="source_type",
                match=MatchAny(any=["upload", "website"]),
            )
        ]
    )

    count_result = client.count(
        collection_name=COLLECTION_NAME,
        count_filter=temporary_filter,
        exact=True,
    )

    deleted_chunks = count_result.count

    if deleted_chunks:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=temporary_filter,
            wait=True,
        )

    return deleted_chunks
