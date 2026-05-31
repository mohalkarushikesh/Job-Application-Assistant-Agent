"""
agent.py — LangChain Job Application AI Agent
Tools:
  1. resume_retriever  — searches your resume via RAG
  2. web_search        — fetches live company info
  3. generate_document — writes tailored resume / cover letter
  4. fit_scorer        — scores your fit for a JD (0–100)

Usage:
    from app.agent import build_agent
    agent = build_agent()
    result = agent.invoke({"input": "Analyse this JD: <paste JD here>"})
    print(result["output"])
"""

import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from app.rag import retrieve

# ── LLM ──────────────────────────────────────────────────────────────────────
# Swap "gpt-3.5-turbo" for "mistral" or any OpenAI-compatible model you prefer.
# For Groq (free): set OPENAI_API_BASE=https://api.groq.com/openai/v1 in .env
def get_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        temperature=0.4,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )


# ── TOOLS ─────────────────────────────────────────────────────────────────────

@tool
def resume_retriever(query: str) -> str:
    """
    Search Rushikesh's resume for relevant skills, projects, or experience.
    Use this before generating any document to ground the output in real facts.
    Input: a natural-language query, e.g. 'deep learning projects' or 'Python skills'.
    """
    context = retrieve(query)
    return f"Relevant resume content:\n{context}"


@tool
def web_search(company_name: str) -> str:
    """
    Search the web for information about a company.
    Use this to find the company's AI focus, recent news, products, and culture
    so the cover letter can reference specific details.
    Input: company name, e.g. 'Sarvam AI Bengaluru'.
    """
    search = DuckDuckGoSearchRun()
    results = search.run(f"{company_name} AI machine learning team products 2025")
    return results[:2000]   # trim to avoid context overflow


@tool
def generate_document(input_data: str) -> str:
    """
    Generate a tailored resume bullet or cover letter paragraph.
    Input format (plain text):
        type: cover_letter OR resume_bullets
        jd_summary: <2-3 sentence summary of the job>
        resume_context: <retrieved resume snippets>
        company_info: <web search results about the company>
    """
    llm = get_llm()
    prompt = f"""
You are an expert career coach. Using ONLY the information provided below,
write the requested document section. Be specific, metric-driven, and concise.

{input_data}

Rules:
- Never invent facts or metrics not present in the resume context.
- Highlight deep learning, NLP, computer vision, LLMs, and RAG where relevant.
- For cover letters: 3 paragraphs — hook, evidence, close. Max 250 words.
- For resume bullets: 3–5 bullets, each starting with a strong action verb.
"""
    response = llm.invoke(prompt)
    return response.content


@tool
def fit_scorer(input_data: str) -> str:
    """
    Score Rushikesh's fit for a job description from 0 to 100.
    Input format:
        jd: <full job description>
        resume_context: <retrieved resume snippets>
    Returns a score, a one-line verdict, and 3 gap areas to address.
    """
    llm = get_llm()
    prompt = f"""
You are a technical recruiter. Score the candidate's fit for the job below.

{input_data}

Respond in this exact format:
Score: <number>/100
Verdict: <one sentence>
Strengths: <2-3 bullet points>
Gaps to address: <2-3 bullet points>
"""
    response = llm.invoke(prompt)
    return response.content


# ── AGENT SYSTEM PROMPT ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert AI career assistant for Rushikesh Mohalkar,
an AI/ML Engineer in Bangalore specialising in deep learning, NLP, computer vision,
and generative AI (LangChain, RAG, LLMs).

Your job is to help Rushikesh apply for AI/ML roles by:
1. Analysing job descriptions he pastes
2. Searching his resume for relevant experience
3. Researching the target company online
4. Generating tailored cover letters and resume bullets
5. Scoring his fit and highlighting gaps

ALWAYS:
- Use resume_retriever before writing any document
- Use web_search to personalise cover letters with company-specific details
- Use fit_scorer when asked "am I a good fit?" or "analyse this JD"
- Be honest about gaps and suggest how to address them

Rushikesh's key strengths: PyTorch, TensorFlow, LangChain, RAG pipelines,
medical imaging (CNNs), RL (PPO), DistilBERT, FastAPI, Docker, AWS.
"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])


# ── BUILD AGENT ───────────────────────────────────────────────────────────────

def build_agent() -> AgentExecutor:
    """Construct and return the AgentExecutor. Call once at startup."""
    llm    = get_llm()
    tools  = [resume_retriever, web_search, generate_document, fit_scorer]
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=10    # remember last 10 turns
    )
    agent = create_openai_tools_agent(llm, tools, PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,           # set False in production
        max_iterations=6,
        handle_parsing_errors=True,
    )
