Toggle Sidebar
Submit
English
Home
Servers
AgentQL MCP Server
AgentQL MCP Server
@
tinyfish-io
Visit Server
10 months ago
research-and-data
#
agent
#
web
#
ai
#
mcp
#
scraping
#
web-scraping
Model Context Protocol server that integrates AgentQL's data extraction capabilities.
Overview
Tools
Comments
Overview
What is AgentQL MCP Server?
AgentQL MCP Server is a Model Context Protocol (MCP) server that integrates AgentQL's data extraction capabilities, allowing users to extract structured data from web pages.
How to use AgentQL MCP Server?
To use the AgentQL MCP Server, install the package via npm, configure it with your preferred application (like Claude, Cursor, or Windsurf), and provide the necessary API key for data extraction.
Key features of AgentQL MCP Server?
Extract structured data from web pages using customizable prompts.
Integration with various applications like Claude, Cursor, and Windsurf.
Easy installation and configuration process.
Use cases of AgentQL MCP Server?
Extracting data from e-commerce websites for price comparison.
Gathering information from social media platforms for analytics.
Automating data collection for research purposes.
FAQ from AgentQL MCP Server?
What is the purpose of the AgentQL MCP Server?
It is designed to facilitate data extraction from web pages using the Model Context Protocol.
Is there a cost associated with using AgentQL MCP Server?
The server is open-source and free to use, but you may need an API key for certain functionalities.
Can I integrate AgentQL MCP Server with other tools?
Yes, it can be integrated with various tools like Claude, Cursor, and Windsurf.
Try in Playground
Server Config
{
  "mcpServers": {
    "agentql": {
      "command": "npx",
      "args": [
        "-y",
        "agentql-mcp"
      ],
      "env": {
        "AGENTQL_API_KEY": "YOUR_API_KEY"
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