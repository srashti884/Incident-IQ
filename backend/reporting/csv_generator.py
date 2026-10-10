"""
IncidentIQ - CSV Export Engine
Generates clean RFC-4180 compliant CSV exports for filtered records and query outputs.
"""
import io
import csv
from typing import List, Dict, Any

def generate_csv_from_dicts(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "No records matching query criteria."
    
    output = io.StringIO()
    fieldnames = list(records[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    return output.getvalue()
