import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_pdf_to_queries(pdf_path: str) -> list[str]:
    """
    Extracts text from a PDF and splits it into an array of chunked strings.
    Each chunk will be used as a query against ChromaDB.
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    
    full_text = "\n\n".join(pages)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    query_chunks = text_splitter.split_text(full_text)
    
    return query_chunks

# if __name__ == "__main__":
#     test_file = r"c:\Users\hackathon user\Documents\LinkPlusCorp_20050802_8-K_EX-10_3240252_EX-10_Affiliate Agreement.pdf" 
#     try:
#         chunks = process_pdf_to_queries(test_file)
#         print(chunks)
#         print(f"Success! Created {len(chunks)} queries from the PDF.")
#         print(f"Sample Query 1:\n{chunks[0][:200]}...")
#     except FileNotFoundError:
#         print("Provide a valid PDF path to test.")