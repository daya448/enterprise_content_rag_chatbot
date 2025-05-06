# ELK FastMCP server(s)

/!\ Experimental /!\

[![ci.yml](https://github.com/elastic/mvp-mlops-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/elastic/mvp-mlops-platform/actions/workflows/ci.yml)
![Powered by fastmcp](https://img.shields.io/badge/Powered%20by-fastmcp-blue)


Model Context Protocol (MCP) server for Elasticsearch built through the OpenAPI specification using [FastMCP](https://github.com/jlowin/fastmcp).


# Installation
We don't have a PyPI package yet, but you can install the package through `git+ssh`

```bash
pip install git+ssh://git@github.com/elastic/elastic-fastmcp-server.git
```

# Example:

Starting the server is as simple as
```python
from fastmcp.server.openapi import RouteMap, RouteType
from elastic.mcp.fastmcp import ESFastMCPOpenAPI

# One can remap resources to be tools, or vice versa
custom_maps = [
    # Force all endpoints to be Tools
    RouteMap(methods=["GET"], pattern=r".*", route_type=RouteType.TOOL),
]
mcp = ESFastMCPOpenAPI(route_maps=custom_maps)

if __name__ == "__main__":
    # Initialize the client
    mcp.run(transport="sse", host="localhost", port=8000)
```
Your credentials will be read from environment variables
```bash
ELASTICSEARCH_URL=https://<your cluster>:<your url>
ELASTIC_API_KEY=<your ES api key>
```

Head to [`scripts/chat`](scripts/chat) for a basic implementation example on how to spin up the server (`python server.py`) and a chat session (`python main.py`) using Anthropic Bedrock that you can modify to your own needs.

## Available Servers:

**Working**: ElasticSearch

**Planned**: Kibana, Logstash


# Developers

## Installation

We use the package manager [Poetry](https://python-poetry.org/). Follow [these instructions](https://python-poetry.org/docs/#installation) to install it.

Install the virtual environment:
```bash
poetry install
```

Install [pre-commit hooks](https://pre-commit.com/):

```bash
poetry run invoke installs.pre-commit
```

## Tests

We use [pytest](https://docs.pytest.org/en/stable/) and [nox](https://nox.thea.codes/en/stable/) to run the tests:

To run the tests with the default Python and dependency versions:

```bash
poetry run invoke testing.test-default-versions
```

To run the tests with the dependency versions matrix:

```bash
poetry run invoke testing.test-matrix-versions
```

## Relevant links
- [SonarQube project](https://sonar.elastic.dev/dashboard?id=)
