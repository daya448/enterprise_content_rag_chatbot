import json
from abc import ABC, abstractmethod
from typing import Optional, Union

import httpx
import yaml
from fastmcp.server.openapi import FastMCPOpenAPI


class ELKFastMCPOpenAPI(FastMCPOpenAPI, ABC):
    """FastMCP OpenAPI server for ELK stack services.

    Args:
        openapi_spec (str or dict, optional): OpenAPI specification URL or dictionary.
            If a string, it can be a URL or a path to a local file.
            If a dictionary, it should be the OpenAPI spec in JSON or YAML format.
        client (httpx.AsyncClient, optional): HTTP client for making requests.
            If not provided, a default client will be created using environment variables.
        **kwargs: Additional keyword arguments for FastMCPOpenAPI.

    """

    def __init__(
        self,
        openapi_spec: Optional[Union[str, dict]] = None,
        client: Optional[httpx.AsyncClient] = None,
        **kwargs,
    ):
        openapi_spec = self._load_openapi_spec(openapi_spec)
        client = client or self._get_default_client()

        super().__init__(
            openapi_spec=openapi_spec,
            client=client,
            **kwargs,
        )

    @property
    @abstractmethod
    def openapi_default_url(self) -> str:
        """Default URL for the OpenAPI specification."""

    def _load_openapi_spec(self, openapi_spec: Optional[Union[str, dict]]) -> dict:
        openapi_spec = openapi_spec or self.openapi_default_url
        if isinstance(openapi_spec, str):
            if openapi_spec.startswith("http"):
                response = httpx.get(openapi_spec)
                response.raise_for_status()
                return yaml.safe_load(response.text)
            if openapi_spec.endswith(".yaml"):
                with open(openapi_spec) as f:
                    return yaml.safe_load(f)
            if openapi_spec.endswith(".json"):
                with open(openapi_spec) as f:
                    return json.load(f)
        return openapi_spec

    @abstractmethod
    def _get_default_client(self) -> httpx.AsyncClient:
        """Create a default HTTP client for the OpenAPI server."""
