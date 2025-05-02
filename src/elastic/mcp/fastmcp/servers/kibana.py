import warnings

from typing_extensions import override

from elastic.mcp.fastmcp.servers.elk import ELKFastMCPOpenAPI


class KibanaFastMCPOpenAPI(ELKFastMCPOpenAPI):
    """FastMCP OpenAPI server for Elasticsearch."""

    @override
    @property
    def openapi_default_url(self) -> str:
        """Default URL for the OpenAPI specification."""
        warnings.warn("Kibana's OpenAPI specification is malformed", UserWarning, stacklevel=2)
        return "https://www.elastic.co/docs/api/doc/kibana.yaml"

    @override
    @property
    def client_url_env(self) -> str:
        """Environment variable name for the ELK URL."""
        return "KIBANA_URL"
