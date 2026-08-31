from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def build_vectorstore(chunks, persist_directory="chroma_db"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={"page_number": chunk["page_number"]}
        )
        for chunk in chunks
    ]
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return vectorstore