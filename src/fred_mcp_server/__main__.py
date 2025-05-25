"""
Main entry point for running the FRED MCP server.

Example usage:
    python -m fred_mcp_server

This module sets up a simple HTTP server that implements the MCP protocol
for FRED economic data.
"""
import os
import sys
import logging
import argparse
import asyncio
from typing import Dict, Any, Optional

from .server import main as start_server
from .config import Settings

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)