from backend.services.pdf_processor import process_pdf_to_queries
from backend.services.chroma_query import ChromaQueryService

# 1. Initialize the DB
db_service = ChromaQueryService(r"C:\Users\hackathon user\Documents\SentinelAI\cuad_chroma_db")

# 2. Get an array of strings from the user's PDF
queries = process_pdf_to_queries(r"c:\Users\hackathon user\Documents\LinkPlusCorp_20050802_8-K_EX-10_3240252_EX-10_Affiliate Agreement.pdf") # Adjust path if needed

# 3. For every chunk in the PDF, get the 3 reference strings!
# for query in queries:
#     top_3_references = db_service.get_top_3_matches(query)
    
#     # --> This is where you will eventually merge 'query' and 'top_3_references'
#     # --> and send them to the AnythingLLM API!

top_3_references = db_service.get_top_3_matches(queries[0]) # Just testing the first chunk for now

print(len(top_3_references))