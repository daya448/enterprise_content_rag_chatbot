import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from elastic.mcp.fastmcp.servers import ELKFastMCPOpenAPI


@pytest.fixture
def elk_mcp():
    """Fixture for creating a dummy ELKFastMCPOpenAPI instance."""
    return MagicMock(spec=ELKFastMCPOpenAPI)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/openapi.json",
        "http://localhost/openapi.yaml",
    ],
)
def test_load_openapi_http(
    url: str,
    elk_mcp: ELKFastMCPOpenAPI,
    dummy_openapi_spec: dict,
):
    response = httpx.Response(
        status_code=200,
        content=json.dumps(dummy_openapi_spec).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", url),
    )
    with patch("elastic.mcp.fastmcp.servers.elk.httpx.get", return_value=response):
        loaded = ELKFastMCPOpenAPI._load_openapi_spec(elk_mcp, url)
        assert loaded == dummy_openapi_spec


@pytest.mark.parametrize(
    "file",
    [
        "openapi.json",
        "openapi.yaml",
    ],
)
def test_load_openapi_local(
    file: str,
    elk_mcp: ELKFastMCPOpenAPI,
    dummy_openapi_spec: dict,
    tmp_path: Path,
):
    yaml_path = tmp_path / file
    yaml_path.write_text(json.dumps(dummy_openapi_spec))
    loaded = ELKFastMCPOpenAPI._load_openapi_spec(elk_mcp, yaml_path)
    assert loaded == dummy_openapi_spec


def test_get_default_client(elk_mcp: ELKFastMCPOpenAPI):
    """Test the default client creation."""
    ENV_URL = "TEST_ELK_URL"
    ENV_API = "TEST_ELASTIC_API_KEY"

    url = "http://localhost:9200"
    api_key = "test_api_key"
    elk_mcp.client_url_env = ENV_URL
    elk_mcp.client_api_key_env = ENV_API

    os_environ = {
        ENV_URL: url,
        ENV_API: api_key,
    }
    with patch.dict("os.environ", os_environ):
        client = ELKFastMCPOpenAPI._get_default_client(elk_mcp)
        assert client.base_url == "http://localhost:9200"
        assert client.headers["Authorization"] == f"ApiKey {api_key}"
