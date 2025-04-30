# ML ES OpenAPI MCP server

[![ci.yml](https://github.com/elastic/mvp-mlops-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/elastic/mvp-mlops-platform/actions/workflows/ci.yml)

OpenAPI based MCP server.

# Installation

We use the package manager [Poetry](https://python-poetry.org/). Follow [these instructions](https://python-poetry.org/docs/#installation) to install it.

Install the virtual environment:
```bash
poetry install
```

Install [pre-commit hooks](https://pre-commit.com/):

```bash
poetry run invoke installs.pre-commit
```

# Tests

We use [pytest](https://docs.pytest.org/en/stable/) and [nox](https://nox.thea.codes/en/stable/) to run the tests:

To run the tests with the default Python and dependency versions:

```bash
poetry run invoke testing.test-default-versions
```

To run the tests with the dependency versions matrix:

```bash
poetry run invoke testing.test-matrix-versions
```

# Relevant links
- [SonarQube project](https://sonar.elastic.dev/dashboard?id=)
