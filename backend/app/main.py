
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes.health import router as health_router
from app.api.routes.query import router as query_router
from app.api.routes.document import router as documents_router
from app.api.routes.website import router as website_router


# Load environment variables from backend/.env
BACKEND_ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../.env")
)
load_dotenv(BACKEND_ENV_PATH)


app = FastAPI()


# Local development origins
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


# Add production frontend URLs from environment variables.
# Multiple URLs can be separated by commas.
frontend_urls = os.getenv("FRONTEND_URL", "")

if frontend_urls:
    production_origins = [
        url.strip().rstrip("/")
        for url in frontend_urls.split(",")
        if url.strip()
    ]

    allowed_origins.extend(production_origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(health_router)
app.include_router(query_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(website_router, prefix="/api/v1")
