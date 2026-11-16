from pathlib import Path

from sentence_transformers import CrossEncoder


BACKEND_DIR = Path(__file__).resolve().parents[2]
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MODEL_PATH = BACKEND_DIR / "models" / "reranker"

model_source = str(MODEL_PATH) if MODEL_PATH.exists() else MODEL_NAME

reranker = CrossEncoder(model_source)


def rerank_documents(
    query: str,
    documents: list[dict],
    limit: int = 3,
):
    if not documents:
        return []

    pairs = [
        (query, document["text"])
        for document in documents
    ]

    scores = reranker.predict(pairs)

    ranked_documents = []

    for document, score in zip(documents, scores):
        ranked_documents.append(
            {
                **document,
                "rerank_score": float(score),
            }
        )

    ranked_documents.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked_documents[:limit]