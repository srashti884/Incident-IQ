"""
IncidentIQ - Synthetic Incident Dataset Generator
Generates realistic, internally-consistent enterprise IT incident data.
Data Lake output: data/raw/applications.csv, data/raw/services.csv, data/raw/incidents.csv
"""
import os
import csv
import json
import random
from datetime import datetime, timedelta

REF_NOW = datetime(2026, 9, 22, 12, 0, 0)
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

APPLICATIONS = [
    {"app_id": "APP-AWS", "name": "AWS Cloud Infrastructure", "short_name": "AWS", "tier": "Tier-1", "owner": "Cloud Ops Core", "criticality": "Critical"},
    {"app_id": "APP-PAY", "name": "Payment Gateway Service", "short_name": "Payment Gateway", "tier": "Tier-1", "owner": "FinTech Engineering", "criticality": "Critical"},
    {"app_id": "APP-AUTH", "name": "Auth & Identity Gateway", "short_name": "Auth Gateway", "tier": "Tier-1", "owner": "SecOps & IAM", "criticality": "Critical"},
    {"app_id": "APP-SAP", "name": "SAP ERP Core", "short_name": "SAP ERP", "tier": "Tier-2", "owner": "Enterprise Apps", "criticality": "High"},
    {"app_id": "APP-KAFKA", "name": "Kafka Stream Cluster", "short_name": "Kafka", "tier": "Tier-1", "owner": "Data Platform Team", "criticality": "Critical"},
    {"app_id": "APP-BILL", "name": "Billing Engine", "short_name": "Billing", "tier": "Tier-2", "owner": "Revenue Ops", "criticality": "High"},
    {"app_id": "APP-CRM", "name": "CRM Customer Portal", "short_name": "CRM", "tier": "Tier-2", "owner": "Customer Experience", "criticality": "Medium"},
    {"app_id": "APP-AD", "name": "Active Directory Sync", "short_name": "Active Directory", "tier": "Tier-3", "owner": "Internal IT Ops", "criticality": "Medium"}
]

SERVICES = [
    {"service_id": "SVC-EC2", "app_id": "APP-AWS", "name": "EC2 Compute Fleet", "tier": "Tier-1"},
    {"service_id": "SVC-RDS", "app_id": "APP-AWS", "name": "RDS Database Cluster", "tier": "Tier-1"},
    {"service_id": "SVC-S3",  "app_id": "APP-AWS", "name": "S3 Object Store", "tier": "Tier-1"},
    {"service_id": "SVC-VPC", "app_id": "APP-AWS", "name": "VPC Direct Connect", "tier": "Tier-1"},
    {"service_id": "SVC-PAY-API", "app_id": "APP-PAY", "name": "Checkout API", "tier": "Tier-1"},
    {"service_id": "SVC-PAY-SET", "app_id": "APP-PAY", "name": "Settlement Batch", "tier": "Tier-2"},
    {"service_id": "SVC-PAY-FRD", "app_id": "APP-PAY", "name": "Fraud Detection Engine", "tier": "Tier-1"},
    {"service_id": "SVC-AUTH-OAUTH", "app_id": "APP-AUTH", "name": "OAuth2 Token Service", "tier": "Tier-1"},
    {"service_id": "SVC-AUTH-MFA",   "app_id": "APP-AUTH", "name": "MFA Authenticator", "tier": "Tier-1"},
    {"service_id": "SVC-AUTH-SAML",  "app_id": "APP-AUTH", "name": "SAML Federation Provider", "tier": "Tier-2"},
    {"service_id": "SVC-SAP-FIN", "app_id": "APP-SAP", "name": "General Ledger Engine", "tier": "Tier-2"},
    {"service_id": "SVC-SAP-SCM", "app_id": "APP-SAP", "name": "Supply Chain Dispatch", "tier": "Tier-2"},
    {"service_id": "SVC-KAF-BRK", "app_id": "APP-KAFKA", "name": "Broker Cluster North", "tier": "Tier-1"},
    {"service_id": "SVC-KAF-CNS", "app_id": "APP-KAFKA", "name": "Event Consumer Group", "tier": "Tier-1"},
    {"service_id": "SVC-BIL-INV", "app_id": "APP-BILL", "name": "Invoice Dispatcher", "tier": "Tier-2"},
    {"service_id": "SVC-BIL-REC", "app_id": "APP-BILL", "name": "Recurring Subscription Daemon", "tier": "Tier-2"},
    {"service_id": "SVC-CRM-WEB", "app_id": "APP-CRM", "name": "Customer Support Dashboard", "tier": "Tier-3"},
    {"service_id": "SVC-CRM-API", "app_id": "APP-CRM", "name": "Salesforce Integration API", "tier": "Tier-2"},
    {"service_id": "SVC-AD-SYNC", "app_id": "APP-AD", "name": "Azure AD Connect Agent", "tier": "Tier-3"}
]

