
def reciprocal_rank_fusion(
    ranked_lists: list[tuple[list[dict], str, str]],
    k: int = 60,
) -> list[dict]:
    """
    Combine multiple ranked retrieval lists using RRF.

    Each ranked list contains:
    - Retrieved documents
    - Retrieval method: dense or bm25
    - Query used for retrieval
    """

    combined_results = {}

    for documents, retrieval_type, query in ranked_lists:

        for rank, document in enumerate(documents, start=1):

            result_key = (
                document.get("chunk_id")
                or f"{document.get('source')}::{document['text']}"
            )

            if result_key not in combined_results:
                combined_results[result_key] = {
                    "text": document["text"],
                    "source": document["source"],
                    "source_type": document.get(
                        "source_type",
                        "unknown",
                    ),
                    "page_title": document.get("page_title"),
                    "document_id": document.get("document_id"),
                    "chunk_id": document.get("chunk_id"),
                    "dense_score": 0.0,
                    "bm25_score": 0.0,
                    "rrf_score": 0.0,
                    "matched_queries": [],
                }

            result = combined_results[result_key]

            # Add the RRF contribution for this ranking.
            result["rrf_score"] += 1 / (k + rank)

            # Preserve the original retrieval scores.
            if retrieval_type == "dense":
                result["dense_score"] = max(
                    result["dense_score"],
                    document["score"],
                )

            elif retrieval_type == "bm25":
                result["bm25_score"] = max(
                    result["bm25_score"],
                    document["bm25_score"],
                )

            else:
                raise ValueError(
                    f"Unsupported retrieval type: {retrieval_type}"
                )

            # Track which queries retrieved this document.
            if query not in result["matched_queries"]:
                result["matched_queries"].append(query)

    return sorted(
        combined_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )
