from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


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