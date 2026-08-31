from extract_pdf import extract_text_by_page, PDF_PATH
from clean_text import clean_all_pages

pages = extract_text_by_page(PDF_PATH)
cleaned_pages = clean_all_pages(pages)

print("--- Page 116, last 300 chars ---")
print(cleaned_pages[115]["text"][-300:])