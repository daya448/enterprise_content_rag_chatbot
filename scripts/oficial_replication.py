import asyncio

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.server.openapi import RouteMap, RouteType

from ml_rd_mcp.servers import ELKFastMCPOpenAPI, ESFastMCPOpenAPI, KibanaFastMCPOpenAPI  # noqa: F401

load_dotenv()

# One can remap resources to be tools, or vice versa
custom_maps = [
    # Force all analytics endpoints to be Tools
    RouteMap(methods=["GET"], pattern=r".*_mapping.*", route_type=RouteType.TOOL)
]
mcp = ESFastMCPOpenAPI(route_maps=custom_maps)
client = Client(mcp)


# But we can also create custom tools to mimic the behavior of the rerouting
# or to add new functionality
@mcp.tool()
async def list_indices():
    """List all indices in the Elasticsearch cluster."""
    uri = "resource://openapi/cat-indices"
    context = mcp.get_context()
    resource = await mcp._resource_manager.get_resource(uri, context=context)
    indices = await resource.read(context=context)
    return indices


def shortprint(items):
    """Print the first 1000 characters of the response."""
    print(items[0].text[0:1000], "...")  # Print the first 100 characters of the response
    print("=" * 20)


async def main():
    """Here we are trying to mimic the current behavior without any implementation."""
    async with client:
        # Index an example document
        index = "mcp-test-index"
        user = {"id": "alebaro"}  # equivalent to doc {"user.id": "alebaro"}
        await client.call_tool(name="index", arguments={"index": index, "user": user})

        # Tool1: list-indices
        indices = await client.call_tool(name="list_indices", arguments={})  # Custom tool
        indices = await client.read_resource("resource://openapi/cat-indices")  # Native
        print("Indices:")
        shortprint(indices)

        # Tool2: get-mappings
        # We rerouted the mappings endpoints to be a tool instead of a resource.
        # We could use the resource directly if we hadn't.
        # mappings = await client.read_resource(f"resource://openapi/indices-get-mapping-1/{index}")
        mappings = await client.call_tool(name="indices-get-mapping-1", arguments={"index": index})
        print("Mappings:")
        shortprint(mappings)

        # Tool3: search
        query = {"match": {"user.id": "alebaro"}}
        search = await client.call_tool(name="search-3", arguments={"index": index, "query": query})
        print("Search:")
        shortprint(search)

        # Tool4: get_shards
        shards = await client.read_resource("resource://openapi/cat-shards")
        print("Shards:")
        shortprint(shards)


asyncio.run(main())
