import pymupdf 
from pathlib import Path

# This finds the project root regardless of where the script is run from
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # go up 2 folders from this script
PDF_PATH = PROJECT_ROOT / "asx-2025-annual-report.pdf"

def extract_text_by_page(pdf_path):
    doc = pymupdf.open(str(pdf_path))  
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({"page_number": page_num + 1, "text": text})
    doc.close()
    return pages

if __name__ == "__main__":
    pages = extract_text_by_page(PDF_PATH)
    print(pages[115]["text"])  # page 116, index 115