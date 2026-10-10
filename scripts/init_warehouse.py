"""
IncidentIQ - Local Warehouse Initializer & ETL Pipeline
Processes raw Data Lake CSVs into data/processed/incidents_clean.csv
Loads cleaned records into SQLite warehouse: data/warehouse/incidentiq.db
Applies schema, constraints, and B-tree indexes.
"""
import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")
DB_PATH = os.path.join(WAREHOUSE_DIR, "incidentiq.db")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(WAREHOUSE_DIR, exist_ok=True)

def run_etl():
    print("Step 1: Ingesting Raw Data Lake files...")
    apps_df = pd.read_csv(os.path.join(RAW_DIR, "applications.csv"))
    services_df = pd.read_csv(os.path.join(RAW_DIR, "services.csv"))
    incidents_df = pd.read_csv(os.path.join(RAW_DIR, "incidents.csv"))

    print(f"Loaded {len(incidents_df)} raw incidents.")

    # Data Processing & Cleansing
    print("Step 2: Processing and normalizing incident records...")
    incidents_df["created_at"] = pd.to_datetime(incidents_df["created_at"])
    incidents_df["assigned_at"] = pd.to_datetime(incidents_df["assigned_at"], errors="coerce")
    incidents_df["resolved_at"] = pd.to_datetime(incidents_df["resolved_at"], errors="coerce")
    
    # Fill numeric nulls
    incidents_df["resolution_time_minutes"] = pd.to_numeric(incidents_df["resolution_time_minutes"], errors="coerce")
    incidents_df["sla_target_minutes"] = pd.to_numeric(incidents_df["sla_target_minutes"], errors="coerce").fillna(240).astype(int)
    incidents_df["sla_breached"] = pd.to_numeric(incidents_df["sla_breached"], errors="coerce").fillna(0).astype(int)
    incidents_df["impact_score"] = pd.to_numeric(incidents_df["impact_score"], errors="coerce").fillna(20).astype(int)
    
    # Fill string nulls
    incidents_df["pattern_id"] = incidents_df["pattern_id"].fillna("")
    incidents_df["fingerprint"] = incidents_df["fingerprint"].fillna("")
    incidents_df["root_cause_summary"] = incidents_df["root_cause_summary"].fillna("Under Investigation")
    incidents_df["root_cause_category"] = incidents_df["root_cause_category"].fillna("General")

    # Format datetime back to ISO strings for SQLite storage
    incidents_df["created_at_str"] = incidents_df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    incidents_df["assigned_at_str"] = incidents_df["assigned_at"].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
    incidents_df["resolved_at_str"] = incidents_df["resolved_at"].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")

    # Export clean processed CSV
    clean_csv_path = os.path.join(PROCESSED_DIR, "incidents_clean.csv")
    incidents_df.to_csv(clean_csv_path, index=False)
    print(f"Exported processed data to {clean_csv_path}")

    # Step 3: SQLite Warehouse Loading
    print(f"Step 3: Loading into SQLite Warehouse: {DB_PATH}...")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable WAL mode for high performance
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")

    # Schema creation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        app_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        short_name TEXT NOT NULL,
        tier TEXT NOT NULL,
        owner TEXT NOT NULL,
        criticality TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        service_id TEXT PRIMARY KEY,
        app_id TEXT NOT NULL,
        name TEXT NOT NULL,
        tier TEXT NOT NULL,
        FOREIGN KEY (app_id) REFERENCES applications(app_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        application TEXT NOT NULL,
        service TEXT NOT NULL,
        severity TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        assigned_at TEXT,
        resolved_at TEXT,
        resolution_time_minutes REAL,
        sla_target_minutes INTEGER NOT NULL,
        sla_breached INTEGER NOT NULL,
        root_cause_category TEXT NOT NULL,
        root_cause_summary TEXT NOT NULL,
        impact_score INTEGER NOT NULL,
        reporter TEXT NOT NULL,
        assignee TEXT NOT NULL,
        pattern_id TEXT,
        fingerprint TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recurring_patterns (
        pattern_id TEXT PRIMARY KEY,
        fingerprint TEXT NOT NULL,
        application TEXT NOT NULL,
        service TEXT NOT NULL,
        severity TEXT NOT NULL,
        occurrences INTEGER NOT NULL,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        avg_resolution_minutes REAL NOT NULL,
        trend TEXT NOT NULL,
        possible_root_cause TEXT NOT NULL,
        root_cause_category TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Populate applications
    apps_df.to_sql("applications", conn, if_exists="append", index=False)

    # Populate services
    services_df.to_sql("services", conn, if_exists="append", index=False)

    # Prepare incidents insert data
    incidents_to_insert = []
    for _, row in incidents_df.iterrows():
        incidents_to_insert.append((
            row["incident_id"],
            row["title"],
            row["description"],
            row["application"],
            row["service"],
            row["severity"],
            row["priority"],
            row["status"],
            row["created_at_str"],
            row["assigned_at_str"] if row["assigned_at_str"] else None,
            row["resolved_at_str"] if row["resolved_at_str"] else None,
            row["resolution_time_minutes"] if pd.notnull(row["resolution_time_minutes"]) else None,
            int(row["sla_target_minutes"]),
            int(row["sla_breached"]),
            row["root_cause_category"],
            row["root_cause_summary"],
            int(row["impact_score"]),
            row["reporter"],
            row["assignee"],
            row["pattern_id"],
            row["fingerprint"]
        ))

    cursor.executemany("""
    INSERT INTO incidents (
        incident_id, title, description, application, service, severity,
        priority, status, created_at, assigned_at, resolved_at,
        resolution_time_minutes, sla_target_minutes, sla_breached,
        root_cause_category, root_cause_summary, impact_score,
        reporter, assignee, pattern_id, fingerprint
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, incidents_to_insert)

    # Calculate and populate recurring_patterns table
    print("Step 4: Compiling recurring pattern statistics...")
    pat_query = """
    SELECT 
        pattern_id,
        fingerprint,
        application,
        service,
        severity,
        COUNT(*) as occurrences,
        MIN(created_at) as first_seen,
        MAX(created_at) as last_seen,
        ROUND(AVG(resolution_time_minutes), 1) as avg_resolution_minutes,
        root_cause_summary as possible_root_cause,
        root_cause_category
    FROM incidents
    WHERE pattern_id != '' AND pattern_id IS NOT NULL
    GROUP BY pattern_id;
    """
    patterns_df = pd.read_sql_query(pat_query, conn)
    
    # Assign trend based on recent activity (e.g. if incidents occurred within last 14 days)
    trends = []
    for _, prow in patterns_df.iterrows():
        last_seen_dt = datetime.strptime(prow["last_seen"], "%Y-%m-%d %H:%M:%S")
        days_since_last = (datetime(2026, 9, 22, 12, 0, 0) - last_seen_dt).days
        if days_since_last <= 3:
            trends.append("Increasing")
        elif days_since_last <= 14:
            trends.append("Stable")
        else:
            trends.append("Decreasing")
    patterns_df["trend"] = trends

    patterns_df.to_sql("recurring_patterns", conn, if_exists="append", index=False)

    # Add metadata record
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value, updated_at) VALUES (?, ?, ?)",
                   ("last_etl_run", now_str, now_str))
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value, updated_at) VALUES (?, ?, ?)",
                   ("total_incidents", str(len(incidents_to_insert)), now_str))
    cursor.execute("INSERT OR REPLACE INTO system_metadata (key, value, updated_at) VALUES (?, ?, ?)",
                   ("version", "IncidentIQ-1.0.0", now_str))

    # Step 5: Create Indexes for fast querying
    print("Step 5: Creating SQLite indexes for high-speed local queries...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_id ON incidents(incident_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_created_at ON incidents(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_severity ON incidents(severity);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_status ON incidents(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_app ON incidents(application);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_service ON incidents(service);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_sla ON incidents(sla_breached);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inc_pattern ON incidents(pattern_id);")

    conn.commit()
    conn.close()

    print(f"ETL and Warehouse initialization successful! Loaded {len(incidents_to_insert)} incidents into {DB_PATH}")

if __name__ == "__main__":
    run_etl()
