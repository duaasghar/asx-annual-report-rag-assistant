from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.build_vectorstore import build_vectorstore
from src.rag_chain import build_rag_chain, format_docs, PROMPT_TEMPLATE

app = FastAPI(title="ASX Annual Report RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load the vector store and chain ONCE at startup, not per-request
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
chain, retriever = build_rag_chain(vectorstore)


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(payload: Question):
    question = payload.question

    # Get answer from the chain
    answer = chain.invoke(question)

    # Also get the raw retrieved chunks, for source citations
    retrieved_docs = retriever.invoke(question)
    sources = [
        {"page": doc.metadata.get("page_number"), "excerpt": doc.page_content[:200]}
        for doc in retrieved_docs
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


@app.get("/")
def health_check():
    return {"status": "ok", "message": "ASX RAG API is running"}