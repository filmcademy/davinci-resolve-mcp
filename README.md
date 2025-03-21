# DaVinci Resolve MCP - Model Context Protocol Integration

DaVinci Resolve MCP connects DaVinci Resolve to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control DaVinci Resolve. This integration enables AI-assisted video editing, color grading, and timeline manipulation.

## Join the Community
Give feedback, get inspired, and build on top of the MCP: [Discord](https://discord.gg/modelcontextprotocol)

## Features

- **Two-way communication**: Connect Claude AI to DaVinci Resolve through a socket-based server
- **Project Management**: Get project information, set project settings (resolution, frame rate, color science)
- **Timeline Editing**: Create timelines, add/delete clips, add transitions and effects
- **Media Management**: Import media files, get clip information, export completed timelines
- **Color Grading**: Apply and modify color grades and effects
- **Markers and Annotations**: Add markers to the timeline
- **Code Execution**: Run arbitrary Python or Lua scripts in DaVinci Resolve from Claude

## Components

The system consists of two main components:

1. **DaVinci Resolve Integration** (`src/davinci_mcp/addon.py`): Connects to DaVinci Resolve's API to send and receive commands
2. **MCP Server** (`src/davinci_mcp/server.py`): A Python server that implements the Model Context Protocol and connects to DaVinci Resolve

## Installation

### Prerequisites

- DaVinci Resolve Studio or free version (compatible with version 18 or newer)
- Python 3.8 or newer
- `uv` and `uvx` package managers:

   If you're on Mac:
   ```bash
   brew install uv
   pip install uvx
   ```
   
   On Windows:
   ```powershell
   # Install uv
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   set Path=C:\Users\username\.local\bin;%Path%
   
   # Install uvx
   pip install uvx
   ```
   
   On Linux:
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install uvx
   pip install uvx
   ```
   
   Or visit [Install uv](https://github.com/astral-sh/uv) for other platforms

⚠️ **Do not proceed before installing UV and UVX**

### Install DaVinci Resolve MCP

Clone the repository:
```bash
git clone https://github.com/filmcademy/davinci-resolve-mcp.git
cd davinci-resolve-mcp
```

Install the package:
```bash
uv pip install -e .
```

### Claude for Desktop Integration

Go to Claude > Settings > Developer > Edit Config > `claude_desktop_config.json` to include the following:

```json
{
    "mcpServers": {
        "davinci": {
            "command": "uvx",
            "args": [
                "resolve-mcp"
            ]
        }
    }
}
```

### Cursor Integration

Run resolve-mcp without installing it permanently through uvx. Go to Cursor Settings > MCP and paste this as a command:

```
uvx resolve-mcp
```

⚠️ **Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both**

### DaVinci Resolve Integration Setup

For DaVinci Resolve to work properly with the MCP, make sure:

1. DaVinci Resolve is running before starting the MCP server
2. The script paths are properly set up (handled automatically by the MCP server)
3. You have the DaVinci Resolve API available on your system:
   - For Windows: Located at `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\`
   - For macOS: Located at `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/`
   - For Linux: Located at `/opt/resolve/Developer/Scripting/Modules/` or `/home/resolve/Developer/Scripting/Modules/`

The MCP server will automatically detect and use the appropriate path for your operating system.

## Usage

### Starting the MCP Server Manually

You can start the DaVinci Resolve MCP server using the following methods:

Using uvx (recommended):
```bash
uvx davinci-resolve-mcp
```

If you installed the package globally:
```bash
davinci-resolve-mcp
```

Or directly with Python:
```bash
cd /path/to/davinci-resolve-mcp
python -m davinci_mcp.server
```

The server will listen on localhost:9877 by default.

### Command-line Arguments

All methods accept the same arguments:

```
--host <ip>     # IP address to bind the server to (default: localhost)
--port <port>   # Port to listen on (default: 9877)
```

For example:
```bash
uvx davinci-resolve-mcp --host 0.0.0.0 --port 8000
```

### Using with Claude

Once the config file has been set on Claude, and the DaVinci Resolve MCP is running, you will see a hammer icon with tools for the DaVinci Resolve MCP in Claude.

## Example Commands

Here are some examples of what you can ask Claude to do:

- "Create a new timeline with 1080p resolution and 24fps"
- "Import the video files from my downloads folder"
- "Add a cross-dissolve transition between the first two clips"
- "Apply a cinematic color grade to the selected clip"
- "Add text that says 'Introduction' to the beginning of the timeline"
- "Export the current timeline as an H.264 MP4 file"
- "Create a montage from the clips in my media pool"
- "Get information about the current project and suggest improvements"

## API Documentation

The DaVinci MCP exposes the following API endpoints:

### Project Information

- `get_project_info`: Returns information about the current project including timelines, format settings, and media
- `get_timeline_info`: Returns details about a specific timeline or the currently active timeline
- `get_media_pool_info`: Returns information about the media pool's contents

### Timeline Operations

- `create_timeline`: Creates a new timeline with specified settings
- `add_clip_to_timeline`: Adds a clip from the media pool to the timeline
- `set_clip_properties`: Updates properties of a clip in the timeline
- `add_transition`: Adds transitions between clips

### Rendering

- `render_timeline`: Renders the current timeline to a specified format and location

### Advanced Operations

- `execute_script`: Executes arbitrary Python code in the DaVinci Resolve context

## Development

### Project Structure

- `src/davinci_mcp/server.py`: Main MCP server implementation
- `src/davinci_mcp/addon.py`: DaVinci Resolve integration functionality

### Adding New Commands

To add new commands to the MCP server, follow these steps:

1. Add a new handler method to the `DaVinciMCPServer` class in `addon.py`
2. Register the handler in the `execute_command` method's handler dictionary
3. Update the API documentation

## Troubleshooting

### Common Issues

- **DaVinci Resolve API not found**: Ensure that DaVinci Resolve is installed and running, and that the API modules are properly installed
- **Connection refused**: Check that DaVinci Resolve is running and that the server is configured correctly
- **No project is currently open**: Open a DaVinci Resolve project before making API calls

## Development Status

This project is in development and may not provide complete access to all DaVinci Resolve features. Contributions and feature requests are welcome.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Blackmagic Design for DaVinci Resolve
- The MCP project for the protocol specification 