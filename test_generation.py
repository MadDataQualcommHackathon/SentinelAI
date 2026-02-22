from backend.services.pdf_processor import process_pdf_to_queries
from backend.services.chroma_query import ChromaQueryService
from backend.orchestrator import run_analysis

DB_PATH = r"C:\Users\hackathon user\Documents\SentinelAI\cuad_chroma_db"
PDF_PATH = r"c:\Users\hackathon user\Documents\LinkPlusCorp_20050802_8-K_EX-10_3240252_EX-10_Affiliate Agreement.pdf"

# 1. Confirm PDF chunking still works
chunks = process_pdf_to_queries(PDF_PATH)
print(f"PDF split into {len(chunks)} chunks.")
print(f"Sample chunk:\n{chunks[0][:200]}...\n")

# 2. Confirm ChromaDB retrieval still works
db_service = ChromaQueryService(DB_PATH)
top_3 = db_service.get_top_3_matches(chunks[0])
print(f"Top 3 ChromaDB references for first chunk:")
for i, ref in enumerate(top_3):
    print(f"\nRef {i+1}:\n{ref[:200]}...")

# 3. Run full generation pipeline
print("\n--- Running full analysis (legal_risk_scoring) ---")
result = run_analysis(PDF_PATH, "legal_risk_scoring")
print(f"Score: {result.get('score')}")
print(f"Findings ({len(result.get('findings', []))}):")
for f in result.get("findings", []):
    print(f"  [{f.get('risk_level')}] {f.get('clause_type')}: {f.get('excerpt', '')[:80]}...")
