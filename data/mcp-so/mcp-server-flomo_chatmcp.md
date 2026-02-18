Toggle Sidebar
Submit
English
Home
Servers
mcp-server-flomo MCP Server
mcp-server-flomo MCP Server
@
chatmcp
Visit Server
10 months ago
knowledge-and-memory
#
mcp
#
mcp-server
#
mcp-flomo
#
mcp-server-flomo
Write notes to Flomo
Overview
Tools
Comments
Overview
What is MCP Server Flomo?
MCP Server Flomo is a TypeScript-based server that allows users to write notes directly to Flomo, a note-taking application.
How to use MCP Server Flomo?
To use MCP Server Flomo, you need to install the server and configure it with your Flomo API URL. You can run the server using the command line with the appropriate configurations.
Key features of MCP Server Flomo?
Write text notes to Flomo using the
write_note
tool.
Easy installation and configuration for different operating systems.
Debugging support through MCP Inspector for easier troubleshooting.
Use cases of MCP Server Flomo?
Quickly jotting down notes from various applications to Flomo.
Automating note-taking processes for developers and researchers.
Integrating with other tools to enhance productivity.
FAQ from MCP Server Flomo?
How do I find my Flomo API URL?
You can find your Flomo API URL by visiting
this link
.
Is MCP Server Flomo free to use?
Yes! MCP Server Flomo is free to use for everyone.
What programming language is MCP Server Flomo built with?
MCP Server Flomo is built using TypeScript.
Try in Playground
Server Config
{
  "mcpServers": {
    "mcp-server-flomo": {
      "command": "npx",
      "args": [
        "-y",
        "@chatmcp/mcp-server-flomo"
      ],
      "env": {
        "FLOMO_API_URL": "https://flomoapp.com/iwh/xxx/xxx/"
      }
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