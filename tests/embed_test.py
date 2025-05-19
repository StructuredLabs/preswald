import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from preswald.engine.server_service import ServerPreswaldService
from preswald.engine.base_service import BasePreswaldService


@pytest.fixture
def service():
    # Create a service instance for testing
    service = ServerPreswaldService()
    
    # Mock the _register_common_client_setup method to avoid actual script execution
    service._register_common_client_setup = AsyncMock(return_value=MagicMock())
    
    # Mock get_component method 
    mock_component = {"id": "test_component", "type": "text", "value": "Test Content"}
    service.get_component = MagicMock(return_value=mock_component)
    
    return service


@pytest.mark.asyncio
async def test_register_client_with_embed_mode(service):
    """Test client registration with embed mode"""
    
    # Create a mock WebSocket
    mock_websocket = AsyncMock()
    mock_websocket.receive_json = AsyncMock(return_value={
        "type": "init", 
        "embed_mode": True,
        "component_id": "test_component"
    })
    
    # Register the client
    await service.register_client("test_client", mock_websocket)
    
    # Verify that embed_mode was set
    assert service.embed_mode is True
    
    # Verify that the component was sent to the client
    mock_websocket.send_json.assert_any_call({
        "type": "components",
        "components": {"rows": [[{"id": "test_component", "type": "text", "value": "Test Content"}]]}
    })


@pytest.mark.asyncio
async def test_register_client_with_nonexistent_component(service):
    """Test client registration with a component ID that doesn't exist"""
    
    # Create a mock WebSocket
    mock_websocket = AsyncMock()
    mock_websocket.receive_json = AsyncMock(return_value={
        "type": "init", 
        "embed_mode": True,
        "component_id": "nonexistent_component"
    })
    
    # Mock get_component to return None for nonexistent component
    service.get_component = MagicMock(return_value=None)
    
    # Register the client
    await service.register_client("test_client", mock_websocket)
    
    # Verify that embed_mode was set
    assert service.embed_mode is True
    
    # Verify that an error message was sent to the client
    mock_websocket.send_json.assert_any_call({
        "type": "error",
        "content": {"message": "Component 'nonexistent_component' not found"}
    })


@pytest.mark.asyncio
async def test_broadcast_components(service):
    """Test broadcasting components to clients"""
    
    # Create mock WebSockets
    mock_websocket1 = AsyncMock()
    mock_websocket2 = AsyncMock()
    
    # Add mock connections
    service.connections = [
        {"id": "client1", "socket": mock_websocket1},
        {"id": "client2", "socket": mock_websocket2}
    ]
    
    # Mock get_rendered_components
    mock_components = {"rows": [[{"id": "test_component", "type": "text", "value": "Test Content"}]]}
    service.get_rendered_components = MagicMock(return_value=mock_components)
    
    # Broadcast to all clients
    await service._broadcast_components()
    
    # Verify that both clients received the components
    mock_websocket1.send_json.assert_called_with({
        "type": "components",
        "components": mock_components
    })
    
    mock_websocket2.send_json.assert_called_with({
        "type": "components",
        "components": mock_components
    })


@pytest.mark.asyncio
async def test_broadcast_components_to_specific_client(service):
    """Test broadcasting components to a specific client"""
    
    # Create mock WebSocket
    mock_websocket = AsyncMock()
    
    # Add the client ID to websocket_connections
    service.websocket_connections = {"client1": mock_websocket}
    
    # Mock get_rendered_components
    mock_components = {"rows": [[{"id": "test_component", "type": "text", "value": "Test Content"}]]}
    service.get_rendered_components = MagicMock(return_value=mock_components)
    
    # Broadcast to specific client
    await service._broadcast_components(client_id="client1")
    
    # Verify that the client received the components
    mock_websocket.send_json.assert_called_with({
        "type": "components",
        "components": mock_components
    })


@pytest.mark.asyncio
async def test_unregister_client(service):
    """Test unregistering a client"""
    
    # Create mock websocket connections and connections list
    mock_websocket = AsyncMock()
    service.websocket_connections = {"client1": mock_websocket}
    service.connections = [{"id": "client1", "socket": mock_websocket}]
    
    # Mock the super().unregister_client method 
    with patch.object(BasePreswaldService, 'unregister_client', AsyncMock()) as mock_super:
        # Mock the _broadcast_connections method
        service._broadcast_connections = AsyncMock()
        
        # Unregister the client
        await service.unregister_client("client1")
        
        # Verify that the super method was called
        mock_super.assert_called_once_with("client1")
        
        # Verify that the client was removed from the connections list
        assert len(service.connections) == 0
        
        # Verify that _broadcast_connections was called
        assert service._broadcast_connections.called 