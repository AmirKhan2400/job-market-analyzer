from fastapi import FastAPI

from job_market_analyzer.api.routes import router

app = FastAPI(
    title="AI Job Market Analyzer",
    version="0.1.0",
)

app.include_router(router)
