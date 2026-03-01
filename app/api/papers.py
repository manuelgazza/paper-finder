from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import arxiv_search, summarizer

router = APIRouter()


class PaperSearchRequest(BaseModel):
    query: str
    max_results: int = 10


class Paper(BaseModel):
    id: str
    title: str
    authors: List[str]
    abstract: str
    published: str
    url: str
    summary: Optional[str] = None


@router.get("/")
async def list_papers():
    """List all saved papers"""
    return {"papers": []}


@router.post("/search")
async def search_papers(request: PaperSearchRequest):
    """Search for papers on arXiv"""
    try:
        results = await arxiv_search.search(request.query, request.max_results)
        return {"papers": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{paper_id}")
async def get_paper(paper_id: str):
    """Get paper details"""
    return {"id": paper_id, "title": "Sample Paper", "abstract": "..."}


@router.post("/{paper_id}/summarize")
async def summarize_paper(paper_id: str):
    """Generate AI summary of a paper"""
    try:
        summary = await summarizer.summarize_paper(paper_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    """Delete a paper"""
    return {"status": "deleted", "id": paper_id}
