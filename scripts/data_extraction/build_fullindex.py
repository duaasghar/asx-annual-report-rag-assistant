from dotenv import load_dotenv
load_dotenv()

from extract_pdf import extract_text_by_page, PDF_PATH
from clean_text import clean_all_pages
from chunk_text import chunk_pages
from build_vectorstore import build_vectorstore

pages = extract_text_by_page(PDF_PATH)
cleaned_pages = clean_all_pages(pages)
chunks = chunk_pages(cleaned_pages)

print(f"Embedding {len(chunks)} chunks... this may take a minute or two.")
vectorstore = build_vectorstore(chunks, persist_directory="chroma_db")
print("Full vectorstore built and persisted!")

# Sanity check with a real financial question
results = vectorstore.similarity_search("What was the operating revenue in FY25?", k=3)
for r in results:
    print(f"\n--- Page {r.metadata['page_number']} ---")
    print(r.page_content[:200])