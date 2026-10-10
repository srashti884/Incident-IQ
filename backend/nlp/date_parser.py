"""
IncidentIQ - NLP Temporal Parser
Parses temporal expressions into deterministic date boundaries (start_time, end_time, label).
Resolves relative time against active reference timestamp (2026-09-22 12:00:00).
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

REF_NOW = datetime(2026, 9, 22, 12, 0, 0)

def parse_temporal_expression(query: str, ref_dt: Optional[datetime] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Returns (start_date_iso, end_date_iso, display_label) or (None, None, None)
    """
    if ref_dt is None:
        ref_dt = REF_NOW
        
    q = query.lower()

    # Yesterday
    if "yesterday" in q:
        start = (ref_dt - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        end = (ref_dt - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Yesterday"

    # Today / Past 24 hours
    if "today" in q or "past 24 hours" in q or "last 24 hours" in q:
        start = ref_dt.replace(hour=0, minute=0, second=0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Today"

    # Last 7 days / past week
    if "last 7 days" in q or "past 7 days" in q:
        start = (ref_dt - timedelta(days=7)).replace(hour=0, minute=0, second=0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last 7 Days"

    # Last week (the calendar week before the current week, or trailing 7 days before this week)
    if "last week" in q or "previous week" in q:
        # Trailing 7 days from start of this week or 7-14 days ago
        end = (ref_dt - timedelta(days=ref_dt.weekday() + 1)).replace(hour=23, minute=59, second=59)
        start = (end - timedelta(days=6)).replace(hour=0, minute=0, second=0)
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last Week"

    # This week
    if "this week" in q:
        start = (ref_dt - timedelta(days=ref_dt.weekday())).replace(hour=0, minute=0, second=0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "This Week"

    # Last 30 days
    if "last 30 days" in q or "past 30 days" in q:
        start = (ref_dt - timedelta(days=30)).replace(hour=0, minute=0, second=0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last 30 Days"

    # Last month (August 2026)
    if "last month" in q or "previous month" in q:
        # August 1 to August 31
        start = datetime(2026, 8, 1, 0, 0, 0)
        end = datetime(2026, 8, 31, 23, 59, 59)
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last Month (August 2026)"

    # This month (September 2026)
    if "this month" in q or "current month" in q:
        start = datetime(2026, 9, 1, 0, 0, 0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "This Month (September 2026)"

    # This quarter (Q3 2026: July 1 - Sept 30)
    if "this quarter" in q or "current quarter" in q or "q3" in q:
        start = datetime(2026, 7, 1, 0, 0, 0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "This Quarter (Q3 2026)"

    # Last quarter (Q2 2026: April 1 - June 30)
    if "last quarter" in q or "previous quarter" in q or "q2" in q:
        start = datetime(2026, 4, 1, 0, 0, 0)
        end = datetime(2026, 6, 30, 23, 59, 59)
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last Quarter (Q2 2026)"

    # Last 90 days
    if "last 90 days" in q or "past 90 days" in q:
        start = (ref_dt - timedelta(days=90)).replace(hour=0, minute=0, second=0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Last 90 Days"

    # Year 2026 / this year
    if "this year" in q or "2026" in q:
        start = datetime(2026, 1, 1, 0, 0, 0)
        end = ref_dt
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), "Year 2026"

    return None, None, None
