
import ipaddress
import socket

from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from app.rag.ingestion import (
    process_document,
    generate_document_id,
)

from app.rag.vector_store import get_indexed_websites


router = APIRouter()


class WebsiteIngestionRequest(BaseModel):
    url: HttpUrl


def normalize_url(url: str) -> str:
    """
    Normalize URLs so equivalent URLs are treated as duplicates.

    Examples:
    HTTPS://Example.com:443/
    https://example.com

    Both become:
    https://example.com/
    """
    parsed_url = urlparse(url)

    scheme = parsed_url.scheme.lower()
    hostname = (parsed_url.hostname or "").lower()

    if not hostname:
        raise ValueError("Invalid website hostname.")

    # Preserve non-default ports.
    port = parsed_url.port

    if port and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"

    # Preserve path and meaningful query parameters.
    path = parsed_url.path or "/"

    if path != "/":
        path = path.rstrip("/") or "/"

    return urlunparse((
        scheme,
        hostname,
        path,
        parsed_url.params,
        parsed_url.query,
        "",
    ))


def validate_public_url(url: str):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if not hostname:
        raise ValueError("Invalid website hostname.")

    if parsed_url.username or parsed_url.password:
        raise ValueError(
            "URLs containing credentials are not allowed."
        )

    if (
        hostname.lower() == "localhost"
        or hostname.lower().endswith(".localhost")
    ):
        raise ValueError("Localhost URLs are not allowed.")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise ValueError(
            "Unable to resolve website hostname."
        )

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])

        if not ip.is_global:
            raise ValueError(
                "Private or non-public IP addresses are not allowed."
            )


@router.get("/websites")
def list_indexed_websites():
    try:
        websites = get_indexed_websites()

        return {
            "websites": websites,
            "total": len(websites),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load indexed websites: {exc}",
        ) from exc


@router.post("/websites/ingest")
def ingest_website(request: WebsiteIngestionRequest):
    original_url = str(request.url)

    try:
        # Validate the original URL before processing.
        validate_public_url(original_url)

        # Normalize before checking for duplicates.
        url = normalize_url(original_url)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    try:
        existing_websites = get_indexed_websites()

        for website in existing_websites:
            existing_url = website.get("source")

            if not existing_url:
                continue

            try:
                normalized_existing_url = normalize_url(
                    existing_url
                )
            except ValueError:
                continue

            if normalized_existing_url == url:
                raise HTTPException(
                    status_code=409,
                    detail="This website has already been added.",
                )

        document_id = generate_document_id(url)

        chunks_indexed = process_document(
            file_path=url,
            document_id=document_id,
            source_type="website",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Website ingestion failed: {exc}",
        ) from exc

    return {
        "message": "Website ingested successfully.",
        "document_id": document_id,
        "source": url,
        "source_type": "website",
        "chunks_indexed": chunks_indexed,
    }
