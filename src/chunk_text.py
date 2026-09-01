from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_pages(cleaned_pages, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # tries these in order to find natural breaks
    )
    
    all_chunks = []
    for page in cleaned_pages:
        page_chunks = splitter.split_text(page["text"])
        for chunk_text in page_chunks:
            all_chunks.append({
                "text": chunk_text,
                "page_number": page["page_number"]
            })
    return all_chunks