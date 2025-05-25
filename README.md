# FRED MCP Server

A Model Context Protocol (MCP) server for accessing and analyzing Federal Reserve Economic Data (FRED).

## Overview

This server provides access to Federal Reserve Economic Data (FRED) using the FRED API through the Model Context Protocol.

## Features

- **Economic Data Access**: Retrieve economic indicators and time series data from FRED
- **Data Visualization**: Generate charts and graphs of economic data
- **Trend Analysis**: Analyze economic trends over time
- **Comparative Analysis**: Compare multiple economic indicators
- **Metadata Access**: Get information about available economic series
- **Prompt Templates**: Use pre-defined prompt templates for common economic analysis tasks

## Installation

### Prerequisites

- Python 3.10 or higher
- A FRED API key (for the backend service)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/fred-mcp-server.git
cd fred-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
# Install with pip
pip install .

# Install with UV (recommended for exact dependency versions)
uv pip install .
```

## Configuration

The server can be configured using environment variables:

- `FRED_API_KEY`: Your FRED API key (required)
- `LOG_LEVEL`: Logging level (default: "INFO")
- `LOG_FILE`: Log file path (default: "fred_mcp_server.log")


## Usage

### Running the Server

```bash
# Run directly
python -m fred_mcp_server

# Or using the installed script
fred-mcp
```

### Using with Claude for Desktop

To use with Claude for Desktop, add this server to your Claude configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fred": {
      "command": "uv",
      "args": [
        "run",
        "-m",
        "fred_mcp_server"
      ],
      "cwd": "<PATH_TO_FRED_MCP_SERVER>/src",
      "env": {
        "FRED_API_KEY": "your_fred_api_key_here"
      }
    }
  }
}
```

**Notes:**
- Replace `<PATH_TO_FRED_MCP_SERVER>` with the absolute path to your fred directory
- You can use `"command": "uv"` with `"args": ["run", "-m", "fred_mcp_server"]` if using the uv package manager

**Note:** Replace `your_fred_api_key_here` with your actual FRED API key. You can obtain a free API key by registering at https://fred.stlouisfed.org/docs/api/api_key.html


## Demo

![FRED MCP Server Demo](demo.jpeg)

## Available Tools

All tools use a consistent `fred_` prefix for clear namespace management:

- `search_fred_series`: Search for economic data series by keywords or category
- `fred_get_series_data`: Retrieve time series data for a specific economic indicator
- `fred_get_series_metadata`: Get detailed metadata about a specific economic data series
- `fred_get_category_series`: List series in a specific FRED category
- `fred_get_releases`: Get economic data releases from FRED
- `fred_compare_series`: Compare multiple economic indicators over a specified time period
- `fred_calculate_statistics`: Calculate basic statistics for a FRED series
- `fred_detect_trends`: Identify trends in FRED economic data
- `analyze_economic_trends`: Analyze trends in economic indicators over time

## Available Prompts

- `economic-data-search`: How to effectively search for economic indicators
- `data-visualization-guide`: How to create and interpret economic data visualizations
- `trend-analysis-guide`: How to analyze trends in economic indicators
- `comparative-analysis`: How to perform comparative analysis of economic indicators
- `latest-data-analysis`: How to analyze the latest economic indicators

## License

MIT
