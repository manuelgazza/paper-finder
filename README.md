# Paper Finder 🎓

AI-powered paper discovery and summarization tool inspired by NotebookLM.

## Features

- Search papers on arXiv, Semantic Scholar, and other sources
- AI-powered summarization using LLMs
- Notebook-style organization with tags and collections
- Export summaries as markdown, PDF, or audio
- Citation management

## Tech Stack

- **Backend**: Python/FastAPI
- **Frontend**: React + TypeScript
- **Database**: SQLite (local) or PostgreSQL (production)
- **AI**: OpenAI GPT-4 / Anthropic Claude / Ollama

## Quick Start

```bash
# Clone the repo
git clone https://github.com/manuelgazza/paper-finder.git
cd paper-finder

# Set up Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here

# Run the app
uvicorn app.main:app --reload
```

## Architecture

```
paper-finder/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core business logic
│   ├── models/       # Data models
│   └── services/     # External integrations
├── frontend/        # React app
├── tests/           # Test suite
└── docs/            # Documentation
```

## API Endpoints

- `GET /api/papers` - List all papers
- `POST /api/papers/search` - Search for papers
- `GET /api/papers/{id}` - Get paper details
- `POST /api/papers/{id}/summarize` - Generate summary
- `DELETE /api/papers/{id}` - Delete paper

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OLLAMA_BASE_URL` | Ollama base URL |
| `DATABASE_URL` | Database connection string |

## License

MIT
