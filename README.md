# 🏛️ Legal AI Assistant for Indian Law

**AI-powered legal assistant** that helps judges, lawyers, and citizens understand Indian law, statutes, sections, and case histories.

> **Zero-cost** — runs entirely locally using Ollama for LLM inference. No API keys needed.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Ollama** — [Install from ollama.ai](https://ollama.ai)

### 1. Start Ollama & Pull a Model

```bash
ollama serve
ollama pull mistral
```

> Or use your existing model (e.g., `minimax-m2.5`). Update `OLLAMA_MODEL` in `.env`.

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Start the backend (auto-seeds legal database on first run)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:
- ✅ Create SQLite database
- ✅ Seed Constitution of India (key articles)
- ✅ Seed Bharatiya Nyaya Sanhita 2023
- ✅ Seed BNSS 2023 & BSA 2023
- ✅ Seed IPC (historical reference)
- ✅ Seed Motor Vehicles Act & Consumer Protection Act
- ✅ Seed 8 landmark Supreme Court cases
- ✅ Connect to Ollama for AI inference

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🏗️ Architecture

```
User Interface (Next.js + TailwindCSS)
        │
        ▼
FastAPI Backend (REST API)
        │
    ┌───┼───────────┐
    │   │           │
    ▼   ▼           ▼
Multi-Agent     ChromaDB      Knowledge
Orchestrator   Vector Store     Graph
    │               │          (NetworkX)
    ▼               │
Ollama LLM     Sentence
(Local)       Transformers
```

## 🤖 AI Agents

| Agent | Purpose |
|-------|---------|
| Legal Research | Statute lookup & summarization |
| Case Law | Similar case retrieval & analysis |
| Evidence | Upload document analysis via RAG |
| Argument Builder | Legal argument generation |
| Prediction | Case win probability estimation |

## 📁 Project Structure

```
legal_ai_assistant/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Settings
│   ├── database.py           # SQLAlchemy engine
│   ├── models/               # User, Case, Document models
│   ├── routers/              # API endpoints
│   │   ├── auth.py           # JWT authentication
│   │   ├── chat.py           # AI chat
│   │   ├── cases.py          # Case CRUD + analysis
│   │   ├── documents.py      # Upload & analyze
│   │   ├── search.py         # Multi-mode search
│   │   └── crawler.py        # Web crawler management
│   ├── ai/
│   │   ├── llm_client.py     # Ollama client
│   │   ├── embeddings.py     # Sentence Transformers
│   │   ├── rag_pipeline.py   # RAG pipeline
│   │   ├── prompts.py        # Prompt templates  
│   │   └── agents/           # Multi-agent system
│   ├── storage/
│   │   ├── vector_store.py   # ChromaDB
│   │   └── knowledge_graph.py # NetworkX graph
│   ├── crawler/              # Web scrapers
│   ├── ingestion/            # Parse → chunk → embed
│   └── data/                 # Seed laws & cases
├── frontend/                 # Next.js app
│   └── src/app/
│       ├── page.tsx          # Dashboard
│       ├── chat/             # AI chat interface
│       ├── cases/            # Case management
│       ├── search/           # Legal search
│       ├── documents/        # Document manager
│       └── crawler/          # Law updates
├── requirements.txt
├── .env
└── README.md
```

## ⚙️ Configuration

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_MODEL` | LLM model name | `deepseek` |
| `EMBEDDING_MODEL` | Sentence Transformers model | `all-MiniLM-L6-v2` |
| `DATABASE_URL` | SQLite connection string | `sqlite+aiosqlite:///./legal_ai.db` |

---

## 📜 License

This project is for educational purposes. Legal information provided by AI should not be considered as legal advice.
