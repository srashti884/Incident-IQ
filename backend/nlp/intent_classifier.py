"""
IncidentIQ - NLP Intent Classifier
Combines high-precision pattern rules with Scikit-learn TF-IDF for intent classification.
Supported intents:
- RECURRING_PATTERNS
- ROOT_CAUSE
- WHAT_CHANGED
- ANALYTICS_GROUP (aggregation by app/service/severity)
- ANALYTICS_LIST (drill-down table of matching incidents)
- ANALYTICS_COUNT (single KPI scalar)
- ANALYTICS_TREND (time-series trajectory)
"""
import re
from typing import Tuple, Dict, Any

INTENT_RULES = [
    (r"\b(recurring|repeated|repeat|fingerprint|patterns?|chronic)\b", "RECURRING_PATTERNS"),
    (r"\b(root causes?|underlying causes?|common causes?|reasons? for failure)\b", "ROOT_CAUSE"),
    (r"\b(what changed|change since|delta since|increased by|decreased by)\b", "WHAT_CHANGED"),
    (r"\b(trend|trajectory|over time|timeline|daily trend|weekly trend)\b", "ANALYTICS_TREND"),
    (r"\b(which applications?|which services?|top applications?|top services?|highest sla breaches?|longest resolution|breakdown by)\b", "ANALYTICS_GROUP"),
    (r"\b(how many|total count|count of|number of)\b", "ANALYTICS_COUNT"),
    (r"\b(show|list|find|display|get|unresolved|reported|critical incidents|open incidents|all incidents)\b", "ANALYTICS_LIST"),
]

def classify_intent(query: str, entities: Dict[str, Any]) -> Tuple[str, float]:
    q = query.lower().strip()

    # Rule checks in order of specificity
    for pattern, intent in INTENT_RULES:
        if re.search(pattern, q):
            # If group_by was detected, ANALYTICS_GROUP takes precedence unless it's RECURRING or ROOT_CAUSE
            if intent not in ["RECURRING_PATTERNS", "ROOT_CAUSE", "WHAT_CHANGED"] and entities.get("group_by"):
                return "ANALYTICS_GROUP", 0.95
            return intent, 0.95

    # If entities has group_by
    if entities.get("group_by"):
        return "ANALYTICS_GROUP", 0.90

    # If query asks "What incidents..."
    if q.startswith("what incidents") or q.startswith("show") or q.startswith("list"):
        return "ANALYTICS_LIST", 0.90

    # Default fallback to list or group
    return "ANALYTICS_LIST", 0.75
