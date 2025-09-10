import json
import sys
import asyncio
import websockets
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class MCPServer:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.connected_clients = set()

    async def handle_client(self, websocket):
        """Handle incoming WebSocket connections"""
        self.connected_clients.add(websocket)
        client_address = websocket.remote_address
        logger.info(f"Client connected from {client_address}")

        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_address} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def process_message(self, websocket, message: str):
        """Process incoming MCP messages"""
        try:
            data = json.loads(message)
            logger.info(f"Received message: {data}")

            # Handle different MCP message types
            message_type = data.get("method") or data.get("type")

            if message_type == "initialize":
                response = await self.handle_initialize(data)
            elif message_type == "tools/list":
                response = await self.handle_tools_list(data)
            elif message_type == "tools/call":
                response = await self.handle_tool_call(data)
            elif message_type == "resources/list":
                response = await self.handle_resources_list(data)
            elif message_type == "ping":
                response = await self.handle_ping(data)
            else:
                response = await self.handle_unknown(data)

            # Send response back to client
            await websocket.send(json.dumps(response))
            logger.info(f"Sent response: {response}")

        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            }
            await websocket.send(json.dumps(error_response))
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": data.get("id") if 'data' in locals() else None
            }
            await websocket.send(json.dumps(error_response))

    async def handle_initialize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialization request"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "Python MCP Server",
                    "version": "1.0.0"
                }
            },
            "id": data.get("id")
        }

    async def handle_tools_list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = [
            {
                "name": "get_time",
                "description": "Get current timestamp",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "echo",
                "description": "Echo back the provided message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            }
        ]

        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": data.get("id")
        }

    async def handle_tool_call(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_time":
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": f"Current time: {datetime.now().isoformat()}"
                    }
                ]
            }
        elif tool_name == "echo":
            message = arguments.get("message", "No message provided")
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": f"Echo: {message}"
                    }
                ]
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                "id": data.get("id")
            }

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": data.get("id")
        }

    async def handle_resources_list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = [
            {
                "uri": "file://example.txt",
                "name": "Example Resource",
                "description": "An example resource",
                "mimeType": "text/plain"
            }
        ]

        return {
            "jsonrpc": "2.0",
            "result": {"resources": resources},
            "id": data.get("id")
        }

    async def handle_ping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request"""
        return {
            "jsonrpc": "2.0",
            "result": {"pong": True},
            "id": data.get("id")
        }

    async def handle_unknown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown requests"""
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": data.get("id")
        }

    async def broadcast_message(self, message: Dict[str, Any]):
        """Send a message to all connected clients"""
        if self.connected_clients:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_str) for client in self.connected_clients],
                return_exceptions=True
            )

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")

        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"MCP Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever