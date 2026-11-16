from pathlib import Path

from sentence_transformers import SentenceTransformer


BACKEND_DIR = Path(__file__).resolve().parents[2]
MODEL_NAME = "intfloat/e5-base-v2"
MODEL_PATH = BACKEND_DIR / "models" / "embeddings"

model_source = str(MODEL_PATH) if MODEL_PATH.exists() else MODEL_NAME

model = SentenceTransformer(model_source)


def generate_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()
