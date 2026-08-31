from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from ragchain import build_rag_chain

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

chain, retriever = build_rag_chain(vectorstore)

test_questions = [
    "What was ASX's operating revenue in FY25?",
    "What was the total dividend per share for FY25?",
    "What was the statutory net profit after tax in FY25?",
    "What was the basic earnings per share in FY25?",
    "What was ASX's capital expenditure in FY25?",
    "What is the CEO's annual salary in Euros?",  # deliberately tricky/out-of-scope
    "What was ASX's revenue in FY30?",  # deliberately impossible - tests hallucination resistance
]

for q in test_questions:
    answer = chain.invoke(q)
    print(f"\nQ: {q}")
    print(f"A: {answer}")