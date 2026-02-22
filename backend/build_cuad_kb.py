from services.pdf_vector_store import PDFVectorStore

if __name__ == "__main__":
    PDF_DATA_PATH = r"C:\Users\hackathon user\Documents\SentinelAI\CUAD_v1\full_contract_pdf"
    
    print("Starting CUAD PDF Ingestion...")
    kb = PDFVectorStore(persist_directory="./cuad_chroma_db")
    kb.build_from_directory(PDF_DATA_PATH)
    print("CUAD PDF Knowledge Base Created in ./cuad_chroma_db")