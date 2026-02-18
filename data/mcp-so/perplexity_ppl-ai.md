Toggle Sidebar
Submit
English
Home
Servers
Perplexity Ask MCP Server
Perplexity Ask MCP Server
@
ppl-ai
Visit Server
10 months ago
research-and-data
#
mathgpt
#
math-solver
#
math-assistant
A Model Context Protocol Server connector for Perplexity API, to enable web search without leaving the MCP ecosystem.
Overview
Tools
Comments
Overview
what is Perplexity Ask MCP Server?
Perplexity Ask MCP Server is a Model Context Protocol Server connector for the Perplexity API, enabling web search capabilities within the MCP ecosystem.
how to use Perplexity Ask MCP Server?
To use the server, clone the MCP repository, install dependencies, obtain a Sonar API key, configure the Claude desktop, build the Docker image, and test the integration.
key features of Perplexity Ask MCP Server?
Real-time web search integration with the Sonar API.
Easy configuration and setup for users.
Support for advanced search parameters.
use cases of Perplexity Ask MCP Server?
Conducting live web searches without leaving the MCP environment.
Enhancing research capabilities for users of the Claude desktop.
Integrating web search functionalities into applications using the Perplexity API.
FAQ from Perplexity Ask MCP Server?
How do I get a Sonar API key?
Sign up for a Sonar API account and generate your API key from the developer dashboard.
Is there a troubleshooting guide available?
Yes, the Claude documentation provides a troubleshooting guide for common issues.
What license is the MCP server under?
The MCP server is licensed under the MIT License, allowing free use, modification, and distribution.
Try in Playground
Server Config
{
  "mcpServers": {
    "perplexity-ask": {
      "command": "npx",
      "args": [
        "-y",
        "@chatmcp/server-perplexity-ask"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "YOUR_API_KEY_HERE"
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