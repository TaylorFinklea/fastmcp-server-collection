# FastMCP Server Collection

A collection of FastMCP servers for various APIs.

## Overview

FastMCP Server Collection provides a set of ready-to-use FastMCP servers that allow you to interact with various APIs through the Model Control Protocol (MCP). This makes it easy to integrate external services into MCP-based workflows.

## Installation

### Requirements

- Python 3.11
- uv (recommended) or pip

### Install from source

```bash
# Clone the repository
git clone https://github.com/TaylorFinklea/fastmcp-server-collection.git
cd fastmcp-server-collection

# Install with uv
uv pip install -e .

# Or with pip
# pip install -e .
```

## Usage

FastMCP Server Collection provides servers for different APIs. You can run a specific server using:

```bash
python -m fastmcp_server_collection -s <server_name>
```

For example, to run the Skyvern server:

```bash
python -m fastmcp_server_collection -s skyvern
```

## Available Servers

### Skyvern

A server for interacting with the Skyvern API. This server requires a Skyvern API key, which should be set in your environment variables or in a `.env` file in the project root.

Required environment variables:
- `SKYVERN_API_KEY`: Your Skyvern API key
- `SKYVERN_URL`: The base URL for the Skyvern API

## Development

### Adding new servers

1. Create a new Python file in the `fastmcp_server_collection/servers/` directory
2. Implement the necessary functionality using FastMCP
3. Ensure your file includes code that starts the FastMCP server when run directly
4. Update the server registry to include your new server

## Testing

REST2MCP uses pytest for testing. The tests are located in the `tests/` directory.

### Running tests

To run the tests, first install the test dependencies:

```bash
# Install with test dependencies
uv pip install -e ".[test]"
```

Then run the tests:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=fastmcp_server_collection
```

### Continuous Integration

This project uses GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/ci.yml`.

The CI pipeline:
- Runs on Python 3.11
- Checks code formatting with Black
- Runs tests with coverage reporting
- Uploads coverage reports to Codecov

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
