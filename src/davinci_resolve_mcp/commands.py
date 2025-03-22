import logging
import sys
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("DaVinciCommands")

# Make this file runnable directly if needed
if __name__ == "__main__":
    # Add the project root to the path if running directly
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def execute_command(connection, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a command using the DaVinci Resolve API"""
    if params is None:
        params = {}
        
    # Execute different commands based on the command_type
    if command_type == "get_project_info":
        result = get_project_info(connection)
    elif command_type == "get_timeline_info":
        result = get_timeline_info(connection, params.get("name"))
    elif command_type == "get_media_pool_info":
        result = get_media_pool_info(connection)
    elif command_type == "create_timeline":
        result = create_timeline(
            connection,
            name=params.get("name"),
            width=params.get("width", 1920),
            height=params.get("height", 1080),
            frame_rate=params.get("frame_rate", 24.0),
            set_as_current=params.get("set_as_current", True)
        )
    elif command_type == "add_clip_to_timeline":
        result = add_clip_to_timeline(
            connection,
            clip_name=params.get("clip_name"),
            track_number=params.get("track_number", 1),
            start_frame=params.get("start_frame", 0),
            end_frame=params.get("end_frame")
        )
    elif command_type == "delete_clip_from_timeline":
        result = delete_clip_from_timeline(
            connection,
            clip_name=params.get("clip_name"),
            track_number=params.get("track_number")
        )
    elif command_type == "add_transition":
        result = add_transition(
            connection,
            clip_name=params.get("clip_name"),
            transition_type=params.get("transition_type", "CROSS_DISSOLVE"),
            duration=params.get("duration", 1.0),
            position=params.get("position", "END"),
            track_number=params.get("track_number")
        )
    elif command_type == "add_effect":
        result = add_effect(
            connection,
            clip_name=params.get("clip_name"),
            effect_name=params.get("effect_name"),
            track_number=params.get("track_number"),
            parameters=params.get("parameters")
        )
    elif command_type == "color_grade_clip":
        result = color_grade_clip(
            connection,
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
        result = import_media(
            connection,
            file_path=params.get("file_path"),
            folder_name=params.get("folder_name")
        )
    elif command_type == "export_timeline":
        result = export_timeline(
            connection,
            output_path=params.get("output_path"),
            format=params.get("format", "mp4"),
            codec=params.get("codec", "h264"),
            quality=params.get("quality", "high"),
            range_type=params.get("range_type", "ALL")
        )
    elif command_type == "add_marker":
        result = add_marker(
            connection,
            frame=params.get("frame"),
            color=params.get("color", "blue"),
            name=params.get("name", ""),
            note=params.get("note", ""),
            duration=params.get("duration", 1)
        )
    elif command_type == "set_project_settings":
        result = set_project_settings(
            connection,
            timeline_resolution=params.get("timeline_resolution"),
            timeline_frame_rate=params.get("timeline_frame_rate"),
            color_science=params.get("color_science"),
            colorspace=params.get("colorspace")
        )
    elif command_type == "execute_script":
        result = execute_script(connection, code=params.get("code"))
    else:
        raise Exception(f"Command not implemented: {command_type}")
            
    return result

def get_project_info(connection):
    """Get information about the current project"""
    project = connection.project
    
    if not project:
        raise Exception("No project is currently open")
    
    # Get timeline count using the correct API method
    try:
        timeline_count = project.GetTimelineCount()
    except Exception as e:
        logger.error(f"Error in GetTimelineCount: {str(e)}")
        timeline_count = 0
    
    # Get all timelines by index
    timelines = []
    try:
        for i in range(1, timeline_count + 1):  # API indexes start at 1
            timeline = project.GetTimelineByIndex(i)
            if timeline:
                timelines.append(timeline.GetName())
    except Exception as e:
        logger.error(f"Error getting timelines by index: {str(e)}")
        
    try:
        current_timeline = project.GetCurrentTimeline()
        current_timeline_name = current_timeline.GetName() if current_timeline else None
    except Exception as e:
        logger.error(f"Error in GetCurrentTimeline: {str(e)}")
        current_timeline_name = None
        
    try:
        frame_rate = project.GetSetting("timelineFrameRate") 
    except Exception as e:
        logger.error(f"Error in GetSetting timelineFrameRate: {str(e)}")
        frame_rate = None
        
    try:
        width = project.GetSetting("timelineResolutionWidth")
        height = project.GetSetting("timelineResolutionHeight")
    except Exception as e:
        logger.error(f"Error in GetSetting resolution: {str(e)}")
        width = height = None
    
    # Return a more robust result that handles potential errors
    result = {
        "name": project.GetName(),
        "timeline_count": timeline_count,
        "timelines": timelines,
        "current_timeline": current_timeline_name,
        "frame_rate": frame_rate,
        "resolution": {
            "width": width,
            "height": height
        } if width and height else {}
    }
    return result
    
def get_timeline_info(connection, timeline_name=None):
    """Get information about a timeline"""
    if timeline_name:
        # Try to find the named timeline
        timeline_count = connection.project.GetTimelineCount()
        found_timeline = None
        
        # Search for the timeline by name
        for i in range(1, timeline_count + 1):
            timeline = connection.project.GetTimelineByIndex(i)
            if timeline and timeline.GetName() == timeline_name:
                found_timeline = timeline
                break
        
        if not found_timeline:
            raise Exception(f"Timeline not found: {timeline_name}")
        
        connection.project.SetCurrentTimeline(timeline_name)
        timeline = connection.project.GetCurrentTimeline()
    else:
        # Use the current timeline
        timeline = connection.project.GetCurrentTimeline()
    
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

# Command implementations with placeholders for not yet implemented features
def get_media_pool_info(connection):
    # Implement media pool info retrieval
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def create_timeline(connection, name, width=1920, height=1080, frame_rate=24.0, set_as_current=True):
    # Implement timeline creation
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def add_clip_to_timeline(connection, clip_name, track_number=1, start_frame=0, end_frame=None):
    # Implement clip addition
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def delete_clip_from_timeline(connection, clip_name, track_number=None):
    # Implement clip deletion
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def add_transition(connection, clip_name, transition_type="CROSS_DISSOLVE", duration=1.0, position="END", track_number=None):
    # Implement transition addition
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def add_effect(connection, clip_name, effect_name, track_number=None, parameters=None):
    # Implement effect addition
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def color_grade_clip(connection, clip_name, track_number=None, lift=None, gamma=None, gain=None, contrast=None, saturation=None, hue=None):
    # Implement color grading
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def import_media(connection, file_path, folder_name=None):
    # Implement media import
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def export_timeline(connection, output_path, format="mp4", codec="h264", quality="high", range_type="ALL"):
    # Implement timeline export
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def add_marker(connection, frame, color="blue", name="", note="", duration=1):
    # Implement marker addition
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def set_project_settings(connection, timeline_resolution=None, timeline_frame_rate=None, color_science=None, colorspace=None):
    # Implement project settings modification
    return {"status": "not_implemented", "message": "Method not yet implemented"}
    
def execute_script(connection, code):
    """Execute arbitrary Python code in the DaVinci Resolve context"""
    try:
        # Create a local execution context with access to Resolve API
        local_context = {
            "resolve": connection.resolve,
            "project_manager": connection.project_manager,
            "project": connection.project,
            "result": None
        }
        
        # Execute the code
        exec(code, globals(), local_context)
        
        # Return the result if one was set
        return {"status": "success", "result": local_context.get("result", "Script executed successfully")}
    except Exception as e:
        logger.error(f"Error executing script: {str(e)}")
        return {"status": "error", "message": f"Script execution error: {str(e)}"} 