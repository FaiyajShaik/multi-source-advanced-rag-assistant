
from rank_bm25 import BM25Okapi

from app.rag.vector_store import get_all_documents


class BM25Retriever:
    def __init__(self, documents: list[dict]):
        self.documents = documents

        tokenized_documents = [
            document["text"].lower().split()
            for document in documents
        ]

        self.bm25 = (
            BM25Okapi(tokenized_documents)
            if tokenized_documents
            else None
        )

    def search(self, query: str, limit: int = 3):
        if not self.documents or self.bm25 is None:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        min_score = scores.min()
        max_score = scores.max()

        if max_score == min_score:
            normalized_scores = [1.0] * len(scores)
        else:
            normalized_scores = (
                (scores - min_score) / (max_score - min_score)
            )

        ranked_documents = []

        for document, score in zip(
            self.documents,
            normalized_scores,
        ):
            ranked_documents.append({
                "text": document["text"],
                "source": document["source"],
                "source_type": document.get("source_type", "unknown"),
                "page_title": document.get("page_title"),
                "document_id": document.get("document_id"),
                "chunk_id": document.get("chunk_id"),
                "bm25_score": float(score),
            })

        ranked_documents.sort(
            key=lambda item: item["bm25_score"],
            reverse=True,
        )

        return ranked_documents[:limit]


def create_bm25_retriever(
    source_types: list[str] | None = None,
    document_ids: list[str] | None = None,
):
    documents = get_all_documents()

    if source_types:
        documents = [
            document
            for document in documents
            if document.get("source_type") in source_types
        ]

    if document_ids:
        selected_ids = set(document_ids)

        documents = [
            document
            for document in documents
            if document.get("document_id") in selected_ids
        ]

    return BM25Retriever(documents)
