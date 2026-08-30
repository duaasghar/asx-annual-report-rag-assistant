import re

def clean_page_text(text):
    # 1. Remove the footer + immediately preceding page number together, as one unit
    text = re.sub(r"\n?\s*\d{1,4}\s*\nASX Limited\s*\|\s*Financial report", "", text)
    
    # 2. Collapse multiple blank lines into a single one
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    # 3. Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def clean_all_pages(pages):
    cleaned = []
    for page in pages:
        cleaned_text = clean_page_text(page["text"])
        cleaned.append({
            "page_number": page["page_number"],
            "text": cleaned_text
        })
    return cleaned