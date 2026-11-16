from pathlib import Path

from huggingface_hub import snapshot_download


BACKEND_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BACKEND_DIR / "models"

MODELS = {
    "embeddings": "intfloat/e5-base-v2",
    "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2",
}

ALLOWED_FILES = [
    "*.json",
    "*.safetensors",
    "*.txt",
]

for model_folder, repo_id in MODELS.items():
    destination = MODELS_DIR / model_folder

    print(f"\nDownloading {repo_id}")
    print(f"Destination: {destination}")

    snapshot_download(
        repo_id=repo_id,
        local_dir=str(destination),
        allow_patterns=ALLOWED_FILES,
    )

    print(f"Completed: {repo_id}")

print("\nAll required models downloaded successfully.")
