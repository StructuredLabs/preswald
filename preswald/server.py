from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from preswald.scriptrunner import ScriptRunner
from preswald.themes import load_theme
from preswald.core import (
    update_component_state, 
    get_component_state, 
    get_all_component_states,
    _rendered_html,
    clear_component_states
)
from typing import Dict, Any, Optional
import os
import uvicorn
import json
from collections import defaultdict
import logging
import pkg_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCRIPT_PATH: Optional[str] = None

# Store active websocket connections and their states
websocket_connections: Dict[str, WebSocket] = {}
client_states: Dict[str, Dict[str, Any]] = {}

# Store persistent component states
component_states: Dict[str, Any] = {}

try:
    # Get the package's static directory using pkg_resources
    BASE_DIR = pkg_resources.resource_filename('preswald', '')
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    ASSETS_DIR = os.path.join(STATIC_DIR, "assets")

    # Ensure directories exist
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Mount static files only if directories exist and contain files
    if os.path.exists(ASSETS_DIR) and os.listdir(ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
        logger.info(f"Mounted assets directory: {ASSETS_DIR}")
    else:
        logger.warning(f"Assets directory not found or empty: {ASSETS_DIR}")

except Exception as e:
    logger.error(f"Error setting up static files: {str(e)}")
    raise

@app.get("/")
async def serve_index():
    """Serve the index.html file"""
    try:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            # Load config if script path is set
            title = "Preswald"  # Default title
            if SCRIPT_PATH:
                try:
                    config_path = os.path.join(os.path.dirname(SCRIPT_PATH), "config.toml")
                    print(f"Loading config from {config_path}")
                    import toml
                    config = toml.load(config_path)
                    print(f"Loaded config in server.py: {config}")
                    print(f"Loaded config in server.py title: {config.get('project', {}).get('title')}")
                    if config.get("project", {}).get("title"):
                        title = config["project"]["title"]
                except Exception as e:
                    logger.error(f"Error loading config for index: {e}")

            # Read and modify the index.html content
            with open(index_path, 'r') as f:
                content = f.read()
                # Replace the title tag content
                content = content.replace('<title>Vite + React</title>', f'<title>{title}</title>')
            
            return HTMLResponse(content)
        else:
            logger.error(f"Index file not found at {index_path}")
            return HTMLResponse("<html><body><h1>Error: Frontend not properly installed</h1></body></html>")
    except Exception as e:
        logger.error(f"Error serving index: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files with proper error handling"""
    try:
        # Security check: prevent directory traversal
        requested_path = os.path.abspath(os.path.join(STATIC_DIR, path))
        if not requested_path.startswith(os.path.abspath(STATIC_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")

        if os.path.exists(requested_path) and os.path.isfile(requested_path):
            return FileResponse(requested_path)
        elif path == "" or not os.path.exists(requested_path):
            # SPA routing - return index.html for non-existent paths
            return await serve_index()
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error serving static file {path}: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/logo.png")
async def serve_logo():
    """Serve the logo file with proper error handling"""
    try:
        logo_path = os.path.join(STATIC_DIR, "logo.png")
        if os.path.exists(logo_path) and os.path.isfile(logo_path):
            return FileResponse(logo_path)
        raise HTTPException(status_code=404, detail="Logo not found")
    except Exception as e:
        logger.error(f"Error serving logo: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Internal server error")

async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    logger.debug(f"[Broadcast] Sending to {len(websocket_connections)} clients: {message}")
    
    for client_id, connection in list(websocket_connections.items()):
        try:
            await connection.send_json(message)
            logger.debug(f"[Broadcast] Sent to client {client_id}")
        except Exception as e:
            logger.error(f"[Broadcast] Error sending to client {client_id}: {e}")
            # Remove dead connections
            websocket_connections.pop(client_id, None)

async def broadcast_state_update(client_id: str, component_id: str, value: Any):
    """Broadcast component state update to all clients except sender"""
    message = {
        "type": "component_update",
        "component_id": component_id,
        "value": value
    }
    
    for ws_id, connection in websocket_connections.items():
        if ws_id != client_id:  # Don't send back to sender
            try:
                await connection.send_json(message)
                logger.debug(f"[State Update] Broadcasted to client {ws_id}: {component_id} = {value}")
            except Exception as e:
                logger.error(f"[State Update] Error broadcasting to client {ws_id}: {e}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections"""
    logger.info(f"[WebSocket] New connection request from client: {client_id}")
    await websocket.accept()
    logger.info(f"[WebSocket] Connection accepted for client: {client_id}")
    
    # Store the connection
    websocket_connections[client_id] = websocket
    client_states[client_id] = {}
    
    # Create ScriptRunner instance for this connection
    script_runner = ScriptRunner(
        session_id=client_id,
        send_message_callback=broadcast_message,
        initial_states=component_states  # Pass the persistent states
    )
    
    try:
        # Load and send config immediately after connection
        if SCRIPT_PATH:
            config_path = os.path.join(os.path.dirname(SCRIPT_PATH), "config.toml")
            config = load_theme(config_path)
            await websocket.send_json({
                "type": "config",
                "config": config
            })
            logger.info(f"[WebSocket] Sent config to client {client_id}")
            
            # Send current component states
            current_states = get_all_component_states()
            await websocket.send_json({
                "type": "initial_state",
                "states": current_states
            })
            logger.info(f"[WebSocket] Sent initial states to client {client_id}: {current_states}")
            
            # Start script execution
            logger.info(f"[WebSocket] Starting script execution for client {client_id}")
            await script_runner.start(SCRIPT_PATH)
            
            # After script execution, send all components if they exist
            components = list(_rendered_html)
            if components:  # Only send if there are components
                await websocket.send_json({
                    "type": "components",
                    "components": components
                })
                logger.info(f"[WebSocket] Sent components to client {client_id}: {components}")
            
        while True:
            try:
                data = await websocket.receive_json()
                logger.debug(f"[WebSocket] Received message from client {client_id}: {data}")
                
                if data.get("type") == "component_update":
                    logger.info(f"[Component Update] Received from client {client_id}:")
                    logger.info(f"  - Raw data: {data}")
                    states = data.get("states", {})
                    
                    if not states:
                        logger.warning(f"[Component Update] No states in update from client {client_id}")
                        continue
                    
                    # Update component states
                    for component_id, value in states.items():
                        try:
                            # Store old state for logging
                            old_state = get_component_state(component_id)
                            logger.info(f"[Component Update] Processing {component_id}:")
                            logger.info(f"  - Old value: {old_state}")
                            logger.info(f"  - New value: {value}")
                            
                            # Update both persistent and core states
                            component_states[component_id] = value
                            update_component_state(component_id, value)
                            client_states[client_id][component_id] = value
                            
                            logger.info(f"  - Updated persistent state: {component_states[component_id]}")
                            
                            # Send acknowledgment back to the client
                            await websocket.send_json({
                                "type": "state_update_ack",
                                "component_id": component_id,
                                "value": value
                            })
                            
                            # Broadcast state update to other clients
                            await broadcast_state_update(client_id, component_id, value)
                            logger.info(f"  - Broadcasted to other clients")
                            
                        except Exception as e:
                            logger.error(f"[Component Update] Error updating {component_id}: {e}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "content": {
                                    "message": str(e),
                                    "componentId": component_id
                                }
                            })
                    
                    try:
                        # Rerun script with new states
                        logger.info(f"[Script Rerun] Triggering with states: {states}")
                        await script_runner.rerun(new_widget_states=states)
                        logger.info("[Script Rerun] Completed successfully")
                        
                        # After rerun, send updated components if they exist
                        components = list(_rendered_html)
                        if components:  # Only send if there are components
                            await websocket.send_json({
                                "type": "components",
                                "components": components
                            })
                            logger.info(f"[WebSocket] Sent updated components to client {client_id}")
                        
                    except Exception as e:
                        logger.error(f"[Script Rerun] Error: {e}", exc_info=True)
                        await websocket.send_json({
                            "type": "error",
                            "content": {
                                "message": str(e)
                            }
                        })
                
            except json.JSONDecodeError as e:
                logger.error(f"[WebSocket] Invalid JSON from client {client_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": {
                        "message": "Invalid JSON message received"
                    }
                })
            except Exception as e:
                logger.error(f"[WebSocket] Error processing message from client {client_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": {
                        "message": str(e)
                    }
                })
                raise
            
    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client disconnected: {client_id}")
        # Clean up client state
        client_states.pop(client_id, None)
    except Exception as e:
        logger.error(f"[WebSocket] Error in connection for client {client_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "content": {
                    "message": str(e)
                }
            })
        except:
            pass
    finally:
        # Clean up the connection
        websocket_connections.pop(client_id, None)
        client_states.pop(client_id, None)
        logger.info(f"[WebSocket] Cleaned up connection for client {client_id}")


