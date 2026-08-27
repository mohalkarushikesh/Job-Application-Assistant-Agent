# 🤖 Job Application AI Agent

An end-to-end Agentic AI system that analyses job descriptions, retrieves relevant experience from a resume using RAG (Retrieval Augmentation Generation), researches target companies, and generates tailored cover letters, resume bullets, and fit scores — all powered by LangChain, FAISS, and an LLM.

---

## 🏗️ Architecture

```
User Input (JD)
      │
      ▼
LangChain Agent Orchestrator
  ├── resume_retriever  → FAISS Vector Store (resume chunks)
  ├── web_search        → DuckDuckGo (company info)
  ├── generate_document → LLM (cover letter / resume bullets)
  └── fit_scorer        → LLM (0–100 fit score + gap analysis)
      │
      ▼
FastAPI Backend  ←→  Streamlit UI
      │
   Docker
```

---

## ✨ Features

- **RAG-powered resume retrieval** — FAISS + sentence-transformers (runs fully locally, no embedding API cost)
- **Live company research** — DuckDuckGo web search to personalise cover letters
- **Tailored document generation** — cover letters and resume bullets grounded in your actual experience
- **Fit scoring** — instant 0–100 score with strengths and gap analysis
- **Conversation memory** — remembers context across 10 turns
- **REST API** — `/chat`, `/analyse`, `/generate` endpoints
- **Streamlit UI** — clean interface with one-click download

---

## 🚀 Quick Start

### 1. Clone & setup

```bash
git clone https://github.com/mohalkarushikesh/job-agent.git
cd job-agent
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (or Groq key — it's free!)
```

### 2. Add your resume

```bash
cp /path/to/your/resume.pdf data/resume.pdf
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 5. Run the UI (new terminal)

```bash
streamlit run ui/app.py
# UI available at http://localhost:8501
```

### 6. Or use Docker

```bash
docker build -t job-agent .
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data job-agent
```

---

## 💡 Free LLM Alternative (Groq)

Don't want to pay for OpenAI? Use Groq — it's free and fast:

1. Sign up at https://console.groq.com
2. Get your API key
3. Update `.env`:

```
OPENAI_API_KEY=gsk_your-groq-key
OPENAI_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama3-8b-8192
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| POST | `/chat` | Conversational agent |
| POST | `/analyse` | Fit score + gap analysis |
| POST | `/generate` | Cover letter or resume bullets |

### Example — Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyse this JD: We need an ML engineer with NLP and RAG experience..."}'
```

### Example — Generate Cover Letter

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for an ML engineer...",
    "company_name": "Sarvam AI",
    "doc_type": "cover_letter"
  }'
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Framework | LangChain |
| LLM | GPT-3.5-turbo / Llama3 (Groq) |
| Embeddings | sentence-transformers (local) |
| Vector Store | FAISS |
| Web Search | DuckDuckGo |
| API | FastAPI |
| UI | Streamlit |
| Containerisation | Docker |

---

## 📁 Project Structure

```
job-agent/
├── app/
│   ├── main.py        # FastAPI entry point
│   ├── agent.py       # LangChain agent + tools
│   └── rag.py         # RAG pipeline
├── ui/
│   └── app.py         # Streamlit frontend
├── data/
│   └── resume.pdf     # Your resume (not committed)
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🗺️ Roadmap

- [ ] Multi-resume support (upload via UI)
- [ ] Email integration (send applications directly)
- [ ] Application tracker dashboard
- [ ] LinkedIn JD scraper
- [ ] Interview prep Q&A mode

---

🔗 [GitHub](https://github.com/mohalkarushikesh) | [LinkedIn](https://linkedin.com/in/rushikesh-mohalkar)
