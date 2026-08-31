from dotenv import load_dotenv
load_dotenv()

from extract_pdf import extract_text_by_page, PDF_PATH
from clean_text import clean_all_pages
from chunk_text import chunk_pages
from build_vectorstore import build_vectorstore

pages = extract_text_by_page(PDF_PATH)
cleaned_pages = clean_all_pages(pages)
chunks = chunk_pages(cleaned_pages)

test_vectorstore = build_vectorstore(chunks[:5], persist_directory="chroma_db_test")
print("Test vectorstore built successfully!")

results = test_vectorstore.similarity_search("annual report highlights", k=2)
for r in results:
    print(f"\nPage {r.metadata['page_number']}: {r.page_content[:150]}")