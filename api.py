import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.rag_chain import build_rag_chain

logger = logging.getLogger("uvicorn.error")

MAX_QUESTION_LENGTH = 500

# Comma-separated list, e.g. "https://my-app.vercel.app,http://localhost:3000"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="ASX Annual Report RAG API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Load the vector store and chain ONCE at startup, not per-request
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
CHUNK_COUNT = len(vectorstore.get(include=[])["ids"])
if CHUNK_COUNT == 0:
    logger.warning("Vector store is empty: run build_index.py and commit chroma_db/")
chain, retriever = build_rag_chain(vectorstore)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class Source(BaseModel):
    page: int | None
    excerpt: str


class Answer(BaseModel):
    question: str
    answer: str
    sources: list[Source]


@app.post("/ask", response_model=Answer)
@limiter.limit("10/minute")  # per client IP
@limiter.shared_limit("60/minute", scope="ask_global", key_func=lambda: "global")  # protects Gemini quota
def ask(request: Request, payload: Question) -> Answer:
    question = payload.question.strip()

    try:
        answer = chain.invoke(question)
        # Also get the raw retrieved chunks, for source citations
        retrieved_docs = retriever.invoke(question)
    except Exception:
        logger.exception("Gemini call failed for /ask")
        raise HTTPException(
            status_code=503,
            detail="The AI model is busy right now. Please try again in a minute.",
        )

    sources = [
        Source(page=doc.metadata.get("page_number"), excerpt=doc.page_content[:200])
        for doc in retrieved_docs
    ]

    return Answer(question=question, answer=answer, sources=sources)


@app.get("/")
def root():
    return {"status": "ok", "message": "ASX RAG API is running"}


@app.get("/health")
def health():
    return {"status": "ok" if CHUNK_COUNT > 0 else "degraded", "chunks": CHUNK_COUNT}
