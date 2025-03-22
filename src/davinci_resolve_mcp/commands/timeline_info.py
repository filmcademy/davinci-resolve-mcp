import logging

# Configure logging
logger = logging.getLogger("DaVinciCommands")

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