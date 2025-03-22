import logging

# Configure logging
logger = logging.getLogger("DaVinciCommands")

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