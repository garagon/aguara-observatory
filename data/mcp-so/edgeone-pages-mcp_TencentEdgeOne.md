Toggle Sidebar
Submit
English
Home
Servers
EdgeOne Pages MCP
EdgeOne Pages MCP
@
TencentEdgeOne
Visit Server
10 months ago
cloud-platforms
An MCP service designed for deploying HTML content to EdgeOne Pages and obtaining an accessible public URL.
Overview
Tools
Comments
Overview
What is EdgeOne Pages MCP?
EdgeOne Pages MCP is a service designed for deploying HTML content to EdgeOne Pages, allowing users to obtain a publicly accessible URL for their content.
How to use EdgeOne Pages MCP?
To use EdgeOne Pages MCP, provide your HTML content to the MCP service, and it will deploy the content, returning a public URL that can be accessed immediately.
Key features of EdgeOne Pages MCP?
Rapid deployment of HTML content using the MCP protocol.
Automatic generation of publicly accessible URLs for deployed content.
Use cases of EdgeOne Pages MCP?
Deploying static HTML websites quickly.
Sharing HTML content with a public URL for easy access.
Integrating with EdgeOne Pages Functions for serverless applications.
FAQ from EdgeOne Pages MCP?
What is the MCP protocol?
The MCP protocol is a method for quickly deploying content to EdgeOne Pages, ensuring fast access and delivery.
Is there a limit to the HTML content I can deploy?
There may be limitations based on the EdgeOne Pages service policies, so it's best to refer to the documentation for specifics.
How do I access the deployed content?
After deployment, the service will provide a public URL that can be accessed via a web browser.
Try in Playground
Server Config
{
  "mcpServers": {
    "edgeone-pages-mcp-server": {
      "command": "npx",
      "args": [
        "edgeone-pages-mcp"
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