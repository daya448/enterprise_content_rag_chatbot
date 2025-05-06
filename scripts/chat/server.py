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


if __name__ == "__main__":
    # Initialize the client
    mcp.run(transport="sse", host="localhost", port=8000)
