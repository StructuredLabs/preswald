import asyncio
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from preswald.engine.base_service import BasePreswaldService

from .runner import ScriptRunner


logger = logging.getLogger(__name__)


class ServerPreswaldService(BasePreswaldService):
    """
    Main service class that orchestrates the application components.
    Acts as a facade to provide a simplified interface to the complex subsystem.
    """

    _instance = None
    _not_initialized_msg = (
        "ServerPreswaldService not initialized. Did you call start_server()?"
    )

    def __init__(self):
        super().__init__()

        # Initialize connection tracking
        self.connections = []  # Track connections for broadcasting
        self._connections: dict[str, Any] = {}  # TODO: deprecated

        # Branding management
        self.branding_manager = None  # set during server creation

        # Initialize session tracking
        self.websocket_connections: dict[str, WebSocket] = {}

    async def register_client(
        self, client_id: str, websocket: WebSocket
    ) -> ScriptRunner:
        """Register a new client connection and create its script runner"""
        try:
            logger.info(f"[WebSocket] New connection request from client: {client_id}")
            await websocket.accept()
            logger.info(f"[WebSocket] Connection accepted for client: {client_id}")
            
            # Store for broadcasting
            self.connections.append({"id": client_id, "socket": websocket})
            
            # Initialize with common setup
            runner = await self._register_common_client_setup(client_id, websocket)
            
            # Wait for initialization message from client
            try:
                init_message = await websocket.receive_json()
                logger.info(f"Received init message: {init_message}")
                
                # Check if this is an embed request
                if init_message.get("type") == "init" and init_message.get("embed_mode"):
                    # Set embed mode flag
                    self.embed_mode = True
                    
                    # If component_id is specified, we'll only send that component
                    component_id = init_message.get("component_id")
                    if component_id:
                        logger.info(f"Embed request for component: {component_id}")
                        
                        # Get the specific component
                        component = self.get_component(component_id)
                        
                        if component:
                            # Create a new components structure with just this component
                            filtered_components = {"rows": [[component]]}
                            await websocket.send_json({
                                "type": "components",
                                "components": filtered_components
                            })
                        else:
                            # Component not found
                            logger.warning(f"Component not found for embed: {component_id}")
                            await websocket.send_json({
                                "type": "error",
                                "content": {"message": f"Component '{component_id}' not found"}
                            })
                    else:
                        # No specific component requested, send all components
                        await self._broadcast_components(client_id=client_id)
            except Exception as e:
                logger.error(f"Error processing init message: {e}")
            
            # Broadcast new connection to all clients
            await self._broadcast_connections()
            
            return runner

        except WebSocketDisconnect:
            logger.error(f"[WebSocket] Client disconnected: {client_id}")
            # Clean up if registration fails
            if client_id in self.websocket_connections:
                self.websocket_connections.pop(client_id)
            if client_id in self.script_runners:
                runner = self.script_runners.pop(client_id)
                await runner.stop()
            # Remove from connections list
            self.connections = [c for c in self.connections if c.get("id") != client_id]
        except Exception as e:
            logger.error(f"Error registering client {client_id}: {e}")
            raise

    async def unregister_client(self, client_id: str):
        """Clean up resources for a disconnected client"""
        await super().unregister_client(client_id)
        
        # Remove from connections list
        self.connections = [conn for conn in self.connections if conn.get("id") != client_id]
        
        # Broadcast updated connections to all clients
        asyncio.create_task(self._broadcast_connections())  # noqa: RUF006

    async def _broadcast_connections(self):
        """Broadcast current connections to all clients"""
        try:
            connection_list = []
            # Use websocket_connections instead of deprecated connection_manager
            for client_id, websocket in self.websocket_connections.items():  # noqa: B007
                connection_info = {
                    "name": client_id,
                    "type": "WebSocket",
                    "details": f"Active WebSocket connection for client {client_id}",
                }
                connection_list.append(connection_info)

            # Broadcast to all connected clients
            for websocket in self.websocket_connections.values():
                try:
                    await websocket.send_json(
                        {"type": "connections_update", "connections": connection_list}
                    )
                except Exception as e:
                    logger.error(f"Error sending connection update to client: {e}")

        except Exception as e:
            logger.error(f"Error broadcasting connections: {e}")
            # Don't raise the exception to prevent disrupting the main flow

    async def _broadcast_components(self, client_id=None):
        """
        Broadcast component data to one or all clients
        
        Args:
            client_id: Optional client ID to send to. If None, sends to all clients.
        """
        try:
            # Get all components
            components = self.get_rendered_components()
            
            if client_id:
                # Send to specific client
                websocket = self.websocket_connections.get(client_id)
                if websocket:
                    await websocket.send_json({
                        "type": "components",
                        "components": components
                    })
            else:
                # Send to all clients
                for conn in self.connections:
                    try:
                        await conn["socket"].send_json({
                            "type": "components",
                            "components": components
                        })
                    except Exception as e:
                        logger.error(f"Error broadcasting components to {conn['id']}: {e}")
        except Exception as e:
            logger.error(f"Error broadcasting components: {e}")
