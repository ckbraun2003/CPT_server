import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from server import app   # <-- your Flask app lives in server.py

async def main():
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    config.reload = True  # optional, for auto-reload during dev

    await serve(app, config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped manually")