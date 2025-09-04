import websockets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self, uri: str = "ws://localhost:8080"):
        self.uri = uri
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        """Establish WebSocket connection to MCP server"""
        logger.info(f"Connecting to MCP server at {self.uri}")
        self.websocket = await websockets.connect(self.uri)
        logger.info("Connected to MCP server")

    async def send_request(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request and wait for response"""
        if not self.websocket:
            raise ConnectionError("Client is not connected to the server.")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        await self.websocket.send(json.dumps(request))
        logger.info(f"Sent request: {request}")

        # Wait for server response
        response = await self.websocket.recv()
        logger.info(f"Received response: {response}")
        return json.loads(response)

    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from MCP server")