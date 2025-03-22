import logging
import os
import sys
import platform
from dataclasses import dataclass
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("DaVinciConnection")

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
            
            # Import commands module directly without relative imports
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from src.davinci_resolve_mcp.commands import execute_command
            return execute_command(self, command_type, params)
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise Exception(f"Error executing command {command_type}: {str(e)}")

# Global connection instance
davinci_connection = None

def get_davinci_connection():
    """Get or create the DaVinci connection"""
    global davinci_connection
    
    if not davinci_connection:
        davinci_connection = DaVinciConnection()
        davinci_connection.connect()
    
    return davinci_connection 