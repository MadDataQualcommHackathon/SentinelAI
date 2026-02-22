import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self, persist_directory="./cuad_chroma_db"):
        self.persist_directory = persist_directory
        # MUST match the embeddings used in build_cuad_kb.py
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        
        # Connect to the existing vector database
        if os.path.exists(self.persist_directory):
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            self._is_ready = True
            print("✅ Connected to local ChromaDB.")
        else:
            self.db = None
            self._is_ready = False
            print("❌ ChromaDB not found. Did you run build_cuad_kb.py?")

    def retrieve(self, query: str, n: int = 3):
        if not self._is_ready:
            return ["Error: Chroma DB not ready."]
        
        # Perform similarity search against the CUAD dataset
        results = self.db.similarity_search(query, k=n)
        
        # Format the retrieved context nicely, including the category metadata we saved earlier
        context_chunks = []
        for res in results:
            category = res.metadata.get("category", "Unknown Contract Type")
            context_chunks.append(f"[Reference Category: {category}]\n{res.page_content}")
            
        return context_chunks

    def is_ready(self):
        return self._is_ready