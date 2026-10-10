"""
IncidentIQ - Automated API Endpoint Validation Test Suite
Tests FastAPI endpoints directly via TestClient.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    client = TestClient(app)
    print("Testing IncidentIQ API Endpoints...")

    # 1. Health
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[OK] Health Check: OK")

    # 2. System Status
    r = client.get("/api/analytics/system-status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "CONNECTED"
    print(f"[OK] Warehouse Status: CONNECTED ({data['total_incidents']} records, {data['file_size_kb']} KB)")

    # 3. Dashboard Analytics
    r = client.get("/api/analytics/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert "kpis" in d
    assert d["kpis"]["total_incidents"] > 0
    print(f"[OK] Dashboard KPIs: {d['kpis']['total_incidents']} incidents, {d['kpis']['critical_incidents']} critical")

    # 4. What Changed
    r = client.get("/api/analytics/what-changed")
    assert r.status_code == 200
    wc = r.json()
    assert "insights" in wc
    print(f"[OK] What Changed Since Yesterday: {len(wc['insights'])} delta insights computed")

    # 5. Impact vs Severity Matrix
    r = client.get("/api/analytics/impact-matrix")
    assert r.status_code == 200
    im = r.json()
    assert len(im["points"]) > 0
    print(f"[OK] Impact Matrix: {len(im['points'])} points analyzed")

    # 6. Natural Language Query
    r = client.post("/api/nlp/query", json={"query": "Show critical AWS incidents from last month."})
    assert r.status_code == 200
    nl_res = r.json()
    assert nl_res["success"] is True
    print(f"[OK] Natural Language Query: Found {len(nl_res['table_data'])} matching records in {nl_res['query_understanding']['execution_time_ms']} ms")

    # 7. Direct Query PDF Download
    r = client.post("/api/reports/query-pdf", json=nl_res)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 1000
    print(f"[OK] Direct Query PDF Download: Generated {len(r.content)} bytes valid PDF")

    # 8. General Audit Report PDF Download
    r = client.post("/api/reports/general-pdf", json={})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    print(f"[OK] General Report PDF Download: Generated {len(r.content)} bytes valid PDF")

    # 9. Excel Export
    r = client.get("/api/reports/excel")
    assert r.status_code == 200
    assert len(r.content) > 10000
    print(f"[OK] Excel Export: Generated {len(r.content)} bytes valid .xlsx workbook")

    # 10. Local MCP Tools List & Invoke
    r = client.get("/api/mcp/tools")
    assert r.status_code == 200
    tools_list = r.json()
    assert len(tools_list["tools"]) >= 7
    print(f"[OK] Local MCP Registry: {len(tools_list['tools'])} tools available")

    r = client.post("/api/mcp/invoke", json={"tool": "get_incident_metrics", "arguments": {}})
    assert r.status_code == 200
    mcp_res = r.json()
    assert mcp_res["success"] is True
    print("[OK] Local MCP Invocation (get_incident_metrics): Executed successfully")

    # 11. Incidents Explorer & Story Drill-down
    r = client.get("/api/incidents?limit=10")
    assert r.status_code == 200
    inc_data = r.json()
    first_id = inc_data["results"][0]["incident_id"]
    r_story = client.get(f"/api/incidents/{first_id}/story")
    assert r_story.status_code == 200
    story = r_story.json()
    assert len(story["timeline"]) >= 3
    print(f"[OK] Incident Explorer & Story Drill-down for {first_id}: {len(story['timeline'])} timeline stages")

    # 12. Recurring Patterns Prediction & Early Warning
    r_pat = client.get("/api/patterns")
    assert r_pat.status_code == 200
    pats = r_pat.json().get("patterns", [])
    assert len(pats) >= 6
    rp14 = next(p for p in pats if p["pattern_id"] == "RP-014")
    assert "prediction" in rp14 and "risk_level" in rp14["prediction"]
    assert rp14["prediction"]["risk_level"] == "High Recurrence Risk"
    assert "early_warning" in rp14 and rp14["early_warning"]["triggered"] is True
    assert "investigation recommended" in rp14["early_warning"]["message"].lower()

    rp08 = next(p for p in pats if p["pattern_id"] == "RP-008")
    assert rp08["early_warning"]["triggered"] is False

    rp05 = next(p for p in pats if p["pattern_id"] == "RP-005")
    assert rp05["early_warning"]["triggered"] is False
    assert rp05["prediction"]["risk_level"] == "Low Recurrence Risk"
    print(f"[OK] Recurring Patterns: Future Incident Prediction & Early Warning verified ({len(pats)} patterns)")

    print("\nALL BACKEND API TESTS COMPLETED AND VERIFIED 100% SUCCESFULLY!")

if __name__ == "__main__":
    run_tests()
