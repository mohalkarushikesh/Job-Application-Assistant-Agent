"""
rag.py — Resume RAG Pipeline
Loads your resume PDF, chunks it, embeds it, stores in FAISS.
Call build_vectorstore() once at startup, then retrieve() at query time.
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

RESUME_PATH = "data/resume.pdf"
EMBED_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"   # free, runs locally

_vectorstore = None   # module-level cache


def build_vectorstore(resume_path: str = RESUME_PATH) -> FAISS:
    """Ingest the resume PDF and return a FAISS vectorstore."""
    global _vectorstore

    # 1. Load PDF pages
    loader = PyPDFLoader(resume_path)
    pages  = loader.load()

    # 2. Split into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(pages)

    # 3. Embed with a local HuggingFace model (no API key needed)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    # 4. Build & cache FAISS index
    _vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"[RAG] Indexed {len(chunks)} chunks from {resume_path}")
    return _vectorstore


def get_vectorstore() -> FAISS:
    """Return cached vectorstore, building it if needed."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = build_vectorstore()
    return _vectorstore


def retrieve(query: str, k: int = 4) -> str:
    """
    Retrieve the top-k resume chunks most relevant to a query.
    Returns a single joined string ready to inject into a prompt.
    """
    vs   = get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    return "\n\n".join(d.page_content for d in docs)
