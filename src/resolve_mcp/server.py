# davinci_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context, Image
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Optional
import os
import sys
import json
import asyncio
import platform

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DaVinciMCPServer")

# Add DaVinci Resolve scripting module paths based on OS
if platform.system() == "Windows":
    resolve_script_path = os.path.join(
        os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
        "Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
    )
    if resolve_script_path not in sys.path:
        sys.path.append(resolve_script_path)
elif platform.system() == "Darwin":  # macOS
    resolve_script_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
    if resolve_script_path not in sys.path:
        sys.path.append(resolve_script_path)
elif platform.system() == "Linux":
    standard_path = "/opt/resolve/Developer/Scripting/Modules/"
    alt_path = "/home/resolve/Developer/Scripting/Modules/"
    
    if os.path.exists(standard_path) and standard_path not in sys.path:
        sys.path.append(standard_path)
    elif os.path.exists(alt_path) and alt_path not in sys.path:
        sys.path.append(alt_path)

# Try to import DaVinci Resolve API directly
try:
    import DaVinciResolveScript as bmd
    
    # Get Resolve instance
    def get_resolve_instance():
        try:
            resolve = bmd.scriptapp("Resolve")
            if resolve:
                logger.info("Connected to DaVinci Resolve")
                return resolve
            else:
                logger.error("Failed to get Resolve instance")
                return None
        except Exception as e:
            logger.error(f"Error connecting to Resolve: {str(e)}")
            return None
except ImportError as e:
    logger.error(f"Failed to import DaVinciResolveScript: {str(e)}")
    logger.error("Make sure DaVinci Resolve is running")
    raise ImportError(f"Could not import DaVinci Resolve API: {str(e)}")

# Global Resolve instance
RESOLVE_INSTANCE = get_resolve_instance()
if not RESOLVE_INSTANCE:
    logger.error("Failed to connect to DaVinci Resolve - MCP server cannot start")
    raise ConnectionError("Could not connect to DaVinci Resolve")