PATTERNS = [
    {
        "pattern_id": "RP-014",
        "fingerprint": "AWS + Timeout + Payment + API",
        "app_name": "Payment Gateway Service",
        "service_name": "Checkout API",
        "severity": "Critical",
        "title_template": "Checkout API downstream timeout during peak payment processing via AWS RDS",
        "root_cause": "Database connection pool exhaustion under sudden traffic burst",
        "category": "Database Contention",
        "frequency_weight": 42
    },
    {
        "pattern_id": "RP-008",
        "fingerprint": "Auth + Token + Expiration + Latency",
        "app_name": "Auth & Identity Gateway",
        "service_name": "OAuth2 Token Service",
        "severity": "High",
        "title_template": "OAuth2 token verification latency exceeding SLA threshold during token rotation",
        "root_cause": "Redis cache lock contention during simultaneous multi-region token refresh",
        "category": "Cache Concurrency",
        "frequency_weight": 35
    },
    {
        "pattern_id": "RP-022",
        "fingerprint": "Kafka + Consumer + Lag + Offset",
        "app_name": "Kafka Stream Cluster",
        "service_name": "Event Consumer Group",
        "severity": "High",
        "title_template": "Consumer group partition rebalance failure causing unbounded consumer lag",
        "root_cause": "Heartbeat timeout mismatch caused by long-running message handler",
        "category": "Consumer Starvation",
        "frequency_weight": 28
    },
    {
        "pattern_id": "RP-003",
        "fingerprint": "AWS + RDS + IOPS + Throttling",
        "app_name": "AWS Cloud Infrastructure",
        "service_name": "RDS Database Cluster",
        "severity": "Critical",
        "title_template": "AWS RDS Provisioned IOPS throttling during nocturnal automated snapshot",
        "root_cause": "Storage volume burst balance depletion during overlapping maintenance window",
        "category": "Infrastructure Limits",
        "frequency_weight": 31
    },
    {
        "pattern_id": "RP-019",
        "fingerprint": "Billing + Batch + Lock + Deadlock",
        "app_name": "Billing Engine",
        "service_name": "Invoice Dispatcher",
        "severity": "Medium",
        "title_template": "Invoice batch generation aborted due to transactional deadlock on billing table",
        "root_cause": "Unordered SQL update execution in parallelized invoice worker jobs",
        "category": "Application Deadlock",
        "frequency_weight": 24
    },
    {
        "pattern_id": "RP-005",
        "fingerprint": "AD + Sync + Certificate + Handshake",
        "app_name": "Active Directory Sync",
        "service_name": "Azure AD Connect Agent",
        "severity": "Low",
        "title_template": "Directory synchronization agent TLS handshake failure during cert rotation",
        "root_cause": "Mismatched intermediate CA trust chain on internal sync proxy server",
        "category": "Network & Security",
        "frequency_weight": 19
    }
]

GENERIC_INCIDENT_TEMPLATES = [
    ("High CPU utilization on {service} pods causing degraded response times", "Infrastructure Overload", "Resource Starvation", "High"),
    ("Intermittent 502 Bad Gateway responses reported on {service}", "Network/Gateway", "Reverse Proxy Gateway Timeout", "Critical"),
    ("Slow SQL query execution impacting {service} search queries", "Database", "Missing Composite Index on Created Date", "Medium"),
    ("Disk storage utilization exceeded 85% threshold on {service} worker", "Storage", "Uncompressed Log Retention Policy Lag", "Low"),
    ("Memory leak observed on {service} JVM instance after scheduled release", "Software Defect", "Native Memory Leak in Serialization Library", "High"),
    ("SSL certificate expiration warning within 7 days on {service} edge endpoint", "Configuration", "Automated Certbot Renewal Cron Misconfiguration", "Low"),
    ("Message drop rate spike detected on {service} ingestion queue", "Queue/Stream", "Queue Buffer Saturated by Upstream Surge", "High"),
    ("Dependency timeout calling external vendor API from {service}", "Third-party Dependency", "Upstream Partner Gateway Degradation", "Medium"),
    ("Stale cache entries served by {service} after deployment rollback", "Cache", "Cache Invalidation Webhook Failed on Deploy", "Medium"),
    ("Elevated 403 Forbidden authorization errors on {service}", "Security/Auth", "IAM Role Policy Scope Drift", "High"),
]

