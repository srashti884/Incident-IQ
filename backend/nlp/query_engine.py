"""
IncidentIQ - Core Natural Language Query Processing Engine
Executes end-to-end NLP query execution pipeline:
User Query -> Normalization -> Entity Extraction -> Intent Detection ->
Semantic Mapping -> Query Planning -> SQLite Warehouse Execution ->
Analytics Aggregation -> Chart Recommendation -> Natural Language Explanation.
"""
import time
from typing import Dict, Any, List
from backend.nlp.entity_extractor import extract_entities
from backend.nlp.intent_classifier import classify_intent
from backend.nlp.query_planner import build_query_plan
from backend.database.connection import execute_query

SUPPORTED_EXAMPLE_QUERIES = [
    "What incidents were reported yesterday?",
    "Show all critical incidents from last week.",
    "Which applications generated the most incidents this quarter?",
    "Show AWS incidents from last month.",
    "Which applications have the highest SLA breaches?",
    "Identify recurring incidents.",
    "What are the most common root causes?",
    "Which services have the longest resolution time?",
    "Show me unresolved critical incidents."
]

def process_natural_language_query(query: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    clean_query = query.strip()

    if not clean_query:
        return {
            "success": False,
            "error": "Query cannot be empty.",
            "supported_examples": SUPPORTED_EXAMPLE_QUERIES
        }

    # 1. Entity Extraction
    entities = extract_entities(clean_query)

    # 2. Intent Classification
    intent, confidence = classify_intent(clean_query, entities)

    # 3. Query Planning & SQL Compilation
    plan = build_query_plan(clean_query, intent, entities)

    # 4. Warehouse Execution
    try:
        raw_results = execute_query(plan["sql"], plan["params"])
    except Exception as e:
        return {
            "success": False,
            "error": f"Warehouse query execution failed: {str(e)}",
            "supported_examples": SUPPORTED_EXAMPLE_QUERIES
        }

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 5. Format applied filters description
    applied_filters = []
    if entities.get("application"):
        applied_filters.append(f"Application: {entities['application']}")
    if entities.get("service"):
        applied_filters.append(f"Service: {entities['service']}")
    if entities.get("severity"):
        applied_filters.append(f"Severity: {entities['severity']}")
    if entities.get("status"):
        val = entities["status"]
        status_str = ", ".join(val) if isinstance(val, list) else val
        applied_filters.append(f"Status: {status_str}")
    if entities.get("sla_breached") is not None:
        applied_filters.append("SLA: Breached" if entities["sla_breached"] == 1 else "SLA: Met")
    if entities.get("time_range"):
        applied_filters.append(f"Time: {entities['time_range'].get('label', 'Custom Range')}")

    if not applied_filters:
        applied_filters.append("All Records (No explicit filters)")

    # 6. Post-process based on view_type
    view_type = plan.get("view_type", "incident_list")
    chart_data = []
    chart_config = {
        "type": plan.get("chart_type", "bar"),
        "x_key": plan.get("chart_x", "dimension"),
        "y_key": plan.get("chart_y", "metric_value"),
        "title": plan.get("metric_name", "Analytical Results")
    }

    summary_text = ""
    kpi_summary = {}

    if view_type == "grouped_analytics":
        chart_data = raw_results
        top_item = raw_results[0] if raw_results else None
        total_sum = sum(r.get("metric_value", 0) for r in raw_results)
        
        if top_item:
            dim_name = top_item.get("dimension", "Unknown")
            val = top_item.get("metric_value", 0)
            summary_text = f"Top {plan.get('chart_x', 'Category').title()}: {dim_name} with {val:,} {plan.get('metric_name', '').lower()}."
            kpi_summary = {
                "top_entity": dim_name,
                "top_value": val,
                "total_volume": total_sum,
                "categories_analyzed": len(raw_results)
            }
        else:
            summary_text = "No grouped incident records found matching query criteria."
            kpi_summary = {"total_volume": 0}

    elif view_type == "patterns":
        chart_data = [
            {"fingerprint": r["pattern_id"], "occurrences": r["occurrences"], "label": r["fingerprint"]}
            for r in raw_results
        ]
        chart_config = {
            "type": "bar",
            "x_key": "fingerprint",
            "y_key": "occurrences",
            "title": "Recurring Pattern Frequencies"
        }
        total_pats = len(raw_results)
        total_occ = sum(r.get("occurrences", 0) for r in raw_results)
        summary_text = f"Identified {total_pats} chronic incident patterns representing {total_occ} total occurrences."
        kpi_summary = {
            "total_patterns": total_pats,
            "total_occurrences": total_occ,
            "top_pattern": raw_results[0]["pattern_id"] if raw_results else "None"
        }

    elif view_type == "root_cause":
        chart_data = [
            {"category": r["root_cause_category"], "count": r["incident_count"]}
            for r in raw_results
        ]
        chart_config = {
            "type": "bar",
            "x_key": "category",
            "y_key": "count",
            "title": "Incidents by Root Cause Category"
        }
        total_inc = sum(r.get("incident_count", 0) for r in raw_results)
        top_cause = raw_results[0]["root_cause_category"] if raw_results else "None"
        summary_text = f"Primary root cause driver: {top_cause}. Evaluated {len(raw_results)} recurring root-cause vectors."
        kpi_summary = {
            "primary_driver": top_cause,
            "total_incidents_analyzed": total_inc,
            "distinct_causes": len(raw_results)
        }

    elif view_type == "trend":
        chart_data = raw_results
        chart_config = {
            "type": "line",
            "x_key": "date_day",
            "y_key": "incident_count",
            "title": "Incident Trajectory"
        }
        total_inc = sum(r.get("incident_count", 0) for r in raw_results)
        summary_text = f"Analyzed trend trajectory over {len(raw_results)} reporting days with {total_inc} incidents."
        kpi_summary = {
            "total_period_incidents": total_inc,
            "days_analyzed": len(raw_results)
        }

    else:
        # incident_list
        count = len(raw_results)
        crit_count = sum(1 for r in raw_results if r.get("severity") == "Critical")
        breach_count = sum(1 for r in raw_results if r.get("sla_breached") == 1)
        resolved_times = [r["resolution_time_minutes"] for r in raw_results if r.get("resolution_time_minutes") is not None]
        avg_res = round(sum(resolved_times) / len(resolved_times), 1) if resolved_times else 0

        # Build severity distribution chart data
        sev_counts = {}
        for r in raw_results:
            sev_counts[r.get("severity", "Unknown")] = sev_counts.get(r.get("severity", "Unknown"), 0) + 1
        
        chart_data = [{"severity": k, "count": v} for k, v in sev_counts.items()]
        chart_config = {
            "type": "bar",
            "x_key": "severity",
            "y_key": "count",
            "title": "Matching Incidents by Severity"
        }

        kpi_summary = {
            "matching_incidents": count,
            "critical_count": crit_count,
            "sla_breaches": breach_count,
            "avg_mttr_minutes": avg_res
        }

        # Build natural summary
        time_ctx = f" ({entities['time_range']['label']})" if entities.get("time_range") else ""
        app_ctx = f" for {entities['application']}" if entities.get("application") else ""
        sev_ctx = f" {entities['severity']}" if entities.get("severity") else ""
        summary_text = f"Found {count} incident records{sev_ctx}{app_ctx}{time_ctx}. {crit_count} Critical, {breach_count} SLA breaches."

    return {
        "success": True,
        "query": clean_query,
        "summary": summary_text,
        "kpis": kpi_summary,
        "view_type": view_type,
        "applied_filters": applied_filters,
        "table_data": raw_results,
        "chart_data": chart_data,
        "chart_config": chart_config,
        "query_understanding": {
            "intent": intent,
            "entities": {
                "application": entities.get("application"),
                "service": entities.get("service"),
                "severity": entities.get("severity"),
                "status": entities.get("status"),
                "sla_breached": entities.get("sla_breached"),
                "time_range": entities.get("time_range", {}).get("label") if entities.get("time_range") else "All Time"
            },
            "metric": entities.get("metric", "incident_count"),
            "data_source": "Local Incident Warehouse (SQLite)",
            "execution_time_ms": elapsed_ms
        }
    }