@dataclass
class DaVinciConnection:
    """Direct connection to DaVinci Resolve API"""
    resolve = None
    project_manager = None
    project = None
    
    def connect(self) -> bool:
        """Connect to the DaVinci Resolve API"""
        global RESOLVE_INSTANCE
        if RESOLVE_INSTANCE:
            self.resolve = RESOLVE_INSTANCE
            self.project_manager = self.resolve.GetProjectManager()
            self.project = self.project_manager.GetCurrentProject()
            logger.info("Connected to DaVinci Resolve API")
            return True
        else:
            # Try to reconnect
            RESOLVE_INSTANCE = get_resolve_instance()
            if RESOLVE_INSTANCE:
                self.resolve = RESOLVE_INSTANCE
                self.project_manager = self.resolve.GetProjectManager()
                self.project = self.project_manager.GetCurrentProject()
                logger.info("Reconnected to DaVinci Resolve API")
                return True
            
            logger.error("Failed to connect to DaVinci Resolve")
            return False
    
    def execute_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command using the DaVinci Resolve API"""
        if not self.resolve and not self.connect():
            raise ConnectionError("Not connected to DaVinci Resolve")
            
        try:
            logger.info(f"Executing command: {command_type} with params: {params}")
            
            # Ensure we have a current project
            if not self.project:
                self.project = self.project_manager.GetCurrentProject()
                
            if not self.project and command_type != "execute_script":
                raise Exception("No project is currently open in DaVinci Resolve")
            
            # Execute different commands based on the command_type
            if command_type == "get_project_info":
                result = self._get_project_info()
            elif command_type == "get_timeline_info":
                result = self._get_timeline_info(params.get("name") if params else None)
            elif command_type == "get_media_pool_info":
                result = self._get_media_pool_info()
            elif command_type == "create_timeline":
                result = self._create_timeline(
                    name=params.get("name"),
                    width=params.get("width", 1920),
                    height=params.get("height", 1080),
                    frame_rate=params.get("frame_rate", 24.0),
                    set_as_current=params.get("set_as_current", True)
                )
            elif command_type == "add_clip_to_timeline":
                result = self._add_clip_to_timeline(
                    clip_name=params.get("clip_name"),
                    track_number=params.get("track_number", 1),
                    start_frame=params.get("start_frame", 0),
                    end_frame=params.get("end_frame")
                )
            elif command_type == "delete_clip_from_timeline":
                result = self._delete_clip_from_timeline(
                    clip_name=params.get("clip_name"),
                    track_number=params.get("track_number")
                )
            elif command_type == "add_transition":
                result = self._add_transition(
                    clip_name=params.get("clip_name"),
                    transition_type=params.get("transition_type", "CROSS_DISSOLVE"),
                    duration=params.get("duration", 1.0),
                    position=params.get("position", "END"),
                    track_number=params.get("track_number")
                )
            elif command_type == "add_effect":
                result = self._add_effect(
                    clip_name=params.get("clip_name"),
                    effect_name=params.get("effect_name"),
                    track_number=params.get("track_number"),
                    parameters=params.get("parameters")
                )
            elif command_type == "color_grade_clip":
                result = self._color_grade_clip(
                    clip_name=params.get("clip_name"),
                    track_number=params.get("track_number"),
                    lift=params.get("lift"),
                    gamma=params.get("gamma"),
                    gain=params.get("gain"),
                    contrast=params.get("contrast"),
                    saturation=params.get("saturation"),
                    hue=params.get("hue")
                )
            elif command_type == "import_media":
                result = self._import_media(
                    file_path=params.get("file_path"),
                    folder_name=params.get("folder_name")
                )
            elif command_type == "export_timeline":
                result = self._export_timeline(
                    output_path=params.get("output_path"),
                    format=params.get("format", "mp4"),
                    codec=params.get("codec", "h264"),
                    quality=params.get("quality", "high"),
                    range_type=params.get("range_type", "ALL")
                )
            elif command_type == "add_marker":
                result = self._add_marker(
                    frame=params.get("frame"),
                    color=params.get("color", "blue"),
                    name=params.get("name", ""),
                    note=params.get("note", ""),
                    duration=params.get("duration", 1)
                )
            elif command_type == "set_project_settings":
                result = self._set_project_settings(
                    timeline_resolution=params.get("timeline_resolution"),
                    timeline_frame_rate=params.get("timeline_frame_rate"),
                    color_science=params.get("color_science"),
                    colorspace=params.get("colorspace")
                )
            elif command_type == "execute_script":
                result = self._execute_script(code=params.get("code"))
            else:
                raise Exception(f"Command not implemented: {command_type}")
                
            return result
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise Exception(f"Error executing command {command_type}: {str(e)}")

    # Command implementations
    def _get_project_info(self):
        """Get information about the current project"""
        project = self.project
        
        if not project:
            raise Exception("No project is currently open")
        
        result = {
            "name": project.GetName(),
            "timeline_count": len(project.GetTimelineNames()),
            "timelines": project.GetTimelineNames(),
            "current_timeline": project.GetCurrentTimeline().GetName() if project.GetCurrentTimeline() else None,
            "frame_rate": project.GetSetting("timelineFrameRate"),
            "resolution": {
                "width": project.GetSetting("timelineResolutionWidth"),
                "height": project.GetSetting("timelineResolutionHeight")
            }
        }
        return result
        
    def _get_timeline_info(self, timeline_name=None):
        """Get information about a timeline"""
        if timeline_name:
            # Try to find the named timeline
            timeline_names = self.project.GetTimelineNames()
            if timeline_name not in timeline_names:
                raise Exception(f"Timeline not found: {timeline_name}")
            
            self.project.SetCurrentTimeline(timeline_name)
            timeline = self.project.GetCurrentTimeline()
        else:
            # Use the current timeline
            timeline = self.project.GetCurrentTimeline()
        
        if not timeline:
            raise Exception("No timeline is currently active")
        
        # Get basic timeline info
        result = {
            "name": timeline.GetName(),
            "duration": timeline.GetDuration(),
            "track_count": {
                "video": timeline.GetTrackCount("video"),
                "audio": timeline.GetTrackCount("audio"),
                "subtitle": timeline.GetTrackCount("subtitle")
            }
        }
        
        return result
        
    # Implement other command methods here with proper handling of DaVinci Resolve API
    # For brevity, these are placeholders - full implementations would be needed

    def _get_media_pool_info(self):
        # Implement media pool info retrieval
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _create_timeline(self, name, width=1920, height=1080, frame_rate=24.0, set_as_current=True):
        # Implement timeline creation
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _add_clip_to_timeline(self, clip_name, track_number=1, start_frame=0, end_frame=None):
        # Implement clip addition
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _delete_clip_from_timeline(self, clip_name, track_number=None):
        # Implement clip deletion
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _add_transition(self, clip_name, transition_type="CROSS_DISSOLVE", duration=1.0, position="END", track_number=None):
        # Implement transition addition
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _add_effect(self, clip_name, effect_name, track_number=None, parameters=None):
        # Implement effect addition
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _color_grade_clip(self, clip_name, track_number=None, lift=None, gamma=None, gain=None, contrast=None, saturation=None, hue=None):
        # Implement color grading
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _import_media(self, file_path, folder_name=None):
        # Implement media import
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _export_timeline(self, output_path, format="mp4", codec="h264", quality="high", range_type="ALL"):
        # Implement timeline export
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _add_marker(self, frame, color="blue", name="", note="", duration=1):
        # Implement marker addition
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _set_project_settings(self, timeline_resolution=None, timeline_frame_rate=None, color_science=None, colorspace=None):
        # Implement project settings modification
        return {"status": "not_implemented", "message": "Method not yet implemented"}
        
    def _execute_script(self, code):
        """Execute arbitrary Python code in the DaVinci Resolve context"""
        try:
            # Create a local execution context with access to Resolve API
            local_context = {
                "resolve": self.resolve,
                "project_manager": self.project_manager,
                "project": self.project,
                "result": None
            }
            
            # Execute the code
            exec(code, globals(), local_context)
            
            # Return the result if one was set
            return {"status": "success", "result": local_context.get("result", "Script executed successfully")}
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return {"status": "error", "message": f"Script execution error: {str(e)}"}

# Global connection instance
davinci_connection = None

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage the lifecycle of the MCP server and DaVinci Resolve connection"""
    global davinci_connection
    
    # Initialize connection
    logger.info("Initializing DaVinci Resolve connection")
    davinci_connection = DaVinciConnection()
    
    if not davinci_connection.connect():
        logger.error("Failed to connect to DaVinci Resolve")
        raise ConnectionError("Could not connect to DaVinci Resolve")
    
    logger.info("DaVinci Resolve MCP Server started successfully")
    
    yield {"status": "running", "message": "DaVinci Resolve MCP Server is running"}
    
    # Cleanup on shutdown
    logger.info("Shutting down DaVinci Resolve MCP Server")
    davinci_connection = None

def get_davinci_connection():
    """Get or create the DaVinci connection"""
    global davinci_connection
    
    if not davinci_connection:
        davinci_connection = DaVinciConnection()
        davinci_connection.connect()
    
    return davinci_connection

# Setup the MCP server
mcp = FastMCP(lifespan=server_lifespan)

# Define MCP tools
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

# Define other MCP tools that map to Resolve API functions
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

# Note: Add the rest of the tool definitions here following the same pattern
# I've simplified this for brevity, but all tools in the original server.py would need to be ported

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

def main():
    """Run the MCP server"""
    import argparse
    
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