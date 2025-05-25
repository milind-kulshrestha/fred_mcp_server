"""
Configuration management for the FRED MCP server.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fred-config")

class Settings:
    """Configuration settings for the FRED MCP server."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # App information
        self.APP_NAME = os.getenv("FRED_APP_NAME", "fred-mcp-server")
        self.APP_VERSION = os.getenv("FRED_APP_VERSION", "1.0.0")
        
        # API configuration
        self.API_KEY = os.getenv("FRED_API_KEY", "")
        self.API_BASE_URL = os.getenv("FRED_API_ENDPOINT", "https://api.stlouisfed.org/fred")
        
        # Rate limiting
        self.RATE_LIMIT = int(os.getenv("FRED_RATE_LIMIT", "120"))  # requests per period
        self.RATE_LIMIT_PERIOD = int(os.getenv("FRED_RATE_LIMIT_PERIOD", "60"))  # period in seconds
        
        # Storage settings
        self.STORAGE_PATH = Path(os.getenv("FRED_STORAGE_PATH", "./data"))
        
        # Logging settings
        self.LOG_LEVEL = os.getenv("FRED_LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("FRED_LOG_FILE", "fred_mcp_server.log")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration settings."""
        if not self.API_KEY:
            logging.warning("FRED API key not provided. Set FRED_API_KEY environment variable.")
        
        # Create storage directory if it doesn't exist
        self.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
