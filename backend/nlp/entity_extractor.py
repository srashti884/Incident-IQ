"""
IncidentIQ - NLP Entity Extractor
Extracts domain entities (application, service, severity, status, SLA condition,
metrics, groupings, limits) from natural language query strings using semantic mappings.
Uses strict token and phrase boundary matching to avoid accidental false positives.
"""
import re
from typing import Dict, Any, List, Optional
from backend.semantic_layer.engine import semantic_engine
from backend.nlp.date_parser import parse_temporal_expression

STOP_WORDS = {"a", "an", "the", "in", "on", "at", "for", "to", "of", "with", "by", "from", "show", "me", "what", "which", "are", "is", "were", "was", "all"}

def extract_entities(query: str) -> Dict[str, Any]:
    q = query.lower().strip()
    entities: Dict[str, Any] = {
        "application": None,
        "service": None,
        "severity": None,
        "status": None,
        "sla_breached": None,
        "time_range": None,
        "metric": "incident_count",
        "group_by": None,
        "order_direction": "DESC",
        "limit": None
    }

    # 1. Temporal expression
    start_dt, end_dt, time_label = parse_temporal_expression(query)
    if start_dt and end_dt:
        entities["time_range"] = {
            "start": start_dt,
            "end": end_dt,
            "label": time_label
        }

    # 2. Group by detection FIRST so we know if "applications" is the grouping dimension rather than a specific app filter
    if re.search(r"\b(which applications?|top applications?|by application|by app|applications generating)\b", q):
        entities["group_by"] = "application"
    elif re.search(r"\b(which services?|top services?|by service|services with)\b", q):
        entities["group_by"] = "service"
    elif re.search(r"\b(by severity|severity breakdown)\b", q):
        entities["group_by"] = "severity"
    elif re.search(r"\b(by status|status breakdown)\b", q):
        entities["group_by"] = "status"

    # 3. Application extraction (only if not simply grouping by "applications" without a specific application name)
    # Check multi-word aliases first, then single-word aliases with strict word boundaries
    app_aliases = semantic_engine.mappings.get("entity_mappings", {}).get("application", {}).get("aliases", {})
    # Sort aliases by length descending
    sorted_aliases = sorted(app_aliases.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        # Don't match generic words "app", "application", "system" as specific application filters
        if alias in ["app", "apps", "application", "applications", "system", "systems", "platform"]:
            continue
        # Use word boundary
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, q):
            entities["application"] = app_aliases[alias]
            break

    # 4. Service extraction
    svc_aliases = semantic_engine.mappings.get("service_mappings", {})
    sorted_svc_aliases = sorted(svc_aliases.keys(), key=len, reverse=True)
    for alias in sorted_svc_aliases:
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, q):
            entities["service"] = svc_aliases[alias]
            break

    # 5. Severity extraction
    sev_aliases = semantic_engine.mappings.get("entity_mappings", {}).get("severity", {}).get("aliases", {})
    for alias in sorted(sev_aliases.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, q):
            entities["severity"] = sev_aliases[alias]
            break

    # 6. Status extraction
    stat_aliases = semantic_engine.mappings.get("entity_mappings", {}).get("status", {}).get("aliases", {})
    for alias in sorted(stat_aliases.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, q):
            entities["status"] = stat_aliases[alias]
            break

    # 7. SLA Breach detection
    if re.search(r"\b(sla breaches?|breached|missed sla|sla violation|breaches?)\b", q):
        # If query is asking "which applications have the highest SLA breaches", metric is sla_breaches,
        # but don't restrict to sla_breached = 1 in WHERE clause if grouping by application
        if entities["group_by"]:
            entities["metric"] = "sla_breaches"
        else:
            entities["sla_breached"] = 1
    elif re.search(r"\b(within sla|met sla|sla met)\b", q):
        entities["sla_breached"] = 0

    # 8. Metric detection
    if re.search(r"\b(resolution times?|longest resolution|slowest resolution|duration|mttr|time to resolve)\b", q):
        entities["metric"] = "average_resolution_time"
    elif re.search(r"\b(sla breach rate|highest sla breaches?|highest breaches?|most breaches?)\b", q):
        entities["metric"] = "sla_breaches"
    elif re.search(r"\b(impact score|highest impact|business impact)\b", q):
        entities["metric"] = "average_impact_score"
    elif "critical" in q and any(w in q for w in ["count", "number", "total"]):
        entities["metric"] = "critical_count"

    # 9. Limit
    top_match = re.search(r"\btop\s+(\d+)\b", q)
    if top_match:
        entities["limit"] = int(top_match.group(1))
    elif entities["group_by"] in ["application", "service"]:
        entities["limit"] = 10

    return entities
