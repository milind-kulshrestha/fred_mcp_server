#!/usr/bin/env python3
"""
Fred MCP Server entry point.
"""
import asyncio
import sys
from fred_mcp_server.server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
