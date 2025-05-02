from typing_extensions import override

from elastic.mcp.fastmcp.servers.elk import ELKFastMCPOpenAPI


class ESFastMCPOpenAPI(ELKFastMCPOpenAPI):
    """FastMCP OpenAPI server for Elasticsearch."""

    @override
    @property
    def openapi_default_url(self) -> str:
        """Default URL for the OpenAPI specification."""
        return "https://www.elastic.co/docs/api/doc/elasticsearch.yaml"

    @override
    @property
    def client_url_env(self) -> str:
        """Environment variable name for the ELK URL."""
        return "ELASTICSEARCH_URL"
