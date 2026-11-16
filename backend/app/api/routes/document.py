
import hashlib
import os

from pathlib import Path
from uuid import uuid4
from collections import defaultdict

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.rag.ingestion import process_document
from app.rag.vector_store import (
    get_all_documents,
    get_uploaded_documents,
    delete_temporary_documents,
    document_content_exists,
)


router = APIRouter()


# Vercel deployment filesystem is read-only.
# Use /tmp for temporary upload processing in production.
# Use the project directory during local development.
UPLOAD_DIRECTORY = (
    Path("/tmp/multi_source_rag_uploads")
    if os.getenv("VERCEL")
    else Path("data/uploads")
)


ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
}


def calculate_content_hash(content: bytes) -> str:
    """Calculate SHA-256 using the actual uploaded file contents."""
    return hashlib.sha256(content).hexdigest()


@router.get("/documents/knowledge-base")
def get_knowledge_base_documents():
    documents = get_all_documents()
    unique_documents = {}

    for document in documents:
        if document.get("source_type") != "knowledge_base":
            continue

        document_id = document.get("document_id")
        source = document.get("source")

        if not document_id or not source:
            continue

        unique_documents[document_id] = {
            "document_id": document_id,
            "filename": document.get("filename") or Path(source).name,
        }

    return {"documents": list(unique_documents.values())}


@router.get("/documents/uploads")
def list_uploaded_documents():
    documents = get_uploaded_documents()

    return {
        "documents": documents,
        "total": len(documents),
    }


@router.get("/documents/diagnostics")
def get_document_diagnostics():
    documents = get_all_documents()

    document_summary = defaultdict(
        lambda: {
            "source_type": "unknown",
            "chunks": 0,
        }
    )

    for document in documents:
        source = document.get("source", "unknown")
        document_id = document.get("document_id", "unknown")
        source_type = document.get("source_type", "unknown")

        key = (source, document_id)

        document_summary[key]["source_type"] = source_type
        document_summary[key]["chunks"] += 1

    return {
        "total_chunks": len(documents),
        "documents": [
            {
                "filename": Path(source).name,
                "source": source,
                "document_id": document_id,
                **details,
            }
            for (source, document_id), details
            in document_summary.items()
        ],
    }


@router.post("/documents/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one document.",
        )

    try:
        UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create temporary upload directory: {exc}",
        ) from exc

    successful_uploads = []
    failed_uploads = []

    # Prevent duplicate content within the same upload request.
    request_hashes = set()

    for file in files:
        file_path = None

        if not file.filename:
            failed_uploads.append({
                "filename": "Unknown file",
                "error": "No filename provided.",
            })
            await file.close()
            continue

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            failed_uploads.append({
                "filename": file.filename,
                "error": "Only PDF, DOCX and TXT files are supported.",
            })
            await file.close()
            continue

        try:
            content = await file.read()

            if not content:
                raise ValueError("The selected file is empty.")

            content_hash = calculate_content_hash(content)

            # Check duplicates in the current request.
            if content_hash in request_hashes:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": "This document already exists.",
                })
                continue

            request_hashes.add(content_hash)

            # Check documents already indexed in Qdrant.
            if document_content_exists(content_hash):
                failed_uploads.append({
                    "filename": file.filename,
                    "error": "This document already exists.",
                })
                continue

            document_id = str(uuid4())
            safe_filename = f"{document_id}{extension}"
            file_path = UPLOAD_DIRECTORY / safe_filename

            # Save temporarily for document processing.
            file_path.write_bytes(content)

            chunks_indexed = process_document(
                str(file_path),
                document_id=document_id,
                source_type="upload",
                display_filename=file.filename,
                content_hash=content_hash,
            )

            successful_uploads.append({
                "document_id": document_id,
                "filename": file.filename,
                "source_type": "upload",
                "chunks_indexed": chunks_indexed,
            })

        except Exception as exc:
            failed_uploads.append({
                "filename": file.filename,
                "error": str(exc),
            })

        finally:
            # Qdrant stores the indexed chunks and metadata.
            # The original temporary file is no longer needed.
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                except OSError:
                    pass

            await file.close()

    if not successful_uploads:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No documents could be uploaded.",
                "failures": failed_uploads,
            },
        )

    return {
        "message": "Document upload completed.",
        "documents": successful_uploads,
        "failures": failed_uploads,
        "successful_count": len(successful_uploads),
        "failed_count": len(failed_uploads),
    }


@router.post("/documents/refresh")
def refresh_temporary_data():
    try:
        uploaded_documents = get_uploaded_documents()

        # Delete temporary uploads and websites from Qdrant.
        # Permanent Knowledge Base documents are excluded.
        deleted_chunks = delete_temporary_documents()

        removed_files = 0
        upload_directory = UPLOAD_DIRECTORY.resolve()

        for document in uploaded_documents:
            source = document.get("source")

            if not source:
                continue

            file_path = Path(source).resolve()

            if (
                file_path.parent == upload_directory
                and file_path.is_file()
            ):
                file_path.unlink()
                removed_files += 1

        return {
            "message": "Temporary data refreshed successfully.",
            "deleted_chunks": deleted_chunks,
            "removed_files": removed_files,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh temporary data: {exc}",
        ) from exc
