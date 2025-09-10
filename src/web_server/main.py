import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from hypercorn.asyncio import serve
from hypercorn.config import Config
from core.server import WEBServer

logger = logging.getLogger(__name__)

server = WEBServer()
app = server.app

async def main(path):
    config = Config()
    config.bind = [path]
    config.reload = True  # optional, for auto-reload during dev

    await serve(app, config)

def run_server(path="0.0.0.0:5000"):
    """Synchronous wrapper to run the async server"""
    try:
        asyncio.run(main(path))
    except KeyboardInterrupt:
        print("Server stopped manually")

if __name__ == "__main__":
    path = "0.0.0.0:5000"
    run_server(path)