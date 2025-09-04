import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from src.web_server.server import WEBServer

server = WEBServer()
app = server.app

async def main(path):
    config = Config()
    config.bind = [path]
    config.reload = True  # optional, for auto-reload during dev

    await serve(app, config)

if __name__ == "__main__":
    path = "0.0.0.0:5000"

    try:
        asyncio.run(main(path))
    except KeyboardInterrupt:
        print("Server stopped manually")