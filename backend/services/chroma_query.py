import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class ChromaQueryService:
    def __init__(self, persist_directory="./cuad_chroma_db"):
        self.persist_directory = persist_directory
        # Must perfectly match the model used in build_cuad_kb.py
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Connect to your existing local database
        if os.path.exists(self.persist_directory):
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.db = None
            print(f"❌ Error: ChromaDB not found at {self.persist_directory}")

    def get_top_3_matches(self, query_text: str) -> list[str]:
        """
        Takes a string query, searches the DB, and returns an array 
        of 3 strings representing the most similar context.
        """
        if not self.db:
            return ["Error: Database not loaded."]
            
        # Perform the vector search (k=3 means top 3 matches)
        results = self.db.similarity_search(query_text, k=3)
        
        # Format the output into a simple array of 3 strings
        matched_strings = []
        for res in results:
            # We pull the category metadata you saved during ingestion!
            category = res.metadata.get("category", "General")
            content = res.page_content.strip()
            
            # Combine them into one clean string
            formatted_match = f"[Reference Category: {category}]\n{content}"
            matched_strings.append(formatted_match)
            
        return matched_strings

# # --- Quick Test ---
# if __name__ == "__main__":
#     # You can run this file directly to test the database connection
#     query_service = ChromaQueryService(r"C:\Users\hackathon user\Documents\SentinelAI\cuad_chroma_db") # Adjust path if needed
    
#     test_query = "The employee shall not engage in any competing business for a period of 12 months."
#     matches = query_service.get_top_3_matches(test_query)
    
#     print("--- Top 3 Matches ---")
#     for i, match in enumerate(matches):
#         print(f"\nMatch {i+1}:\n{match}")