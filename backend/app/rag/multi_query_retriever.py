
from app.rag.multi_query import generate_search_queries
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_vectors
from app.rag.bm25_retriever import create_bm25_retriever
from app.rag.reranker import rerank_documents
from app.rag.fusion import reciprocal_rank_fusion


def multi_query_search(
    question: str,
    queries_count: int = 3,
    candidates_per_query: int = 10,
    final_limit: int = 5,
    source_types: list[str] | None = None,
    document_ids: list[str] | None = None,
):
    queries = generate_search_queries(
        question=question,
        number_of_queries=queries_count,
    )

    bm25_retriever = create_bm25_retriever(
        source_types=source_types,
        document_ids=document_ids,
    )

    ranked_lists = []

    for query in queries:
        # Dense retrieval
        query_embedding = generate_embedding(query)

        dense_results = search_vectors(
            query_embedding,
            limit=candidates_per_query,
            source_types=source_types,
            document_ids=document_ids,
        )

        # BM25 retrieval
        bm25_results = bm25_retriever.search(
            query,
            limit=candidates_per_query,
        )

        # Collect both ranked lists for RRF
        ranked_lists.append(
            (dense_results, "dense", query)
        )

        ranked_lists.append(
            (bm25_results, "bm25", query)
        )

    # Reciprocal Rank Fusion
    fused_results = reciprocal_rank_fusion(
        ranked_lists=ranked_lists,
    )
    print("\n===== FUSED RETRIEVAL CANDIDATES =====")

    for index, document in enumerate(fused_results, start=1):
        print(f"\nCandidate {index}")
        print("Source:", document.get("source"))
        print("Text:", document.get("text", "")[:500])

    # Cross-encoder reranking
    reranked_results = rerank_documents(
        query=question,
        documents=fused_results,
        limit=final_limit,
    )

    print("\n===== RERANKED DOCUMENTS =====")

    for index, document in enumerate(reranked_results, start=1):
        print(f"\nDocument {index}")
        print("Score:", document.get("rerank_score"))
        print("Text:", document.get("text", "")[:500])

    return {
        "queries": queries,
        "results": reranked_results,
    }
