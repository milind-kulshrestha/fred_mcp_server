"""
Tool implementations for the FRED MCP server.
"""
# Import direct tool definitions that match the server.py imports
from .search_tools import search_series_tool
from .data_tools import get_series_data_tool, get_series_metadata_tool, get_category_series_tool, get_releases_tool
from .analysis_tools import compare_series_tool, calculate_statistics_tool, detect_trends_tool

# Import tool handlers
from .search_tools import handle_search_series
from .data_tools import handle_get_series_data, handle_get_series_metadata, handle_get_category_series, handle_get_releases
from .analysis_tools import handle_compare_series, handle_calculate_statistics, handle_detect_trends

__all__ = [
    # Tool definitions
    "search_series_tool",
    "get_series_data_tool",
    "get_series_metadata_tool",
    "get_category_series_tool",
    "get_releases_tool",
    "compare_series_tool",
    "calculate_statistics_tool",
    "detect_trends_tool",
    
    # Tool handlers
    "handle_search_series",
    "handle_get_series_data",
    "handle_get_series_metadata",
    "handle_get_category_series",
    "handle_get_releases",
    "handle_compare_series",
    "handle_calculate_statistics",
    "handle_detect_trends",
]
