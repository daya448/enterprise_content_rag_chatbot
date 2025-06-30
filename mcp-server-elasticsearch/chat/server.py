from dotenv import load_dotenv
from fastmcp.server.openapi import RouteMap, RouteType

from elastic.mcp.fastmcp import ESFastMCPOpenAPI

load_dotenv()

# One can remap resources to be tools, or vice versa
custom_maps = [
    # Force all endpoints to be Tools
    RouteMap(methods=["GET"], pattern=r".*", route_type=RouteType.TOOL),
]
mcp = ESFastMCPOpenAPI(route_maps=custom_maps)


@mcp.tool(
    description=(
        "Search for documents ONLY in indices matching 'content-*' pattern. "
        "This tool automatically searches all content indices. "
        "Provide only the query body (e.g., {'query': {'match': {'field': 'value'}}})."
    )
)
async def search_content(body: dict) -> dict:
    """Search for documents in content indices (content-* pattern only).

    Args:
        body: Search query or aggregation query as a dictionary
    """
    uri = "resource://openapi/search-3"
    context = mcp.get_context()
    arguments = {"index": "content-*", "body": body}
    resource = await mcp._resource_manager.get_resource(uri, context=context)
    results = await resource.call_tool(arguments, context=context)
    return results


if __name__ == "__main__":
    # Initialize the client
    mcp.run(transport="sse", host="localhost", port=8000)
