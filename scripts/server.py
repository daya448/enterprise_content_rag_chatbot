import asyncio

from dotenv import load_dotenv
from fastmcp import Client

from ml_rd_mcp.servers import ESFastMCPOpenAPI

load_dotenv()

mcp = ESFastMCPOpenAPI()
client = Client(mcp)


async def list_tools():
    """List all available tools."""
    tools = await mcp.get_tools()
    print("Tools available:")
    for name, tool in tools.items():
        print(f"- {name}")
        if name == "index":
            print(f"  Description: {tool.description}")
            print(f"  Parameters: {tool.parameters}")


async def call_tool(name: str, **kwargs):
    """Call a tool with the given name and arguments."""
    async with client:
        result = await client.call_tool(name, kwargs)
        print(result)


index = "mcp-test-index"
body = {"user": {"id": "alebaro"}}

asyncio.run(list_tools())
asyncio.run(call_tool("index", index=index, body=body))
