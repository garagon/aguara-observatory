Toggle Sidebar
Submit
English
Home
Servers
302_browser_use_mcp
302_browser_use_mcp
@
302ai
Visit Server
10 months ago
#
browser-automation
#
remote-browser
#
automation-tool
Automatically create a remote browser to complete your specified tasks, developed based on Browser Use + Sandbox.

自动创建一个远程浏览器，完成你指定的任务，基于Browser Use + Sandbox开发。
Overview
Tools
Comments
Overview
what is 302AI BrowserUse MCP?
302AI BrowserUse MCP is a tool designed to automatically create a remote browser to complete specified tasks, leveraging Browser Use and Sandbox development.
how to use 302AI BrowserUse MCP?
To use 302AI BrowserUse MCP, install the necessary dependencies, build the server, and configure it with your API key. You can also set it up for use with Claude Desktop by adding the server configuration to the appropriate config file based on your operating system.
key features of 302AI BrowserUse MCP?
Automatic creation of remote browsers for task completion
Integration with Claude Desktop
Debugging tools available through MCP Inspector
use cases of 302AI BrowserUse MCP?
Automating web scraping tasks
Running automated tests on web applications
Completing repetitive online tasks without manual intervention
FAQ from 302AI BrowserUse MCP?
What is the purpose of 302AI BrowserUse MCP?
It automates the creation of remote browsers to perform specified tasks efficiently.
Is there a way to debug the server?
Yes! You can use the MCP Inspector for debugging, which provides a URL to access debugging tools in your browser.
How do I find my API key?
You can find your 302AI_API_KEY
here
.
Try in Playground
Server Config
{
  "mcpServers": {
    "302ai-browser-use-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@302ai/browser-use-mcp"
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