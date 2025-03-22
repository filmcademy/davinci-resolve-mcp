import json
import logging
import sys
import os
from mcp.server.fastmcp import Context

# Configure logging
logger = logging.getLogger("DaVinciMCPTools")

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import connection functionality using absolute imports
from src.davinci_resolve_mcp.connection import get_davinci_connection

def register_tools(mcp):
    """Register all MCP tools with the FastMCP instance"""
    
    @mcp.tool()
    def get_project_info(ctx: Context) -> str:
        """Get information about the current DaVinci Resolve project"""
        try:
            connection = get_davinci_connection()
            result = connection.execute_command("get_project_info")
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_timeline_info(ctx: Context, timeline_name: str = None) -> str:
        """
        Get information about a specific timeline or the current timeline
        
        Args:
            timeline_name: The name of the timeline to get info on (optional, uses current timeline if not specified)
        """
        try:
            connection = get_davinci_connection()
            result = connection.execute_command("get_timeline_info", {"name": timeline_name})
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def create_timeline(
        ctx: Context,
        name: str,
        width: int = 1920,
        height: int = 1080,
        frame_rate: float = 24.0,
        set_as_current: bool = True
    ) -> str:
        """
        Create a new timeline in the current project
        
        Args:
            name: The name of the new timeline
            width: The width of the timeline in pixels (default: 1920)
            height: The height of the timeline in pixels (default: 1080)
            frame_rate: The frame rate of the timeline (default: 24.0)
            set_as_current: Whether to set the new timeline as the current timeline (default: True)
        """
        try:
            connection = get_davinci_connection()
            result = connection.execute_command("create_timeline", {
                "name": name,
                "width": width,
                "height": height,
                "frame_rate": frame_rate,
                "set_as_current": set_as_current
            })
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def execute_davinci_resolve_script(ctx: Context, code: str) -> str:
        """
        Execute arbitrary Python code in the DaVinci Resolve context
        
        Args:
            code: The Python code to execute
        """
        try:
            connection = get_davinci_connection()
            result = connection.execute_command("execute_script", {"code": code})
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
            
    # Additional tools can be added here for the other command types
    
    @mcp.prompt()
    def video_editing_strategy() -> str:
        """Prompt to help Claude understand how to use the DaVinci Resolve API"""
        return """
        You have access to DaVinci Resolve's powerful video editing and color grading capabilities through the Model Context Protocol.
        
        To work with DaVinci Resolve, you can use the following general approach:
        
        1. Get information about the current project with `get_project_info()`
        2. Use the timeline tools to create, modify or edit timelines
        3. Add media, transitions, effects, and markers
        4. Apply color grades to clips
        5. Export the final video
        
        You can also execute arbitrary Python code that uses the DaVinci Resolve API with `execute_davinci_resolve_script()`
        if you need more advanced functionality.
        
        Remember that all changes take place in the running DaVinci Resolve application, 
        and the user will see these changes happening in real-time.
        """ 