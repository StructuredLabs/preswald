import json
import logging
import os
import re
import signal
from typing import Optional

import pkg_resources
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from preswald.engine.branding import BrandingManager
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


def _register_routes(app: FastAPI):
    """Register all application routes"""

    @app.get("/")
    async def serve_index():
        """Serve the index.html file with branding configuration"""
        try:
            return _handle_index_request(app.state.service)
        except Exception as e:
            logger.error(f"Error serving index: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/favicon.ico")
    async def serve_favicon():
        """Serve favicon.ico from config.toml branding or fallback to assets directory"""
        try:
            return _handle_favicon_request(app.state.service)
        except Exception as e:
            logger.error(f"Error serving favicon: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/api/connections")
    async def get_connections():
        """Get all active connections and their states"""
        # TODO need to properly implement as in server.py
        return {
            "connections": {}  # app.state.service.connection_manager.get_all_connections(),
        }

    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """Handle WebSocket connections"""
        try:
            # Register client and get script runner
            await app.state.service.register_client(client_id, websocket)

            # Handle messages until disconnection
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


def start_server(script: Optional[str] = None, port: int = 8501):
    """Start the FastAPI server"""
    app = create_app(script)

    # Load port from config if available
    if script:
        try:
            script_dir = os.path.dirname(script)
            config_path = os.path.join(script_dir, "config.toml")
            if os.path.exists(config_path):
                import toml

                config = toml.load(config_path)
                if "project" in config and "port" in config["project"]:
                    port = config["project"]["port"]
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)

    signal.signal(signal.SIGINT, app.state.service.shutdown)
    signal.signal(signal.SIGTERM, app.state.service.shutdown)

    try:
        import asyncio

        asyncio.run(server.serve())

    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        asyncio.run(app.state.service.shutdown())
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


def _setup_static_files(app: FastAPI) -> BrandingManager:
    """Set up static file serving and initialize branding manager"""
    # Get package directories
    base_dir = pkg_resources.resource_filename("preswald", "")
    static_dir = os.path.join(base_dir, "static")
    assets_dir = os.path.join(static_dir, "assets")

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
        static_dir = pkg_resources.resource_filename("preswald", "static")
        index_path = os.path.join(static_dir, "index.html")

        if not os.path.exists(index_path):
            logger.error(f"Index file not found at {index_path}")
            return HTMLResponse(
                "<html><body><h1>Error: Frontend not properly installed</h1></body></html>"
            )

        # Get branding configuration
        branding = service.branding_manager.get_branding_config(service.script_path)

        # Read and modify index.html
        with open(index_path, "r") as f:
            content = f.read()

        # Replace title
        content = content.replace(
            "<title>Vite + React</title>", f'<title>{branding["name"]}</title>'
        )

        # Add favicon links
        favicon_links = f"""    <link rel="icon" type="image/x-icon" href="{branding["favicon"]}" />
    <link rel="shortcut icon" type="image/x-icon" href="{branding["favicon"]}" />"""
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
        raise HTTPException(status_code=500, detail="Internal server error")


def _handle_favicon_request(service: PreswaldService) -> HTMLResponse:
    """Handle index.html requests with proper branding"""
    try:
        # Get branding configuration
        branding = service.branding_manager.get_branding_config(service.script_path)
        return FileResponse(branding["favicon"])
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
