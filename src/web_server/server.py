from flask import Flask
import logging

from src.mcp_server.client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WEBServer:
    def __init__(self, mcp_path = "ws://localhost:8080"):
        self.app = Flask(__name__)
        self.mcp_client = MCPClient(mcp_path)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/")
        async def home():
            try:
                await self.mcp_client.connect()

                # Initialize connection
                response = await self.mcp_client.send_request("initialize")

            except Exception as e:
                logger.error(f"Error in client: {e}")
            finally:
                await self.mcp_client.close()
            return response


