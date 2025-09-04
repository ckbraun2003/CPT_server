import asyncio
from server import MCPServer  # assuming your server code is in server.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    server = MCPServer(host="localhost", port=8080)
    await server.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP Server stopped manually")