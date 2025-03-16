import json
import logging
import os
import re
import signal
from importlib.resources import files
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from preswald.engine.managers.branding import BrandingManager
from preswald.engine.service import PreswaldService


logger = logging.getLogger(__name__)


def create_app(script_path: Optional[str] = None) -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI()
    service = PreswaldService.initialize(script_path)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure static files
    service.branding_manager = _setup_static_files(app)

    # Store service instance
    app.state.service = service

    # Set script path if provided
    if script_path:
        service.script_path = script_path

    # Register routes
    _register_routes(app)

    return app


def _register_static_routes(app: FastAPI):
    """Register routes for static file serving"""

    @app.get("/")
    async def serve_index():
        """Serve the index.html file with branding configuration"""
        try:
            return _handle_index_request(app.state.service)
        except Exception as e:
            logger.error(f"Error serving index: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.get("/favicon.ico")
    async def serve_favicon():
        """Serve favicon.ico from preswald.toml branding or fallback to assets directory"""
        try:
            return _handle_favicon_request(app.state.service)
        except Exception as e:
            logger.error(f"Error serving favicon: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.get("/static/{path:path}")
    async def get_static(path: str):
        """Serve static files that aren't in assets"""
        file_path = os.path.join(app.state.service.branding_manager.static_dir, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="File not found")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve the SPA for any other routes"""
        return await serve_index()


def _register_websocket_routes(app: FastAPI):
    """Register WebSocket routes"""

    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """Handle WebSocket connections"""
        try:
            await app.state.service.register_client(client_id, websocket)
            try:
                while not app.state.service._is_shutting_down:
                    message = await websocket.receive_json()
                    await app.state.service.handle_client_message(client_id, message)
            except WebSocketDisconnect:
                logger.info(f"Client disconnected: {client_id}")
            finally:
                await app.state.service.unregister_client(client_id)
        except Exception as e:
            logger.error(f"Error in websocket endpoint: {e}")
            if not app.state.service._is_shutting_down:
                await websocket.close(code=1011, reason=str(e))


def _register_routes(app: FastAPI):
    """Register all application routes"""

    _register_websocket_routes(app)
    _register_static_routes(app)  # order matters for static routes


def start_server(script: Optional[str] = None, port: int = 8501):
    """Start the FastAPI server"""
    app = create_app(script)

    config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)

    # Handle shutdown signals
    async def handle_shutdown(signum=None, frame=None):
        """Handle graceful shutdown of the server"""
        logger.info("Shutting down server...")
        await app.state.service.shutdown()

    # Handle shutdown signals
    def sync_handle_shutdown(signum, frame):
        """Synchronous wrapper for the async shutdown handler"""
        loop = asyncio.get_event_loop()
        loop.create_task(handle_shutdown(signum, frame))  # noqa: RUF006

    signal.signal(signal.SIGINT, sync_handle_shutdown)
    signal.signal(signal.SIGTERM, sync_handle_shutdown)

    try:
        import asyncio

        asyncio.run(server.serve())
    except KeyboardInterrupt:
        asyncio.run(handle_shutdown())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def _setup_static_files(app: FastAPI) -> BrandingManager:
    """Set up static file serving and initialize branding manager"""
    # Get package directories
    base_dir = files("preswald")
    static_dir = base_dir / "static"
    assets_dir = static_dir / "assets"

    # Ensure directories exist
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # Initialize branding manager
    branding_manager = BrandingManager(static_dir, assets_dir)

    # Mount static files
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    return branding_manager


def _handle_index_request(service: PreswaldService) -> HTMLResponse:
    """Handle index.html requests with proper branding"""
    try:
        static_dir = files("preswald") / "static"
        index_path = static_dir / "index.html"

        if not os.path.exists(index_path):
            logger.error(f"Index file not found at {index_path}")
            return HTMLResponse(
                "<html><body><h1>Error: Frontend not properly installed</h1></body></html>"
            )

        # Get branding configuration
        branding = service.branding_manager.get_branding_config(service.script_path)

        # Read and modify index.html
        with open(index_path) as f:
            content = f.read()

        # Replace title
        content = content.replace(
            "<title>Vite + React</title>", f"<title>{branding['name']}</title>"
        )

        import time

        # Add favicon links
        favicon_links = f"""    <link rel="icon" type="image/x-icon" href="{branding["favicon"]}" />
    <link rel="shortcut icon" type="image/x-icon" href="{branding["favicon"]}?timestamp={time.time()}" />"""
        content = re.sub(r'<link[^>]*rel="icon"[^>]*>', "", content)
        content = content.replace(
            '<meta charset="UTF-8" />', f'<meta charset="UTF-8" />\n{favicon_links}'
        )

        # Add branding data
        branding_script = (
            f"<script>window.PRESWALD_BRANDING = {json.dumps(branding)};</script>"
        )
        content = content.replace("</head>", f"{branding_script}\n</head>")

        logger.info(f"Serving index.html with branding: {branding}")
        return HTMLResponse(content)

    except Exception as e:
        logger.error(f"Error serving index: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


def _handle_favicon_request(service: PreswaldService) -> HTMLResponse:
    """Handle index.html requests with proper branding"""
    try:
        # Get branding configuration
        branding = service.branding_manager.get_branding_config(service.script_path)
        return FileResponse(branding["favicon"])
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
