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

from preswald.engine.celery import CeleryEngine
from preswald.engine.managers.branding import BrandingManager
from preswald.engine.service import PreswaldService

logger = logging.getLogger(__name__)

# Global celery engine instance
celery_engine = None


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

    # Configure static files and branding manager
    branding_manager = _setup_static_files(app)
    setattr(service, 'branding_manager', branding_manager)

    # Store service instance
    app.state.service = service

    # Initialize CeleryEngine
    global celery_engine
    celery_engine = CeleryEngine()

    # Set script path if provided
    if script_path:
        service.script_path = script_path
        # Start celery worker and trigger initial connection parsing
        celery_engine.start_worker(script_path)

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


def _register_api_routes(app: FastAPI):
    """Register API routes"""

    @app.get("/api/connections")
    async def get_connections():
        """Get all active connections and their states"""
        global celery_engine
        if celery_engine:
            return celery_engine.get_latest_result()
        return {
            "connections": [],
            "error": "Celery engine not initialized",
            "timestamp": 0,
            "is_parsing": False,
        }


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

    _register_api_routes(app)
    _register_websocket_routes(app)
    _register_static_routes(app)  # order matters for static routes


def start_server(script: Optional[str] = None, port: int = 8501):
    """Start the FastAPI server"""
    app = create_app(script)

    config_port = None
    # Load port from config if available
    if script:
        try:
            script_dir = os.path.dirname(script)
            config_path = os.path.join(script_dir, "preswald.toml")
            if os.path.exists(config_path):
                import toml

                config = toml.load(config_path)
                if "project" in config and "port" in config["project"]:
                    config_port = config["project"]["port"]
                    logger.info(f"Using port {config_port} from config.toml")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    # Use port priority: CLI argument > config file > default
    final_port = port if port != 8501 else (config_port if config_port is not None else 8501)
    logger.info(f"Starting server on port {final_port}")

    # Set environment variable for frontend
    os.environ["PRESWALD_PORT"] = str(final_port)

    config = uvicorn.Config(app, host="0.0.0.0", port=final_port, loop="asyncio")
    server = uvicorn.Server(config)

    # Handle shutdown signals
    def handle_shutdown(signum, frame):
        logger.info("Shutting down server...")
        global celery_engine
        if celery_engine:
            celery_engine.stop_worker()
        app.state.service.shutdown()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        import asyncio

        asyncio.run(server.serve())

    except KeyboardInterrupt:
        handle_shutdown(None, None)
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
        with open(index_path) as f:
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
        raise HTTPException(status_code=500, detail="Internal server error") from e


def _handle_favicon_request(service: PreswaldService) -> FileResponse:
    """Handle favicon requests with proper branding"""
    try:
        # Get branding configuration
        branding = service.branding_manager.get_branding_config(service.script_path)
        return FileResponse(branding["favicon"])
    except Exception as e:
        logger.error(f"Error serving favicon: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
