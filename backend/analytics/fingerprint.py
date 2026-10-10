"""
IncidentIQ - Incident Fingerprinting & Clustering
Uses Scikit-learn TF-IDF vectorization and Cosine Similarity to cluster
recurring incidents into deterministic fingerprints.
Provides Future Incident Prediction (Recurrence Risk) and Early Warning detection.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.database.connection import execute_query

REF_NOW = datetime(2026, 9, 22, 12, 0, 0)

def compute_recurrence_risk(
    total_occ: int,
    first_seen: str,
    last_seen: str,
    trend: str,
    occ_30d: int,
    occ_14d: int,
    ref_dt: datetime = REF_NOW
) -> Dict[str, Any]:
    """
    Estimates recurrence risk likelihood based on historical occurrences,
    recency (days since last event), and recent 30-day velocity.
    Labels: High Recurrence Risk, Medium Recurrence Risk, Low Recurrence Risk, Insufficient historical data.
    """
    try:
        first_dt = datetime.strptime(first_seen, "%Y-%m-%d %H:%M:%S")
        last_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return {
            "risk_level": "Insufficient Historical Data",
            "explanation": "Insufficient timestamp data to compute recurrence risk."
        }

    total_days = max((ref_dt - first_dt).days, 1)
    days_since_last = max((ref_dt - last_dt).days, 0)

    # Insufficient data safeguard
    if total_occ < 5 or total_days < 7:
        return {
            "risk_level": "Insufficient Historical Data",
            "explanation": f"Insufficient sample size ({total_occ} occurrences over {total_days} days) for statistically reliable estimation."
        }

    # Factor evaluation:
    # 1. High Recurrence Risk: Increasing trend, recent event within 7 days, and sustained 30-day velocity
    if trend == "Increasing" and days_since_last <= 7 and occ_30d >= 8:
        risk_level = "High Recurrence Risk"
        explanation = (
            f"Elevated recurrence likelihood based on high historical frequency ({total_occ} occurrences), "
            f"recent detection within {days_since_last} days, and an increasing 30-day velocity ({occ_30d} events)."
        )
    # 2. Medium Recurrence Risk: Consistent historical baseline with steady 30-day occurrences
    elif (trend in ["Increasing", "Stable"] and days_since_last <= 14) or (total_occ >= 20 and occ_30d >= 5):
        risk_level = "Medium Recurrence Risk"
        explanation = (
            f"Moderate recurrence likelihood with consistent historical baseline ({total_occ} occurrences) "
            f"and active events in the last month ({occ_30d} events in past 30 days)."
        )
    # 3. Low Recurrence Risk: Decreasing trend or elongated dormant interval
    else:
        risk_level = "Low Recurrence Risk"
        explanation = (
            f"Low recurrence likelihood with {trend.lower()} trajectory and extended interval "
            f"since last recorded event ({days_since_last} days dormant)."
        )

    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "days_since_last_seen": days_since_last,
        "recent_30d_count": occ_30d
    }

def compute_early_warning(
    total_occ: int,
    first_seen: str,
    last_seen: str,
    trend: str,
    occ_30d: int,
    ref_dt: datetime = REF_NOW
) -> Dict[str, Any]:
    """
    Detects if a known recurring pattern is escalating significantly compared
    to its historical baseline.
    Warning triggers ONLY when there is clear evidence of an increasing pattern.
    """
    try:
        first_dt = datetime.strptime(first_seen, "%Y-%m-%d %H:%M:%S")
        last_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return {
            "triggered": False,
            "message": None,
            "reason": None
        }

    total_days = max((ref_dt - first_dt).days, 1)

    # Avoid false warnings caused by very small sample sizes
    if total_occ < 10 or total_days < 30:
        return {
            "triggered": False,
            "message": None,
            "reason": "Insufficient historical data baseline for early warning calculation."
        }

    # Baseline daily rate prior to trailing 30 days
    baseline_days = max(total_days - 30, 1)
    baseline_occ = max(total_occ - occ_30d, 0)
    baseline_daily_rate = baseline_occ / float(baseline_days)

    recent_daily_rate = occ_30d / 30.0

    # Warning conditions:
    # Trend is 'Increasing' AND recent rate >= baseline rate * 1.20 (at least 20% surge) AND recent occ >= 5
    is_increasing_surge = (
        trend == "Increasing" and
        occ_30d >= 5 and
        baseline_daily_rate > 0 and
        (recent_daily_rate >= baseline_daily_rate * 1.20)
    )

    if is_increasing_surge:
        pct_increase = round(((recent_daily_rate - baseline_daily_rate) / baseline_daily_rate) * 100)
        return {
            "triggered": True,
            "message": "Recurring pattern increasing — investigation recommended.",
            "reason": (
                f"Recent 30-day frequency ({occ_30d} incidents, {recent_daily_rate:.2f}/day) "
                f"is {pct_increase}% higher than the historical baseline ({baseline_daily_rate:.2f}/day)."
            ),
            "percent_increase": pct_increase
        }

    # Stable or decreasing patterns do NOT show an increasing warning
    return {
        "triggered": False,
        "message": None,
        "reason": f"Pattern frequency is {trend.lower()} and within historical tolerance."
    }

def get_recurring_patterns_analytics() -> List[Dict[str, Any]]:
    """
    Fetches structured recurring patterns from warehouse with enriched analytics,
    future incident prediction (recurrence risk), and early warning indicators.
    """
    sql = """
    SELECT 
        pattern_id,
        fingerprint,
        application,
        service,
        severity,
        occurrences,
        first_seen,
        last_seen,
        avg_resolution_minutes,
        trend,
        possible_root_cause,
        root_cause_category
    FROM recurring_patterns
    ORDER BY occurrences DESC;
    """
    patterns = execute_query(sql)

    # Query recent 14d and 30d occurrences from incidents table
    recent_query = """
    SELECT 
        pattern_id,
        SUM(CASE WHEN created_at >= date('2026-09-22', '-14 days') THEN 1 ELSE 0 END) as occ_14d,
        SUM(CASE WHEN created_at >= date('2026-09-22', '-30 days') THEN 1 ELSE 0 END) as occ_30d
    FROM incidents
    WHERE pattern_id != '' AND pattern_id IS NOT NULL
    GROUP BY pattern_id;
    """
    recent_rows = execute_query(recent_query)
    recent_map = {r["pattern_id"]: r for r in recent_rows}

    # Enrich each pattern with Prediction and Early Warning
    enriched_patterns = []
    for pat in patterns:
        pid = pat["pattern_id"]
        rec = recent_map.get(pid, {"occ_14d": 0, "occ_30d": 0})
        occ_14d = rec["occ_14d"] or 0
        occ_30d = rec["occ_30d"] or 0

        # Feature 1: Future Incident Prediction / Recurrence Risk
        prediction = compute_recurrence_risk(
            total_occ=pat["occurrences"],
            first_seen=pat["first_seen"],
            last_seen=pat["last_seen"],
            trend=pat["trend"],
            occ_30d=occ_30d,
            occ_14d=occ_14d
        )

        # Feature 2: Early Warning for Increasing Patterns
        early_warning = compute_early_warning(
            total_occ=pat["occurrences"],
            first_seen=pat["first_seen"],
            last_seen=pat["last_seen"],
            trend=pat["trend"],
            occ_30d=occ_30d
        )

        pat_enriched = dict(pat)
        pat_enriched["prediction"] = prediction
        pat_enriched["early_warning"] = early_warning
        enriched_patterns.append(pat_enriched)

    return enriched_patterns

def cluster_ad_hoc_incidents(threshold: float = 0.65, max_incidents: int = 300) -> List[Dict[str, Any]]:
    """
    Performs on-the-fly TF-IDF and Cosine Similarity clustering on recent incidents
    to detect uncatalogued emerging patterns.
    """
    sql = f"""
    SELECT incident_id, title, application, service, severity, created_at
    FROM incidents
    ORDER BY created_at DESC
    LIMIT {max_incidents};
    """
    incidents = execute_query(sql)
    if not incidents or len(incidents) < 2:
        return []

    corpus = [f"{i['application']} {i['service']} {i['title']}" for i in incidents]
    vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    clusters = []
    visited = set()

    for idx, inc in enumerate(incidents):
        if idx in visited:
            continue
        cluster_members = [inc]
        visited.add(idx)

        for other_idx, other_inc in enumerate(incidents):
            if other_idx not in visited and similarity_matrix[idx][other_idx] >= threshold:
                cluster_members.append(other_inc)
                visited.add(other_idx)

        if len(cluster_members) >= 3:
            clusters.append({
                "cluster_size": len(cluster_members),
                "primary_application": inc["application"],
                "primary_service": inc["service"],
                "sample_title": inc["title"],
                "incident_ids": [m["incident_id"] for m in cluster_members[:5]]
            })

    clusters.sort(key=lambda x: x["cluster_size"], reverse=True)
    return clusters
