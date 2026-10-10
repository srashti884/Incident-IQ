"""
IncidentIQ - Database Connection & Query Executor
Manages local SQLite connections, executes safe parameterized queries,
provides health checks, row counts, and table inspection.
"""
import os
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse", "incidentiq.db")

def get_db_connection() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Local warehouse database not found at {DB_PATH}. Please run init_warehouse.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def execute_query(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def execute_query_df(query: str, params: Tuple = ()) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

def get_warehouse_stats() -> Dict[str, Any]:
    if not os.path.exists(DB_PATH):
        return {
            "status": "DISCONNECTED",
            "file_size_kb": 0,
            "total_incidents": 0,
            "total_applications": 0,
            "total_services": 0,
            "total_patterns": 0,
            "db_path": DB_PATH
        }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents")
        inc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM applications")
        app_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM services")
        svc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM recurring_patterns")
        pat_count = cursor.fetchone()[0]

        cursor.execute("SELECT key, value FROM system_metadata")
        meta = {r["key"]: r["value"] for r in cursor.fetchall()}

        size_kb = round(os.path.getsize(DB_PATH) / 1024, 1)

        return {
            "status": "CONNECTED",
            "file_size_kb": size_kb,
            "total_incidents": inc_count,
            "total_applications": app_count,
            "total_services": svc_count,
            "total_patterns": pat_count,
            "last_etl_run": meta.get("last_etl_run", "Unknown"),
            "db_path": DB_PATH
        }
    finally:
        conn.close()
