from app.rag.embeddings import generate_embedding
from app.rag.vector_store import search_vectors
from app.rag.bm25_retriever import create_bm25_retriever
from app.rag.reranker import rerank_documents
from app.rag.fusion import reciprocal_rank_fusion


def hybrid_search(
    query: str,
    limit: int = 3,
):
    query_embedding = generate_embedding(query)

    # Dense retrieval
    dense_results = search_vectors(
        query_embedding,
        limit=limit,
    )

    # BM25 retrieval
    bm25_retriever = create_bm25_retriever()

    bm25_results = bm25_retriever.search(
        query,
        limit=limit,
    )

    # Combine both ranked lists using RRF
    fused_results = reciprocal_rank_fusion(
        ranked_lists=[
            (dense_results, "dense", query),
            (bm25_results, "bm25", query),
        ]
    )

    # Rerank the fused candidates
    reranked_results = rerank_documents(
        query=query,
        documents=fused_results,
        limit=limit,
    )

    return reranked_results