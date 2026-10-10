"""
IncidentIQ - Local MCP Dispatcher
Provides discovery and invocation interface for all local MCP tools.
"""
from typing import Dict, Any, Callable
from backend.mcp import tools

TOOL_REGISTRY: Dict[str, Callable] = {
    "get_incident_schema": tools.get_incident_schema,
    "search_incidents": tools.search_incidents,
    "get_incident_metrics": tools.get_incident_metrics,
    "get_application_metrics": tools.get_application_metrics,
    "get_trend_metrics": tools.get_trend_metrics,
    "get_recurring_patterns": tools.get_recurring_patterns,
    "get_root_cause_context": tools.get_root_cause_context
}

def list_tools() -> Dict[str, Any]:
    return {
        "mcp_version": "1.0-local",
        "description": "Local MCP-compatible incident analytics data provider",
        "tools": [
            {
                "name": name,
                "doc": fn.__doc__.strip() if fn.__doc__ else "Local analytical tool"
            }
            for name, fn in TOOL_REGISTRY.items()
        ]
    }

def invoke_tool(tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    if arguments is None:
        arguments = {}
    if tool_name not in TOOL_REGISTRY:
        return {
            "error": f"Tool '{tool_name}' not found.",
            "available_tools": list(TOOL_REGISTRY.keys())
        }
    try:
        fn = TOOL_REGISTRY[tool_name]
        result = fn(**arguments)
        return {
            "success": True,
            "tool": tool_name,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "tool": tool_name,
            "error": str(e)
        }
