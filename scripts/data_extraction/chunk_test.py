from extract_pdf import extract_text_by_page, PDF_PATH
from clean_text import clean_all_pages
from chunk_text import chunk_pages

pages = extract_text_by_page(PDF_PATH)
cleaned_pages = clean_all_pages(pages)
chunks = chunk_pages(cleaned_pages)

print(f"Total chunks created: {len(chunks)}")


print(f"\n--- Next chunk (index 51) ---")
print(chunks[51]["text"][:300])