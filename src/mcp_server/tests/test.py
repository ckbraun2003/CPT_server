import asyncio
import logging

from src.web_server.clients.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = MCPClient("ws://localhost:8080")

    try:
        await client.connect()

        # Initialize connection
        init_resp = await client.send_request("initialize")
        # print("Initialize Response:", init_resp)

        # List tools
        tools_resp = await client.send_request("tools/list")
        # print("Tools List:", tools_resp)

        # Call echo tool
        echo_resp = await client.send_request("tools/call", {
            "name": "echo",
            "arguments": {"message": "Hello MCP!"}
        })
        # print("Echo Response:", echo_resp)

        # Call get_time tool
        time_resp = await client.send_request("tools/call", {
            "name": "get_time",
            "arguments": {}
        })
        # print("Time Response:", time_resp)

        # Ping server
        ping_resp = await client.send_request("ping")
        # print("Ping Response:", ping_resp)

    except Exception as e:
        logger.error(f"Error in client: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())