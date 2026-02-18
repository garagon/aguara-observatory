Toggle Sidebar
Submit
English
Home
Servers
Framelink Figma MCP Server
Framelink Figma MCP Server
@
GLips
Visit Server
a year ago
developer-tools
#
typescript
#
ai
#
mcp
#
cursor
#
figma
MCP server to provide Figma layout information to AI coding agents like Cursor
Overview
Tools
Comments
Overview
What is Figma MCP Server?
Figma MCP Server is a server designed to provide Figma layout information to AI coding agents like Cursor, enhancing their ability to implement designs accurately.
How to use Figma MCP Server?
To use the Figma MCP Server, clone the repository, install dependencies, set up your Figma API access token, and connect it to Cursor. Once connected, you can paste links to Figma files in Cursor's composer to interact with the design data.
Key features of Figma MCP Server?
Provides Figma design data to AI coding agents.
Simplifies and translates Figma API responses for better accuracy.
Supports fetching specific file and node information from Figma.
Use cases of Figma MCP Server?
Implementing UI designs directly from Figma files.
Enhancing AI coding agents' accuracy in design implementation.
Streamlining the design-to-code workflow for developers.
FAQ from Figma MCP Server?
Can I use Figma MCP Server with any AI coding agent?
The server is specifically designed for use with Cursor.
Is there a cost associated with using Figma MCP Server?
No, it is free to use.
What kind of access do I need for the Figma API?
Only read access is required for the Figma API.
Try in Playground
Server Config
{
  "mcpServers": {
    "figma-developer-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--stdio"
      ],
      "env": {
        "FIGMA_API_KEY": "<your-figma-api-key>"
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