def _send_message_callback(msg: dict):
    """
    Callback function that ScriptRunner will use to send messages back to the frontend.
    In a WebSocket setup, this would send directly through the socket.
    For HTTP, we'll need to store messages and let the frontend poll for them.
    """
    # For now, we'll just print the messages
    # In a real implementation, we might store these in a queue or database
    print(f"Message from ScriptRunner: {msg}")


# Initialize a single ScriptRunner instance for handling Python script execution
script_runner = ScriptRunner(
    session_id="default_session", send_message_callback=_send_message_callback
)


@app.get("/api/components")
async def get_components():
    """
    API to fetch dynamic components data.
    """
    return [
        {"type": "button", "label": "Click Me"},
        {"type": "slider", "label": "Adjust Volume", "min": 0, "max": 100},
        {"type": "text", "label": "Enter Name", "placeholder": "Your Name"},
        {"type": "checkbox", "label": "Agree to Terms"},
        {
            "type": "selectbox",
            "label": "Select Option",
            "options": ["Option 1", "Option 2", "Option 3"],
        },
        {"type": "progress", "label": "Loading...", "value": 50},
        {"type": "spinner", "label": "Loading..."},
        {"type": "alert", "message": "This is an alert!", "level": "info"},
        {
            "type": "image",
            "src": "https://cdn.pixabay.com/photo/2020/07/21/01/33/cute-5424776_1280.jpg",
            "alt": "Placeholder image",
        },
        {
            "type": "text_input",
            "label": "Type here",
            "placeholder": "Type something here",
        },
        {"type": "connection"},
        {
            "type": "table",
            "data": [
                {"Index": 1, "Value": 1},
                {"Index": 2, "Value": 2},
                {"Index": 3, "Value": 3},
            ],
        },
        {"type": "plot", "data": [1, 2, 3]},
    ]


@app.get("/api/run_script")
async def run_script():
    """
    API to run script.
    """
    await script_runner.start(script_path=SCRIPT_PATH)


def start_server(script=None, port=8501):
    """
    Start the FastAPI server.

    Args:
        port (int): The port to run the server on.
    """
    print(f"Starting Preswald server at http://localhost:{port}")
    global SCRIPT_PATH

    if script:
        SCRIPT_PATH = os.path.abspath(script)
        print(f"Will run script: {SCRIPT_PATH}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
