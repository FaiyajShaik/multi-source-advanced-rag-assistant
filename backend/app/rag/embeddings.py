from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/e5-base-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()