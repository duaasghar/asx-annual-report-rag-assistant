import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def build_vectorstore(chunks, persist_directory="chroma_db", batch_size=90, delay_seconds=65):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={"page_number": chunk["page_number"]}
        )
        for chunk in chunks
    ]
    
    vectorstore = None
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        print(f"Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=persist_directory
            )
        else:
            vectorstore.add_documents(batch)
        
        # Wait before the next batch, unless this was the last one
        if i + batch_size < len(documents):
            print(f"Waiting {delay_seconds}s to respect rate limit...")
            time.sleep(delay_seconds)
    
    return vectorstore