import asyncio

from dotenv import load_dotenv
from fastmcp import Client

from ml_rd_mcp.servers import ELKFastMCPOpenAPI, ESFastMCPOpenAPI, KibanaFastMCPOpenAPI  # noqa: F401

load_dotenv()

mcps = {
    "es": ESFastMCPOpenAPI(),
    # "kibana":KibanaFastMCPOpenAPI()
}

clients = {k: Client(mcp) for k, mcp in mcps.items()}


async def list_tools(mcp: ELKFastMCPOpenAPI):
    """List all available tools."""
    tools = await mcp.get_tools()
    print("Tools available:")
    for name, tool in tools.items():
        print(f"- {name}")
        if name == "index":
            print(f"  Description: {tool.description}")
            print(f"  Parameters: {tool.parameters}")


async def call_tool(client: Client, name: str, **kwargs):
    """Call a tool with the given name and arguments."""
    async with client:
        result = await client.call_tool(name, kwargs)
        print(result)


# Elasticsearch example

index = "mcp-test-index"
body = {"user": {"id": "alebaro"}}
asyncio.run(list_tools(mcp=mcps["es"]))
asyncio.run(call_tool(client=clients["es"], name="index", index=index, body=body))
