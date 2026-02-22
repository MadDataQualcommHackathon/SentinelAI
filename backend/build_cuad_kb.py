from services.pdf_vector_store import PDFVectorStore

if __name__ == "__main__":
    # Path to where you extracted the Zenodo PDF folder
    PDF_DATA_PATH = "./CUAD_v1/full_contract_pdf"

    print("Starting CUAD PDF Ingestion...")
    kb = PDFVectorStore()
    kb.build_from_directory(PDF_DATA_PATH)
    print("CUAD PDF Knowledge Base stored in ChromaDB (localhost:8001)")
