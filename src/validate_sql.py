import sys
import os
sys.path.insert(0, os.path.abspath("."))
import re
from src.database import run_query

def test_all_queries():
    with open("database/analysis_queries.sql", "r", encoding="utf-8") as f:
        content = f.read()

    # Split queries by semicolon followed by comment or end of string
    raw_queries = content.split(";\n")
    valid_queries = []
    
    for q in raw_queries:
        cleaned = q.strip()
        # Filter out comments-only blocks
        lines = [l for l in cleaned.split("\n") if not l.strip().startswith("--") and l.strip()]
        if lines:
            valid_queries.append(cleaned)

    print(f"Found {len(valid_queries)} SQL queries to validate.\n")
    
    for idx, query in enumerate(valid_queries, 1):
        # Extract title from leading comment
        first_lines = [l.strip() for l in query.split("\n") if l.strip().startswith("-- Query") or l.strip().startswith("-- Business")]
        title = first_lines[0] if first_lines else f"Query {idx}"
        try:
            df = run_query(query)
            print(f"[{idx:02d}/20] PASSED: {title} -> Returned {len(df)} rows, cols: {list(df.columns)}")
        except Exception as e:
            print(f"[{idx:02d}/20] FAILED: {title} -> Error: {e}")
            raise e

if __name__ == "__main__":
    test_all_queries()
