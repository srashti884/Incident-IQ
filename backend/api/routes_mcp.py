"""
IncidentIQ - Local MCP Inspection & Invocation Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.mcp.server import list_tools, invoke_tool

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

class MCPInvokeRequest(BaseModel):
    tool: str
    arguments: Optional[Dict[str, Any]] = None

@router.get("/tools")
def api_mcp_tools():
    return list_tools()

@router.post("/invoke")
def api_mcp_invoke(req: MCPInvokeRequest):
    return invoke_tool(req.tool, req.arguments or {})
