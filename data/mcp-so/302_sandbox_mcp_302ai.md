Toggle Sidebar
Submit
English
Home
Servers
302_sandbox_mcp
302_sandbox_mcp
@
302ai
Visit Server
10 months ago
#
302ai
#
sandbox
#
mcp
#
server
Create a remote sandbox that can execute code/run commands/upload and download files.
创建远程沙盒，可以执行代码/运行命令/上传下载文件
Overview
Tools
Comments
Overview
what is 302AI Sandbox MCP?
302AI Sandbox MCP is a server designed for development and integration with Claude Desktop, allowing users to set up and run a model context protocol (MCP) server.
how to use 302AI Sandbox MCP?
To use the 302AI Sandbox MCP, install the necessary dependencies, build the server, and configure it with your Claude Desktop application by adding the server configuration to the appropriate config file based on your operating system.
key features of 302AI Sandbox MCP?
Easy installation and setup for developers
Auto-rebuild feature for development
Integration with Claude Desktop for enhanced functionality
Debugging tools available through MCP Inspector
use cases of 302AI Sandbox MCP?
Developing and testing AI models in a controlled environment.
Integrating custom AI solutions with existing applications.
Debugging and optimizing AI server performance.
FAQ from 302AI Sandbox MCP?
How do I install the 302AI Sandbox MCP?
You can install it by running
npm install
and then build the server with
npm run build
.
Can I use this server on Windows?
Yes! The server can be configured on both MacOS and Windows.
Where can I find my API key?
You can find your 302AI_API_KEY
here
.
Try in Playground
Server Config
{
  "mcpServers": {
    "302ai-sandbox-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@302ai/sandbox-mcp"
      ],
      "env": {
        "302AI_API_KEY": "YOUR_API_KEY_HERE"
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