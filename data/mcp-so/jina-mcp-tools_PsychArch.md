Toggle Sidebar
Submit
English
Home
Servers
Jina AI MCP Tools
Jina AI MCP Tools
@
PsychArch
Visit Server
9 months ago
research-and-data
A Model Context Protocol (MCP) server that integrates with Jina AI Search Foundation APIs.
Overview
Tools
Comments
Overview
what is Jina AI MCP Tools?
Jina AI MCP Tools is a Model Context Protocol (MCP) server that integrates with Jina AI Search Foundation APIs, enabling users to access various AI-driven tools for web reading, searching, and fact-checking.
how to use Jina AI MCP Tools?
To use Jina AI MCP Tools, you need to set up a configuration file for Cursor and provide your Jina API key. Once configured, you can instruct Cursor to use the Jina tools for various tasks.
key features of Jina AI MCP Tools?
Web Reader
: Extracts content from web pages.
Web Search
: Searches the web for information.
Fact-Check
: Verifies factual statements.
use cases of Jina AI MCP Tools?
Extracting content from a specific webpage for analysis.
Searching for information on complex topics like quantum computing.
Verifying claims or statements for accuracy.
FAQ from Jina AI MCP Tools?
How do I get a Jina API key?
You can obtain a free API key from the Jina AI website.
What programming language is Jina AI MCP Tools built with?
Jina AI MCP Tools is built using JavaScript.
Is there a license for Jina AI MCP Tools?
Yes, it is licensed under the MIT license.
Try in Playground
Server Config
{
  "mcpServers": {
    "jina-mcp-tools": {
      "command": "npx",
      "args": [
        "jina-mcp-tools"
      ],
      "env": {
        "JINA_API_KEY": "your_jina_api_key_here"
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