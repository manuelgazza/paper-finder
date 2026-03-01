"""NotebookLM API service"""
import os
import httpx
from typing import List, Dict, Optional
from google.auth import default as google_default
from google.auth.transport.requests import Request as GoogleRequest


class NotebookLMClient:
    """Client for NotebookLM Enterprise API"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.base_url = "https://notebooklm.googleapis.com/v1"
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Get access token using Application Default Credentials"""
        try:
            import google.auth
            credentials, _ = google.default()
            auth_req = GoogleRequest()
            credentials.refresh(auth_req)
            self.token = credentials.token
        except Exception as e:
            print(f"Warning: Could not authenticate with GCP: {e}")
            self.token = os.getenv("GCP_ACCESS_TOKEN")
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def list_notebooks(self) -> List[Dict]:
        """List all notebooks in the project"""
        url = f"{self.base_url}/projects/{self.project_id}/notebooks"
        response = httpx.get(url, headers=self._headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("notebooks", [])
    
    def create_notebook(self, name: str, description: str = "") -> Dict:
        """Create a new notebook"""
        url = f"{self.base_url}/projects/{self.project_id}/notebooks"
        payload = {
            "notebook": {
                "display_name": name,
                "description": description
            }
        }
        response = httpx.post(url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_notebook(self, notebook_id: str) -> Dict:
        """Get notebook details"""
        url = f"{self.base_url}/projects/{self.project_id}/notebooks/{notebook_id}"
        response = httpx.get(url, headers=self._headers(), timeout=30)
        response.raise_for_status()
        return response.json()
    
    def add_source(self, notebook_id: str, source_url: str, title: str = None) -> Dict:
        """Add a URL source to a notebook"""
        url = f"{self.base_url}/projects/{self.project_id}/notebooks/{notebook_id}/sources"
        payload = {
            "source": {
                "uri": source_url,
                "title": title
            }
        }
        response = httpx.post(url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def add_pdf(self, notebook_id: str, pdf_content: bytes, title: str) -> Dict:
        """Add a PDF source to a notebook"""
        import base64
        
        url = f"{self.base_url}/projects/{self.project_id}/notebooks/{notebook_id}/sources:upload"
        
        # Create multipart request
        files = {
            "file": (f"{title}.pdf", pdf_content, "application/pdf")
        }
        metadata = {
            "source": {"title": title}
        }
        
        # For now, we'll use URL sources as PDF upload is more complex
        # This would need proper OAuth2 flow
        raise NotImplementedError("PDF upload requires OAuth2. Use URL sources for now.")
    
    def find_or_create_notebook(self, topic: str) -> Dict:
        """
        Find an existing notebook for a topic or create a new one.
        Topic matching is done by checking display name.
        """
        notebooks = self.list_notebooks()
        
        # Look for matching notebook
        topic_lower = topic.lower()
        for nb in notebooks:
            if topic_lower in nb.get("displayName", "").lower():
                return nb
        
        # Create new notebook if not found
        return self.create_notebook(
            name=f"AI Papers: {topic}",
            description=f"Auto-generated notebook for {topic} papers"
        )
    
    def add_paper_to_notebook(self, paper: Dict, notebook_id: str = None, topic: str = "LLM") -> Dict:
        """
        Add a paper to a notebook. If notebook_id provided, use it.
        Otherwise find or create notebook for the topic.
        """
        if notebook_id is None:
            notebook = self.find_or_create_notebook(topic)
            notebook_id = notebook.get("notebookId") or notebook.get("name", "").split("/")[-1]
        
        # Use arXiv PDF URL or the paper URL
        source_url = paper.get("pdf_url") or paper.get("url")
        title = paper.get("title", "Untitled")
        
        return self.add_source(notebook_id, source_url, title)


# Convenience functions
async def add_paper_to_notebook(paper: Dict, topic: str = "LLM", notebook_id: str = None) -> Dict:
    """Add a paper to NotebookLM"""
    client = NotebookLMClient()
    return client.add_paper_to_notebook(paper, notebook_id, topic)


async def create_topic_notebook(topic: str, description: str = "") -> Dict:
    """Create a notebook for a specific topic"""
    client = NotebookLMClient()
    return client.create_notebook(topic, description)
