import logging

# Configure logging
logger = logging.getLogger("DaVinciCommands")

def create_timeline(connection, name, width=1920, height=1080, frame_rate=24.0, set_as_current=True):
    """Create a new timeline with the specified parameters"""
    try:
        project = connection.project
        if not project:
            return {"status": "error", "message": "No project is currently open"}
        
        # Check if a timeline with this name already exists
        timeline_count = project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            timeline = project.GetTimelineByIndex(i)
            if timeline and timeline.GetName() == name:
                return {"status": "error", "message": f"Timeline with name '{name}' already exists"}
        
        # Get the media pool (required to create timelines)
        media_pool = project.GetMediaPool()
        if not media_pool:
            return {"status": "error", "message": "Failed to access media pool"}
        
        # Set project settings before creating timeline
        project.SetSetting("timelineResolutionWidth", str(width))
        project.SetSetting("timelineResolutionHeight", str(height))
        project.SetSetting("timelineFrameRate", str(frame_rate))
        
        # Create an empty timeline
        timeline = media_pool.CreateEmptyTimeline(name)
        
        # If timeline creation failed
        if not timeline:
            return {"status": "error", "message": f"Failed to create timeline: {name}"}
            
        # Get info about the created timeline with safe method access
        timeline_name = ""
        timeline_duration = 0
        
        # Try to get the current timeline (the one we just created)
        current_timeline = project.GetCurrentTimeline()
        if current_timeline:
            try:
                timeline_name = current_timeline.GetName()
            except:
                timeline_name = name
                
            try:
                timeline_duration = current_timeline.GetDuration()
            except:
                timeline_duration = 0
        
        return {
            "status": "success", 
            "message": f"Timeline '{name}' created successfully",
            "timeline": {
                "name": timeline_name or name,
                "duration": timeline_duration,
                "frame_rate": frame_rate,
                "resolution": {
                    "width": width,
                    "height": height
                }
            }
        }
    except Exception as e:
        logger.error(f"Error creating timeline: {str(e)}")
        return {"status": "error", "message": f"Error creating timeline: {str(e)}"} 