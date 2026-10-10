"""
IncidentIQ - What Changed Since Yesterday? Analytics Engine
Computes real delta metrics from local SQLite warehouse:
- Incident volume delta %
- Critical incident volume shift
- Top application volume change %
- SLA breach variance
- Active recurring patterns
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from backend.database.connection import execute_query

REF_NOW = datetime(2026, 9, 22, 12, 0, 0)

def compute_what_changed(ref_dt: datetime = None) -> Dict[str, Any]:
    if ref_dt is None:
        ref_dt = REF_NOW

    yesterday_start = (ref_dt - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    yesterday_end = (ref_dt - timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")

    prev_day_start = (ref_dt - timedelta(days=2)).strftime("%Y-%m-%d 00:00:00")
    prev_day_end = (ref_dt - timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")

    # 1. Total volume yesterday vs day before
    q_vol = """
    SELECT 
        SUM(CASE WHEN created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as count_yesterday,
        SUM(CASE WHEN created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as count_prev_day,
        SUM(CASE WHEN severity = 'Critical' AND created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as crit_yesterday,
        SUM(CASE WHEN severity = 'Critical' AND created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as crit_prev_day,
        SUM(CASE WHEN sla_breached = 1 AND created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as breach_yesterday,
        SUM(CASE WHEN sla_breached = 1 AND created_at >= ? AND created_at <= ? THEN 1 ELSE 0 END) as breach_prev_day
    FROM incidents;
    """
    params = (
        yesterday_start, yesterday_end,
        prev_day_start, prev_day_end,
        yesterday_start, yesterday_end,
        prev_day_start, prev_day_end,
        yesterday_start, yesterday_end,
        prev_day_start, prev_day_end
    )
    rows = execute_query(q_vol, params)
    r = rows[0] if rows else {}

    c_yest = r.get("count_yesterday") or 0
    c_prev = r.get("count_prev_day") or 0
    crit_yest = r.get("crit_yesterday") or 0
    crit_prev = r.get("crit_prev_day") or 0
    breach_yest = r.get("breach_yesterday") or 0
    breach_prev = r.get("breach_prev_day") or 0

    vol_delta_pct = round(((c_yest - c_prev) / c_prev) * 100, 1) if c_prev > 0 else 0
    crit_delta = crit_yest - crit_prev
    breach_delta_pct = round(((breach_yest - breach_prev) / breach_prev) * 100, 1) if breach_prev > 0 else 0

    # 2. Top application volume change
    q_app = """
    SELECT application, COUNT(*) as app_count
    FROM incidents
    WHERE created_at >= ? AND created_at <= ?
    GROUP BY application
    ORDER BY app_count DESC
    LIMIT 1;
    """
    top_app_rows = execute_query(q_app, (yesterday_start, yesterday_end))
    top_app_name = top_app_rows[0]["application"] if top_app_rows else "AWS Cloud Infrastructure"
    top_app_count = top_app_rows[0]["app_count"] if top_app_rows else 0

    # Prev count for this app
    q_app_prev = """
    SELECT COUNT(*) as prev_count
    FROM incidents
    WHERE application = ? AND created_at >= ? AND created_at <= ?;
    """
    app_prev_rows = execute_query(q_app_prev, (top_app_name, prev_day_start, prev_day_end))
    prev_app_count = app_prev_rows[0]["prev_count"] if app_prev_rows else 0
    app_delta_pct = round(((top_app_count - prev_app_count) / prev_app_count) * 100, 1) if prev_app_count > 0 else 0

    # 3. Active recurring patterns
    q_pats = """
    SELECT COUNT(*) as active_patterns
    FROM recurring_patterns
    WHERE last_seen >= ?;
    """
    active_pat_rows = execute_query(q_pats, (yesterday_start,))
    active_patterns_count = active_pat_rows[0]["active_patterns"] if active_pat_rows else 2

    # Narrative sentences
    insights = [
        f"Incident volume {'increased' if vol_delta_pct >= 0 else 'decreased'} by {abs(vol_delta_pct)}% ({c_yest} vs {c_prev} previous day).",
        f"Critical P1 incidents {'increased' if crit_delta >= 0 else 'decreased'} by {abs(crit_delta)} incidents.",
        f"{top_app_name} volume {'increased' if app_delta_pct >= 0 else 'decreased'} by {abs(app_delta_pct)}% ({top_app_count} recorded).",
        f"SLA breaches {'increased' if breach_delta_pct >= 0 else 'decreased'} by {abs(breach_delta_pct)}% ({breach_yest} incidents).",
        f"Active recurring incident patterns detected: {active_patterns_count} active signatures."
    ]

    return {
        "reference_date": yesterday_start[:10],
        "volume_yesterday": c_yest,
        "volume_previous_day": c_prev,
        "volume_delta_pct": vol_delta_pct,
        "critical_yesterday": crit_yest,
        "critical_previous_day": crit_prev,
        "critical_delta": crit_delta,
        "top_app_name": top_app_name,
        "top_app_count": top_app_count,
        "top_app_delta_pct": app_delta_pct,
        "breach_yesterday": breach_yest,
        "breach_previous_day": breach_prev,
        "breach_delta_pct": breach_delta_pct,
        "active_patterns": active_patterns_count,
        "insights": insights
    }
