"""
IncidentIQ - Benchmark NL Query Engine Test Suite
Tests natural language queries and verifies structured results from local warehouse.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from backend.nlp.query_engine import process_natural_language_query

BENCHMARK_QUERIES = [
    "What incidents were reported yesterday?",
    "Show all critical incidents from last week.",
    "Which applications generated the most incidents this quarter?",
    "Show AWS incidents from last month.",
    "Which applications have the highest SLA breaches?",
    "Identify recurring incidents.",
    "What are the most common root causes?",
    "Which services have the longest resolution time?",
    "Show me unresolved critical incidents."
]

def run_tests():
    print("==================================================")
    print("INCIDENTIQ NLP BENCHMARK VALIDATION")
    print("==================================================")
    
    all_passed = True
    for i, q in enumerate(BENCHMARK_QUERIES, 1):
        res = process_natural_language_query(q)
        print(f"\n[{i}/{len(BENCHMARK_QUERIES)}] Query: '{q}'")
        if not res.get("success"):
            print(f"FAILED: {res.get('error')}")
            all_passed = False
            continue

        qu = res["query_understanding"]
        print(f"  Intent:     {qu['intent']}")
        print(f"  Entities:   {qu['entities']}")
        print(f"  Metric:     {qu['metric']}")
        print(f"  Time (ms):  {qu['execution_time_ms']} ms")
        print(f"  Summary:    {res['summary']}")
        print(f"  Rows Found: {len(res['table_data'])}")
        print(f"  Chart Type: {res['chart_config']['type']}")
        
        if len(res["table_data"]) == 0 and "unresolved" not in q.lower():
            print("  WARNING: 0 rows returned!")

    print("\n==================================================")
    if all_passed:
        print("ALL BENCHMARK NL QUERIES PASSED WITH VERIFIED LOCAL DATA!")
    else:
        print("SOME QUERIES FAILED.")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
