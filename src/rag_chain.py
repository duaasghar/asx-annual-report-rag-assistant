from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

PROMPT_TEMPLATE = """You are a financial document assistant. Answer the question using ONLY the context provided below, which is extracted from ASX Limited's FY2025 Annual Report.

Rules:
- If the answer is not contained in the context, say "I don't have enough information in the provided report to answer that" — do not guess or use outside knowledge.
- When you state a number, mention which page it came from if that information is available in the context.
- Be precise and concise.

Context:
{context}

Question: {question}

Answer:"""

def format_docs(docs):
    formatted = []
    for doc in docs:
        page = doc.metadata.get("page_number", "unknown")
        formatted.append(f"[Page {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)

def build_rag_chain(vectorstore, k=5):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    # Fail fast when Gemini is overloaded or out of quota, then fall back to a
    # lighter model with its own quota. Worst case stays inside the frontend
    # proxy's 55s window (20s primary + 20s fallback).
    primary = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, timeout=20, max_retries=0)
    fallback = ChatGoogleGenerativeAI(model=FALLBACK_MODEL, timeout=20, max_retries=0)
    llm = primary.with_fallbacks([fallback])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever