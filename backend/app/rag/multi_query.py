
from app.rag.qwen_client import chat_completion


def generate_search_queries(
    question: str,
    number_of_queries: int = 3,
) -> list[str]:
    original_question = question.strip()

    if not original_question:
        return []

    system_prompt = (
        "You generate alternative search queries for a document "
        "retrieval system. Given a user's question, produce concise "
        "search queries that preserve the user's intent. "
        "Do not answer the question. "
        "Return only the queries, one per line."
    )

    user_prompt = (
        f"Create {number_of_queries - 1} alternative search queries "
        f"for this question:\n\n"
        f"{original_question}"
    )

    queries = [original_question]

    if number_of_queries <= 1:
        return queries

    try:
        response = chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        generated_queries = [
            line.strip().lstrip("-•0123456789. ")
            for line in response.splitlines()
            if line.strip()
        ]

        for query in generated_queries:
            if (
                query
                and query.lower() not in {
                    existing.lower()
                    for existing in queries
                }
            ):
                queries.append(query)

            if len(queries) >= number_of_queries:
                break

    except Exception:
        # Preserve basic retrieval if query generation fails.
        pass

    return queries[:number_of_queries]
