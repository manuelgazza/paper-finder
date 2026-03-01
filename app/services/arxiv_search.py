"""ArXiv search service"""
import arxiv
from typing import List, Dict


async def search(query: str, max_results: int = 10) -> List[Dict]:
    """Search arXiv for papers"""
    client = arxiv.Client()
    
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for result in client.results(search):
        results.append({
            "id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "published": result.published.isoformat() if result.published else "",
            "url": result.entry_id,
            "pdf_url": result.pdf_url
        })
    
    return results
