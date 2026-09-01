from dotenv import load_dotenv
load_dotenv()

from src.extract_pdf import extract_text_by_page, PDF_PATH
from src.clean_text import clean_all_pages
from src.chunk_text import chunk_pages
from src.build_vectorstore import build_vectorstore
import os

if os.path.exists("chroma_db") and os.listdir("chroma_db"):
    response = input("chroma_db already exists and has data. Rebuild anyway? This will use API quota. (y/n): ")
    if response.lower() != "y":
        print("Aborted. Delete chroma_db manually first if you want to rebuild.")
        exit()
        
pages = extract_text_by_page(PDF_PATH)
cleaned_pages = clean_all_pages(pages)
chunks = chunk_pages(cleaned_pages)

print(f"Embedding {len(chunks)} chunks...")
vectorstore = build_vectorstore(chunks, persist_directory="chroma_db")
print("Vectorstore built and persisted!") 


# Sanity check with a real financial question
results = vectorstore.similarity_search("What was the operating revenue in FY25?", k=3)
for r in results:
    print(f"\n--- Page {r.metadata['page_number']} ---")
    print(r.page_content[:200])