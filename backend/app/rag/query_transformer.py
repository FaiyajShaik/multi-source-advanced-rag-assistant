from app.rag.qwen_client import chat_completion


def rewrite_query(question: str) -> str:
    system_prompt = (
        "You are a search query rewriting assistant. "
        "Rewrite user questions into concise search queries "
        "for retrieving relevant information from a knowledge base. "
        "Preserve the original meaning. "
        "Do not answer the question. "
        "Do not add information that is not present in the question. "
        "Return only the rewritten search query."
    )

    user_prompt = (
        f"User question:\n{question}"
    )

    rewritten_query = chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    return rewritten_query.strip()