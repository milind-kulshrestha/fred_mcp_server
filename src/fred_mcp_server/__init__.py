"""
FRED MCP Server - Model Context Protocol server for FRED economic data.

This package provides a secure proxy interface to the Federal Reserve Economic Data (FRED)
API following the Model Context Protocol (MCP) specification.
"""

from .config import Settings

__version__ = "0.1.0"

__all__ = [
    "Settings",
]
