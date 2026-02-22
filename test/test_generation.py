from ..backend.services.pdf_processor import process_pdf_to_queries
from ..backend.services.chroma_query import ChromaQueryService
from ..backend.orchestrator import run_analysis

DB_PATH = r"C:\Users\hackathon user\Documents\SentinelAI\cuad_chroma_db"
PDF_PATH = r"c:\Users\hackathon user\Documents\LinkPlusCorp_20050802_8-K_EX-10_3240252_EX-10_Affiliate Agreement.pdf"
# PDF_PATH = r"C:\Users\hackathon user\Documents\SentinelAI\CUAD_v1\full_contract_pdf\Part_III\Maintenance\SECURIANFUNDSTRUST_05_01_2012-EX-99.28.H.9-NET INVESTMENT INCOME MAINTENANCE AGREEMENT.PDF"

# # 1. Confirm PDF chunking still works
# chunks = process_pdf_to_queries(PDF_PATH)
# print(f"PDF split into {len(chunks)} chunks.")
# print(f"Sample chunk:\n{chunks[0][:200]}...\n")

# # 2. Confirm ChromaDB retrieval still works
# db_service = ChromaQueryService(DB_PATH)
# top_3 = db_service.get_top_3_matches(chunks[0])
# print(f"Top 3 ChromaDB references for first chunk:")
# for i, ref in enumerate(top_3):
#     print(f"\nRef {i+1}:\n{ref[:200]}...")

# 3. Run full generation pipeline
print("\n--- Running full analysis (legal_risk_scoring) ---")
result = run_analysis(PDF_PATH, "legal_risk_scoring")
print(f"Score: {result.get('score')}")
print(f"Findings ({len(result.get('findings', []))}):")
for f in result.get("findings", []):
     print(f"  [{f.get('risk_level')}] {f.get('clause_type')}: {f.get('excerpt', '')[:80]}...")

# print("\n--- Running full analysis (pii_masking) ---")
# result = run_analysis(PDF_PATH, "pii_masking")
# print(f"PII instances found: {len(result.get('pii_instances', []))}")
# for p in result.get("pii_instances", []):
#      print(f"  [{p.get('pii_type')}] {p.get('excerpt', '')[:80]}...")
#      print(f"    Recommendation: {p.get('recommendation', '')}")


# print("\n--- Running full analysis (vulnerability_detection) ---")
# result = run_analysis(PDF_PATH, "vulnerability_detection")
# print(f"Findings ({len(result.get('findings', []))}):")
# for f in result.get("findings", []):
#      print(f"  [{f.get('severity')}] {f.get('vulnerability_type')}:{f.get('excerpt', '')[:80]}...")
#      print(f"    Recommendation: {f.get('recommendation', '')}")