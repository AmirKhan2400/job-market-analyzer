from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_market_analyzer.api.routes import router
from job_market_analyzer.config import settings


def _cors_origins() -> list[str]:
    return [
        origin.strip()
        for origin in settings.backend_cors_origins.split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="AI Job Market Analyzer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
