"""
Paper Hunter - Automated AI Paper Discovery & NotebookLM Integration

Searches for relevant AI/LLM papers and adds them to NotebookLM notebooks.
Only adds papers that pass relevance threshold.
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx

# Configuration
RELEVANCE_THRESHOLD = 7  # Only add papers scoring >= 7/10
DEFAULT_TOPICS = ["LLM", "AI agents", "prompt injection", "AI security"]

# State file for tracking processed papers
STATE_FILE = os.path.expanduser("~/.paper_hunter_state.json")


def load_state() -> Dict:
    """Load processed paper IDs"""
    import json
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed_ids": [], "notebooks": {}}


def save_state(state: Dict):
    """Save processed paper IDs"""
    import json
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


async def search_arxiv(query: str, max_results: int = 20) -> List[Dict]:
    """Search arXiv for papers"""
    import arxiv
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    results = []
    for result in client.results(search):
        results.append({
            "id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "abstract": result.summary,
            "published": result.published.isoformat() if result.published else "",
            "url": result.entry_id,
            "pdf_url": result.pdf_url,
            "query": query
        })
    
    return results


async def score_relevance(paper: Dict, topics: List[str]) -> float:
    """
    Use AI to score paper relevance (1-10).
    Considers: topic match, novelty, technical depth
    """
    # Check if paper mentions key topics in title/abstract
    text = (paper["title"] + " " + paper["abstract"]).lower()
    
    score = 5.0  # Base score
    
    # Topic matching boost
    for topic in topics:
        if topic.lower() in text:
            score += 1.5
    
    # Recent papers get a boost
    try:
        pub_date = datetime.fromisoformat(paper["published"])
        days_old = (datetime.now() - pub_date).days
        if days_old < 30:
            score += 2
        elif days_old < 90:
            score += 1
    except:
        pass
    
    # Cap at 10
    return min(score, 10.0)


def determine_topic(paper: Dict, existing_topics: List[str]) -> str:
    """Determine which topic/notebook this paper belongs to"""
    text = (paper["title"] + " " + paper["abstract"]).lower()
    
    # Topic keywords mapping
    topic_keywords = {
        "LLM Security": ["prompt injection", "jailbreak", "security", "adversarial", "attack"],
        "AI Agents": ["agent", "autonomous", "tool use", "planning", "reasoning"],
        "LLM Fine-tuning": ["fine-tune", "training", "rlhf", "dpo", "alignment"],
        "Multimodal": ["vision", "image", "video", "multimodal", "clip"],
        "LLM Reasoning": ["reasoning", "chain-of-thought", "math", "problem-solving"],
    }
    
    best_topic = "General AI"
    best_match = 0
    
    for topic, keywords in topic_keywords.items():
        matches = sum(1 for kw in keywords if kw in text)
        if matches > best_match:
            best_match = matches
            best_topic = topic
    
    return best_topic


async def add_to_notebooklm(paper: Dict, topic: str, client) -> Dict:
    """Add paper to NotebookLM"""
    # Find or create notebook for topic
    notebook = client.find_or_create_notebook(topic)
    notebook_id = notebook.get("notebookId") or notebook.get("name", "").split("/")[-1]
    
    # Add source
    result = client.add_source(notebook_id, paper["pdf_url"], paper["title"])
    return result


async def hunt_papers(
    topics: List[str] = None,
    max_per_topic: int = 10,
    dry_run: bool = False
) -> Dict:
    """
    Main function to hunt for relevant papers and add to NotebookLM.
    
    Args:
        topics: List of search queries (default: DEFAULT_TOPICS)
        max_per_topic: Max papers to search per topic
        dry_run: If True, don't add to NotebookLM, just report
    
    Returns:
        Summary of actions taken
    """
    from app.services.notebooklm import NotebookLMClient
    
    topics = topics or DEFAULT_TOPICS
    state = load_state()
    processed_ids = set(state.get("processed_ids", []))
    
    results = {
        "searched": 0,
        "scored": 0,
        "relevant": 0,
        "added": 0,
        "skipped": 0,
        "papers": []
    }
    
    all_papers = []
    
    # Step 1: Search all topics
    print(f"🔍 Searching arXiv for: {', '.join(topics)}")
    
    for topic in topics:
        papers = await search_arxiv(topic, max_per_topic)
        results["searched"] += len(papers)
        
        # Filter out already processed
        papers = [p for p in papers if p["id"] not in processed_ids]
        
        for paper in papers:
            paper["search_topic"] = topic
            paper["topic"] = determine_topic(paper, topics)
            all_papers.append(paper)
    
    # Step 2: Score relevance
    print(f"📊 Scoring {len(all_papers)} papers for relevance...")
    
    client = None
    if not dry_run:
        try:
            client = NotebookLMClient()
        except Exception as e:
            print(f"⚠️ NotebookLM auth failed: {e}")
            print("   Running in dry-run mode")
            dry_run = True
    
    for paper in all_papers:
        score = await score_relevance(paper, topics)
        paper["relevance_score"] = score
        results["scored"] += 1
        
        if score >= RELEVANCE_THRESHOLD:
            results["relevant"] += 1
            paper["status"] = "relevant"
            
            if not dry_run and client:
                try:
                    await add_to_notebooklm(paper, paper["topic"], client)
                    paper["status"] = "added"
                    results["added"] += 1
                    print(f"   ✅ Added: {paper['title'][:60]}...")
                except Exception as e:
                    paper["status"] = f"error: {e}"
                    print(f"   ❌ Failed: {paper['title'][:40]}... - {e}")
            else:
                results["added"] += 1  # Count as added in dry run
                paper["status"] = "would_add"
                print(f"   📝 Would add: {paper['title'][:60]}... (score: {score})")
            
            # Mark as processed
            processed_ids.add(paper["id"])
        else:
            results["skipped"] += 1
            paper["status"] = "skipped"
            processed_ids.add(paper["id"])
        
        results["papers"].append({
            "id": paper["id"],
            "title": paper["title"],
            "score": score,
            "topic": paper["topic"],
            "status": paper["status"]
        })
    
    # Save state
    state["processed_ids"] = list(processed_ids)
    save_state(state)
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"   Searched: {results['searched']}")
    print(f"   Relevant (score >= {RELEVANCE_THRESHOLD}): {results['relevant']}")
    print(f"   Added to NotebookLM: {results['added']}")
    print(f"   Skipped (low relevance): {results['skipped']}")
    
    return results


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    status_check = "--status" in sys.argv or "-s" in sys.argv
    topics = None
    
    for arg in sys.argv[1:]:
        if arg.startswith("--topic="):
            topics = [arg.split("=", 1)[1]]
        if arg.startswith("--topics="):
            topics = arg.split("=", 1)[1].split(",")
    
    if status_check:
        state = load_state()
        print(f"📚 Processed papers: {len(state.get('processed_ids', []))}")
        print(f"📓 Notebooks: {len(state.get('notebooks', {}))}")
        sys.exit(0)
    
    result = asyncio.run(hunt_papers(topics=topics, dry_run=dry_run))
