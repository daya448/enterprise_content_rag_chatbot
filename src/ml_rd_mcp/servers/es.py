import os

import httpx

from ml_rd_mcp.servers.elk import ELKFastMCPOpenAPI


class ESFastMCPOpenAPI(ELKFastMCPOpenAPI):
    """FastMCP OpenAPI server for Elasticsearch."""

    @property
    def openapi_default_url(self) -> str:
        """Default URL for the OpenAPI specification."""
        return "https://www.elastic.co/docs/api/doc/elasticsearch.yaml"

    def _get_default_client(self) -> httpx.AsyncClient:
        ELASTIC_URL = os.getenv("ELASTIC_URL")
        ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

        headers = {"Authorization": f"ApiKey {ELASTIC_API_KEY}"}
        return httpx.AsyncClient(
            base_url=ELASTIC_URL,
            headers=headers,
            verify=True,
        )
