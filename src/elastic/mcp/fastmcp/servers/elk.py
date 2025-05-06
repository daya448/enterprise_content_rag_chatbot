import json
import os
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

    @property
    @abstractmethod
    def client_url_env(self) -> str:
        """Environment variable name for the ELK URL."""

    @property
    def client_api_key_env(self) -> str:
        """Environment variable name for the ELK API key."""
        return "ELASTIC_API_KEY"

    def _load_openapi_spec(self, openapi_spec: Optional[Union[str, dict]]) -> dict:
        openapi_spec = openapi_spec or self.openapi_default_url
        if not isinstance(openapi_spec, dict):
            openapi_spec = str(openapi_spec)

        is_str = isinstance(openapi_spec, str)
        is_yaml = is_str and (openapi_spec.endswith((".yaml", ".yml")))
        is_json = is_str and openapi_spec.endswith(".json")

        if isinstance(openapi_spec, str):
            if openapi_spec.startswith("http"):
                response = httpx.get(openapi_spec)
                response.raise_for_status()
                if is_yaml:
                    return yaml.safe_load(response.text)
                if is_json:
                    return response.json()
            if is_yaml:
                with open(openapi_spec) as f:
                    return yaml.safe_load(f)
            if is_json:
                with open(openapi_spec) as f:
                    return json.load(f)
        return openapi_spec

    def _get_default_client(self) -> httpx.AsyncClient:
        ELASTIC_URL = os.getenv(self.client_url_env)
        ELASTIC_API_KEY = os.getenv(self.client_api_key_env)

        headers = {"Authorization": f"ApiKey {ELASTIC_API_KEY}"}
        return httpx.AsyncClient(
            base_url=ELASTIC_URL,
            headers=headers,
            verify=True,
        )
