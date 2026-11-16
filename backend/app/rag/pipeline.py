
from app.rag.multi_query_retriever import multi_query_search
from app.rag.context_compressor import compress_context
from app.rag.qwen_client import generate_answer


def answer_question(
    question: str,
    retrieval_limit: int = 5,
    max_context_characters: int = 3000,
    source_types: list[str] | None = None,
    document_ids: list[str] | None = None,
):
    # Generate multiple search queries and retrieve
    # relevant documents from the selected sources.
    retrieval_result = multi_query_search(
        question=question,
        queries_count=3,
        candidates_per_query=10,
        final_limit=retrieval_limit,
        source_types=source_types,
        document_ids=document_ids,
    )

    retrieved_documents = retrieval_result["results"]
    generated_queries = retrieval_result["queries"]

    # Compress the retrieved context.
    compressed_documents = compress_context(
        documents=retrieved_documents,
        question=question,
        max_characters=max_context_characters,
    )

    context_parts = []

    for index, document in enumerate(
        compressed_documents,
        start=1,
    ):
        context_parts.append(
            f"[Source {index}]\n"
            f"Source: {document['source']}\n"
            f"Page Title: {document.get('page_title') or 'Not available'}\n"
            f"Content:\n{document['text']}"
        )

    context = "\n\n".join(context_parts)

    # Generate the answer using the original question.
    answer = generate_answer(
        question=question,
        context=context,
    )

    return {
        "answer": answer,
        "sources": compressed_documents,
        "generated_queries": generated_queries,
    }
