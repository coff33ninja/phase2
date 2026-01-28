"""Nexus - Dashboard & Interface main server."""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from loguru import logger

from config import config
from api import metrics_router, patterns_router, chat_router, control_router
from api.status import router as status_router
from websockets.metrics_stream import metrics_handler

# Create FastAPI app
app = FastAPI(
    title="Nexus Dashboard",
    description="Central hub for Phase 2 system monitoring and control",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(metrics_router)
app.include_router(patterns_router)
app.include_router(chat_router)
app.include_router(control_router)
app.include_router(status_router)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard page."""
    html_file = Path(__file__).parent / "templates" / "index.html"
    
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    
    # Fallback HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 10px;
            }
            .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 40px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .api-link {
                color: #ffd700;
                text-decoration: none;
                font-weight: bold;
            }
            .api-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Nexus Dashboard</h1>
            <p class="subtitle">Central Hub for Phase 2 System Monitoring</p>
            
            <div class="card">
                <h2>📊 API Endpoints</h2>
                <ul>
                    <li><a href="/api/metrics/current" class="api-link">Current Metrics</a></li>
                    <li><a href="/api/metrics/history" class="api-link">Metrics History</a></li>
                    <li><a href="/api/metrics/processes" class="api-link">Process List</a></li>
                    <li><a href="/api/patterns/learned" class="api-link">Learned Patterns</a></li>
                    <li><a href="/api/patterns/anomalies" class="api-link">Anomalies</a></li>
                    <li><a href="/api/control/profiles" class="api-link">Guardian Profiles</a></li>
                    <li><a href="/docs" class="api-link">API Documentation</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h2>🔌 WebSocket</h2>
                <p>Connect to <code>ws://localhost:8000/ws/metrics</code> for real-time metrics streaming</p>
            </div>
            
            <div class="card">
                <h2>✅ Status</h2>
                <p>Nexus is running and ready to serve!</p>
                <p>Version: 0.1.0</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "components": {
            "sentinel": config.sentinel_db_path.exists(),
            "oracle": config.oracle_db_path.exists(),
            "sage": config.sage_db_path.exists(),
            "guardian": config.guardian_db_path.exists()
        }
    }


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    await metrics_handler.connect(websocket)
    await metrics_handler.send_metrics(websocket)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Nexus Dashboard starting...")
    logger.info(f"Server: http://{config.host}:{config.port}")
    logger.info(f"API Docs: http://{config.host}:{config.port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Nexus Dashboard shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower()
    )
