
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from openai import APIError, RateLimitError

from app.rag.pipeline import answer_question


router = APIRouter()

SourceType = Literal[
    "all",
    "knowledge_base",
    "upload",
    "website",
]


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Enter a question between 1 and 2000 characters.",
    )

    source_type: SourceType = Field(default="all")

    document_ids: list[str] | None = Field(default=None)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Question cannot be empty or contain only spaces."
            )

        return value

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, value):
        if value is not None:
            value = list(
                dict.fromkeys(
                    document_id.strip()
                    for document_id in value
                    if document_id.strip()
                )
            )

        return value

    def validate_source_selection(self):
        if self.source_type in (
            "knowledge_base",
            "upload",
            "website",
        ):
            if not self.document_ids:
                raise ValueError(
                    f"Select at least one {self.source_type} document."
                )

        elif self.document_ids is not None:
            if not self.document_ids:
                raise ValueError(
                    "Select at least one document to search."
                )


@router.post("/query")
def query_rag(request: QueryRequest):
    try:
        request.validate_source_selection()

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    source_types = (
        None
        if request.source_type == "all"
        else [request.source_type]
    )

    try:
        result = answer_question(
            request.question,
            source_types=source_types,
            document_ids=request.document_ids,
        )

    except RateLimitError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI model provider has reached its usage limit. "
                "Please try again later."
            ),
        )

    except APIError:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
        )

    sources = [
        {
            "source": document["source"],
            "source_type": document.get("source_type", "unknown"),
            "page_title": document.get("page_title"),
            "document_id": document.get("document_id"),
            "chunk_id": document.get("chunk_id"),
            "text": document["text"],
        }
        for document in result["sources"]
    ]

    return {
        "answer": result["answer"],
        "sources": sources,
    }
