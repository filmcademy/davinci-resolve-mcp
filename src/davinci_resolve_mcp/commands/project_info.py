import logging

# Configure logging
logger = logging.getLogger("DaVinciCommands")

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