"""
main.py — FastAPI Backend
Endpoints:
  POST /chat          — conversational agent (main endpoint)
  POST /analyse       — score fit for a JD
  POST /generate      — generate cover letter or resume bullets
  GET  /health        — liveness check
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import build_agent
from app.rag import build_vectorstore

# ── Startup: build vectorstore + agent once ───────────────────────────────────
agent_executor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_executor
    print("[Startup] Building vectorstore...")
    build_vectorstore()
    print("[Startup] Building agent...")
    agent_executor = build_agent()
    print("[Startup] Ready!")
    yield

app = FastAPI(
    title="Job Application AI Agent",
    description="AI agent that tailors applications for Rushikesh Mohalkar",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class AnalyseRequest(BaseModel):
    job_description: str
    company_name: str = ""

class GenerateRequest(BaseModel):
    job_description: str
    company_name: str = ""
    doc_type: str = "cover_letter"   # or "resume_bullets"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Main conversational endpoint. Paste any message — JD, question, request."""
    try:
        result = agent_executor.invoke({"input": req.message})
        return ChatResponse(response=result["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse", response_model=ChatResponse)
def analyse(req: AnalyseRequest):
    """Score fit for a job description and list strengths / gaps."""
    message = (
        f"Analyse this JD and score my fit. Company: {req.company_name}\n\n"
        f"JD:\n{req.job_description}"
    )
    try:
        result = agent_executor.invoke({"input": message})
        return ChatResponse(response=result["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=ChatResponse)
def generate(req: GenerateRequest):
    """Generate a tailored cover letter or resume bullets."""
    message = (
        f"Generate a {req.doc_type} for this role at {req.company_name}.\n\n"
        f"JD:\n{req.job_description}"
    )
    try:
        result = agent_executor.invoke({"input": message})
        return ChatResponse(response=result["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
