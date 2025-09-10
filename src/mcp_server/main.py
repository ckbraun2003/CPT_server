import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from core.server import MCPServer

logger = logging.getLogger(__name__)


async def main(host="localhost", port=8080):
    server = MCPServer(host=host, port=port)
    await server.start_server()


def run_server(host="localhost", port=8080):
    """Synchronous wrapper to run the async server"""
    try:
        asyncio.run(main(host, port))
    except KeyboardInterrupt:
        print("Server stopped manually")

if __name__ == "__main__":
    host = "localhost"
    port = 8080
    run_server(host, port)