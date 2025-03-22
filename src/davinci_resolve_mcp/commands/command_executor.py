import logging
from typing import Dict, Any

# Use relative imports instead of absolute imports to avoid circular dependencies
from .project_info import get_project_info
from .timeline_info import get_timeline_info
from .media_pool_info import get_media_pool_info
from .create_timeline import create_timeline
from .add_clip import add_clip_to_timeline
from .delete_clip import delete_clip_from_timeline
from .add_transition import add_transition
from .add_effect import add_effect
from .color_grade import color_grade_clip
from .import_media import import_media
from .export_timeline import export_timeline
from .add_marker import add_marker
from .project_settings import set_project_settings
from .execute_script import execute_script

# Configure logging
logger = logging.getLogger("DaVinciCommands")

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