SEVERITY_SLA_TARGETS = {
    "Critical": 60,
    "High": 240,
    "Medium": 480,
    "Low": 1440
}

ENGINEERS = [
    "Alex Mercer", "Priya Sharma", "David Chen", "Sarah Jenkins",
    "Marcus Vance", "Elena Rostova", "Rohan Patel", "Chloe Martin",
    "Amina Al-Mansoor", "Lukas Weber"
]

def generate_dataset():
    print(f"Generating realistic dataset referencing {REF_NOW.strftime('%Y-%m-%d %H:%M:%S')}...")
    
    # 1. Write applications.csv
    app_csv_path = os.path.join(RAW_DIR, "applications.csv")
    with open(app_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["app_id", "name", "short_name", "tier", "owner", "criticality"])
        writer.writeheader()
        writer.writerows(APPLICATIONS)

    # 2. Write services.csv
    svc_csv_path = os.path.join(RAW_DIR, "services.csv")
    with open(svc_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["service_id", "app_id", "name", "tier"])
        writer.writeheader()
        writer.writerows(SERVICES)

    app_to_services = {}
    for svc in SERVICES:
        app_to_services.setdefault(svc["app_id"], []).append(svc)
    app_lookup = {a["app_id"]: a for a in APPLICATIONS}
    app_name_to_id = {a["name"]: a["app_id"] for a in APPLICATIONS}

    incidents = []
    inc_counter = 1001

    def create_incident(created_dt, app_name, svc_name, sev, status, title, root_cause, category, pat_id="", fprint=""):
        nonlocal inc_counter
        sla_target = SEVERITY_SLA_TARGETS[sev]
        if status in ["Resolved", "Closed"]:
            breached = random.random() < 0.20
            res_minutes = int(sla_target * (random.uniform(1.1, 2.2) if breached else random.uniform(0.2, 0.9)))
            assigned_dt = created_dt + timedelta(minutes=random.randint(3, 15))
            resolved_dt = created_dt + timedelta(minutes=res_minutes)
        else:
            elapsed = (REF_NOW - created_dt).total_seconds() / 60
            breached = elapsed > sla_target
            res_minutes = None
            assigned_dt = created_dt + timedelta(minutes=random.randint(3, 15))
            resolved_dt = None

        sev_multiplier = {"Critical": 40, "High": 25, "Medium": 15, "Low": 5}[sev]
        sla_penalty = 20 if breached else 0
        tier_bonus = 20 if app_name in ["AWS Cloud Infrastructure", "Payment Gateway Service", "Auth & Identity Gateway"] else 10
        impact_score = min(100, max(10, sev_multiplier + sla_penalty + tier_bonus + random.randint(3, 12)))

        inc = {
            "incident_id": f"INC-{inc_counter}",
            "title": title,
            "description": f"Incident logged for {app_name} - {svc_name}. Summary: {title}. Root cause category: {category}.",
            "application": app_name,
            "service": svc_name,
            "severity": sev,
            "priority": f"P{1 if sev == 'Critical' else (2 if sev == 'High' else (3 if sev == 'Medium' else 4))}",
            "status": status,
            "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_at": assigned_dt.strftime("%Y-%m-%d %H:%M:%S") if assigned_dt else "",
            "resolved_at": resolved_dt.strftime("%Y-%m-%d %H:%M:%S") if resolved_dt else "",
            "resolution_time_minutes": res_minutes if res_minutes is not None else "",
            "sla_target_minutes": sla_target,
            "sla_breached": 1 if breached else 0,
            "root_cause_category": category,
            "root_cause_summary": root_cause,
            "impact_score": impact_score,
            "reporter": random.choice(["Datadog Alert", "Prometheus Watcher", "PagerDuty Trigger", "CloudWatch Metric", "Helpdesk Tier-1"]),
            "assignee": random.choice(ENGINEERS),
            "pattern_id": pat_id,
            "fingerprint": fprint
        }
        inc_counter += 1
        return inc

    # A. Specific deterministic incidents for TODAY (Sept 22, 2026)
    # Including UNRESOLVED CRITICAL incidents
    incidents.append(create_incident(
        REF_NOW - timedelta(hours=2, minutes=15),
        "AWS Cloud Infrastructure", "RDS Database Cluster", "Critical", "Open",
        "Production primary RDS Aurora read replica replication lag critical alert",
        "Storage burst balance exhaustion during peak read operations", "Infrastructure Limits"
    ))
    incidents.append(create_incident(
        REF_NOW - timedelta(hours=3, minutes=45),
        "Payment Gateway Service", "Checkout API", "Critical", "In Progress",
        "Checkout API 504 gateway timeout cascade across regional payment endpoints",
        "Connection pool starvation triggered by external bank processor timeout", "Database Contention",
        "RP-014", "AWS + Timeout + Payment + API"
    ))
    incidents.append(create_incident(
        REF_NOW - timedelta(hours=1, minutes=30),
        "Auth & Identity Gateway", "OAuth2 Token Service", "Critical", "Open",
        "OAuth2 token validation service rate limit saturation in US-East zone",
        "Sudden spike in client credential renegotiation requests", "Security/Auth"
    ))
    incidents.append(create_incident(
        REF_NOW - timedelta(hours=4, minutes=10),
        "SAP ERP Core", "General Ledger Engine", "High", "In Progress",
        "SAP GL month-end balance posting job thread lock",
        "Contention on table ACC_DOC_POSTING during parallel processing", "Application Deadlock"
    ))
    incidents.append(create_incident(
        REF_NOW - timedelta(hours=5),
        "Kafka Stream Cluster", "Broker Cluster North", "Medium", "Resolved",
        "Kafka broker 03 disk space warning exceeded 80%",
        "Unpurged debug segment logs in test topic", "Storage"
    ))

    # B. Specific incidents for YESTERDAY (Sept 21, 2026)
    yesterday_date = REF_NOW - timedelta(days=1)
    for h in [2, 5, 8, 10, 11, 14, 16, 18, 20, 22]:
        dt = yesterday_date.replace(hour=h, minute=random.randint(5, 55))
        app = random.choice(APPLICATIONS)
        svc = random.choice(app_to_services[app["app_id"]])
        sev = random.choices(["Low", "Medium", "High", "Critical"], weights=[0.25, 0.40, 0.25, 0.10])[0]
        tpl = random.choice(GENERIC_INCIDENT_TEMPLATES)
        incidents.append(create_incident(
            dt, app["name"], svc["name"], sev,
            random.choice(["Resolved", "Resolved", "Closed"]),
            tpl[0].format(service=svc["name"]), tpl[2], tpl[1]
        ))

    # C. Specific recurring pattern occurrences
    for pat in PATTERNS:
        target_count = pat["frequency_weight"]
        for i in range(target_count):
            days_ago = int(random.triangular(2, 160, 20))
            hours_ago = random.randint(0, 23)
            dt = REF_NOW - timedelta(days=days_ago, hours=hours_ago, minutes=random.randint(0, 59))
            status = random.choices(["Resolved", "Closed"], weights=[0.75, 0.25])[0]
            incidents.append(create_incident(
                dt, pat["app_name"], pat["service_name"], pat["severity"], status,
                pat["title_template"], pat["root_cause"], pat["category"],
                pat["pattern_id"], pat["fingerprint"]
            ))

    # D. General dataset spanning past 180 days to reach ~1,280 total
    remaining = 1280 - len(incidents)
    for _ in range(remaining):
        days_ago = int(random.triangular(2, 180, 45))
        hours_ago = random.randint(0, 23)
        dt = REF_NOW - timedelta(days=days_ago, hours=hours_ago, minutes=random.randint(0, 59))

        app = random.choices(
            APPLICATIONS,
            weights=[0.24, 0.20, 0.16, 0.12, 0.10, 0.08, 0.06, 0.04]
        )[0]
        svc = random.choice(app_to_services[app["app_id"]])
        sev = random.choices(["Low", "Medium", "High", "Critical"], weights=[0.30, 0.40, 0.20, 0.10])[0]
        status = random.choices(["Resolved", "Closed"], weights=[0.7, 0.3])[0]
        tpl = random.choice(GENERIC_INCIDENT_TEMPLATES)
        incidents.append(create_incident(
            dt, app["name"], svc["name"], sev, status,
            tpl[0].format(service=svc["name"]), tpl[2], tpl[1]
        ))

    incidents.sort(key=lambda x: x["created_at"], reverse=True)

    # 3. Write incidents.csv
    inc_csv_path = os.path.join(RAW_DIR, "incidents.csv")
    fieldnames = list(incidents[0].keys())
    with open(inc_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incidents)

    # 4. Write patterns definition json
    pat_json_path = os.path.join(RAW_DIR, "recurring_definitions.json")
    with open(pat_json_path, "w", encoding="utf-8") as f:
        json.dump(PATTERNS, f, indent=2)

    return len(incidents)

if __name__ == "__main__":
    count = generate_dataset()
    print(f"Generated {count} incidents.")
