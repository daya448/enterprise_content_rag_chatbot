import pytest
from typing_extensions import override

from elastic.mcp.fastmcp.servers import ELKFastMCPOpenAPI


class DummyFastMCPOpenAPIServer(ELKFastMCPOpenAPI):
    """Dummy FastMCP OpenAPI server for testing purposes."""

    @override
    @property
    def openapi_default_url(self) -> str:
        """Default URL for the OpenAPI specification."""
        return "http://localhost/openapi.json"

    @override
    @property
    def client_url_env(self) -> str:
        """Environment variable name for the ELK URL."""
        return "TEST_ELK_URL"


@pytest.fixture()
def dummy_openapi_spec():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Print Service", "version": "1.0.0"},
        "paths": {
            "/print": {
                "post": {
                    "summary": "Print an argument",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"arg": {"type": "string"}},
                                    "required": ["arg"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Argument printed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"message": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
    }


@pytest.fixture()
def dummy_mcp(dummy_openapi_spec):
    """Fixture for a dummy FastMCP OpenAPI server."""
    server = DummyFastMCPOpenAPIServer(openapi_spec=dummy_openapi_spec)
    return server
