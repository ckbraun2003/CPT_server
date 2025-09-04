import asyncio
from src.mcp_server.server import MCPServer  # assuming your server code is in server.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main(host="localhost", port=8080):
    server = MCPServer(host=host, port=port)
    await server.start_server()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080

    try:
        asyncio.run(main(host, port))
    except KeyboardInterrupt:
        logger.info("MCP Server stopped manually")