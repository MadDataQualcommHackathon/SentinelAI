from langchain_text_splitters import RecursiveCharacterTextSplitter
from .pdf_parser import extract_text_corpus

class IngestionService:
    def __init__(self):
        # We use the same chunk size as our KB to ensure the LLM gets consistent data sizes
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def process(self, file_path: str):
        print(f"📄 Parsing and chunking uploaded file: {file_path}")
        
        # 1. Parse the full text from the uploaded PDF using your existing parser
        full_text = extract_text_corpus(file_path)
        
        # 2. Chunk the text
        docs = self.text_splitter.create_documents([full_text])
        
        # 3. Format as a list of dictionaries exactly how your main.py expects it
        chunks = []
        for i, doc in enumerate(docs):
            chunks.append({
                "chunk_id": f"chunk_{i}",
                "text": doc.page_content,
                "file_type": "legal", 
                "index": i
            })
            
        print(f"✂️ Extracted {len(chunks)} chunks to analyze.")
        return chunks