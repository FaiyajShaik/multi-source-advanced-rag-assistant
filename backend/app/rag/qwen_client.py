import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set in the environment."
    )

if not OPENROUTER_MODEL:
    raise ValueError(
        "OPENROUTER_MODEL is not set in the environment."
    )


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def chat_completion(
    system_prompt: str,
    user_prompt: str,
) -> str:
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content


def generate_answer(
    question: str,
    context: str,
) -> str:
    system_prompt = (
        "You are a helpful question-answering assistant. "
        "Answer the user's question using only the provided context. "
        "If the answer is not present in the context, say "
        "that you do not have enough information."
    )

    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    return chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )