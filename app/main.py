"""
Paper Finder - AI-powered paper discovery and summarization
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    
    class Config:
        env_file = ".env"


settings = Settings()
app = FastAPI(title="Paper Finder", description="AI-powered paper discovery and summarization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Paper Finder API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Import and include routers
from app.api import papers

app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
