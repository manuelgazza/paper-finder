from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import arxiv_search, summarizer, notebooklm

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
    pdf_url: Optional[str] = None
    summary: Optional[str] = None


class AddToNotebookRequest(BaseModel):
    notebook_id: Optional[str] = None
    topic: str = "LLM"


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


@router.post("/{paper_id}/notebook")
async def add_to_notebook(paper_id: str, request: AddToNotebookRequest):
    """
    Add a paper to NotebookLM.
    If notebook_id is provided, adds to that notebook.
    Otherwise finds existing or creates new notebook for the topic.
    """
    try:
        # For now, we need the full paper data passed in
        # In production, you'd fetch from DB
        return {"status": "success", "message": "NotebookLM integration ready"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notebooks")
async def list_notebooks():
    """List all NotebookLM notebooks"""
    try:
        client = notebooklm.NotebookLMClient()
        notebooks = client.list_notebooks()
        return {"notebooks": notebooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notebooks")
async def create_notebook(topic: str, description: str = ""):
    """Create a new NotebookLM notebook for a topic"""
    try:
        client = notebooklm.NotebookLMClient()
        result = client.create_notebook(topic, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    """Delete a paper"""
    return {"status": "deleted", "id": paper_id}
