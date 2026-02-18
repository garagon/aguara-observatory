Toggle Sidebar
Submit
English
Home
Servers
Brave Search
Brave Search
@
modelcontextprotocol
Visit Server
10 months ago
knowledge-and-memory
#
brave-search
#
search-api
#
web-and-local-search
Web and local search using Brave's Search API
Overview
Tools
Comments
Overview
what is Brave Search?
Brave Search is an MCP server implementation that utilizes the Brave Search API to provide both web and local search capabilities.
how to use Brave Search?
To use Brave Search, sign up for a Brave Search API account to get an API key, then configure the server in your application with the provided API key and start making search queries.
key features of Brave Search?
Web Search
: Execute general queries, news, and articles with pagination and freshness controls.
Local Search
: Find businesses and services with detailed descriptions, automatically falling back to web search if no local results are found.
Flexible Filtering
: Control types of results, safety levels, and content freshness.
Smart Fallbacks
: Automatically fallback to web search for local queries when no results are found.
use cases of Brave Search?
Conducting general web searches for news articles.
Finding local businesses or services quickly.
Custom filtering of search results based on user-defined criteria.
FAQ from Brave Search?
How do I obtain an API Key for Brave Search?
Sign up for a Brave Search API account, select a plan, and generate your API key from the developer dashboard.
Is there a free tier available?
Yes, the free tier allows up to 2,000 queries per month.
What happens if no local search results are found?
The service automatically falls back to a web search to continue providing relevant results.
Try in Playground
Server Config
{
  "mcpServers": {
    "brave-search": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "BRAVE_API_KEY",
        "mcp/brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
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