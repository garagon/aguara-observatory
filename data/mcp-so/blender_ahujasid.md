Toggle Sidebar
Submit
English
Home
Servers
Blender
Blender
@
ahujasid
Visit Server
a year ago
developer-tools
#
blender
#
3d-modeling
#
AI-integration
BlenderMCP connects Blender to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Blender. This integration enables prompt assisted 3D modeling, scene creation, and manipulation.
Overview
Tools
Comments
Overview
What is BlenderMCP?
BlenderMCP is an integration that connects Blender to Claude AI through the Model Context Protocol (MCP), enabling prompt-assisted 3D modeling, scene creation, and manipulation.
How to use BlenderMCP?
To use BlenderMCP, install the addon in Blender, configure the MCP server, and connect to Claude AI to start creating and manipulating 3D models.
Key features of BlenderMCP?
Two-way communication between Claude AI and Blender.
Object manipulation capabilities including creation, modification, and deletion of 3D objects.
Material control for applying and modifying materials and colors.
Scene inspection to get detailed information about the current Blender scene.
Ability to execute arbitrary Python code in Blender from Claude.
Use cases of BlenderMCP?
Creating complex 3D scenes with AI assistance.
Modifying existing 3D models through natural language commands.
Generating 3D models based on user-defined parameters or images.
FAQ from BlenderMCP?
Can BlenderMCP work with any version of Blender?
No, BlenderMCP requires Blender 3.0 or newer.
Is there a limit to the number of models I can generate?
Yes, Hyper3D's free trial key allows a limited number of models per day.
What should I do if I encounter connection issues?
Ensure the Blender addon server is running and the MCP server is configured correctly.
Try in Playground
Server Config
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": [
        "blender-mcp"
      ]
    }
  }
}
© 2025 MCP.so. All rights reserved.
Build with
ShipAny
.
Explore
Playground
Blog
Cases
DXT
Partners
Privacy
Terms