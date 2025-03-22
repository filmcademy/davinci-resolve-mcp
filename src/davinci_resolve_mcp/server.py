"""DaVinci Resolve MCP Server

This module provides a Model Context Protocol (MCP) server that connects to DaVinci Resolve
and exposes its functionality through a clean API.
"""
import logging
import sys
import os
import argparse
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DaVinciMCPServer")

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import connection management using absolute imports
from src.davinci_resolve_mcp.connection import (
    get_davinci_connection,
    davinci_connection
)

# Import tools registration
from src.davinci_resolve_mcp.tools import register_tools

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage the lifecycle of the MCP server and DaVinci Resolve connection"""
    
    # Initialize connection
    logger.info("Initializing DaVinci Resolve connection")
    
    if not get_davinci_connection().connect():
        logger.error("Failed to connect to DaVinci Resolve")
        raise ConnectionError("Could not connect to DaVinci Resolve")
    
    logger.info("DaVinci Resolve MCP Server started successfully")
    
    yield {"status": "running", "message": "DaVinci Resolve MCP Server is running"}
    
    # Cleanup on shutdown
    logger.info("Shutting down DaVinci Resolve MCP Server")

# Setup the MCP server
mcp = FastMCP(lifespan=server_lifespan)

# Register all tools
register_tools(mcp)

def main():
    """Run the MCP server"""
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=9877, help="Port to listen on")
    args = parser.parse_args()
    
    logger.info(f"Starting DaVinci Resolve MCP Server on {args.host}:{args.port}")
    
    # Note: FastMCP.run() doesn't accept host/port arguments
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 