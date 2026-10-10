"""
IncidentIQ - Enterprise Local Incident Analytics & Reporting Platform
Main FastAPI Backend Server
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.api.routes_analytics import router as analytics_router
from backend.api.routes_nlp import router as nlp_router
from backend.api.routes_incidents import router as incidents_router
from backend.api.routes_patterns import router as patterns_router
from backend.api.routes_reports import router as reports_router
from backend.api.routes_mcp import router as mcp_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

app = FastAPI(
    title="IncidentIQ",
    description="Enterprise Operational Incident Analytics and Reporting Platform",
    version="1.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(analytics_router)
app.include_router(nlp_router)
app.include_router(incidents_router)
app.include_router(patterns_router)
app.include_router(reports_router)
app.include_router(mcp_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "IncidentIQ",
        "environment": "corporate-local",
        "version": "1.0.0"
    }

# If the frontend has been built into frontend/dist, serve static files and provide SPA fallback
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept API requests
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        target_file = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        index_html = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_html):
            return FileResponse(index_html)
        return JSONResponse(status_code=404, content={"detail": "Frontend build not found"})
    
@app.get("/")
async def index():
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return JSONResponse(
        status_code=404,
        content={"detail": "Frontend build not found"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
