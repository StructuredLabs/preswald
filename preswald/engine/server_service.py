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

        # TODO: deprecated
        # Connection management
        self._connections: dict[str, Any] = {}

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

            return await self._register_common_client_setup(client_id, websocket)

        except WebSocketDisconnect:
            logger.error(f"[WebSocket] Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error registering client {client_id}: {e}")
            raise

    async def unregister_client(self, client_id: str):
        await super().unregister_client(client_id)
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
