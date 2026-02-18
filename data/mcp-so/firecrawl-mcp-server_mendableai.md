Toggle Sidebar
Submit
English
Home
Servers
Firecrawl Mcp Server
Firecrawl Mcp Server
@
mendableai
Visit Server
8 months ago
#
web-crawler
#
web-scraping
#
data-collection
#
batch-processing
#
content-extraction
#
search-api
Official Firecrawl MCP Server - Adds powerful web scraping to Cursor, Claude and any other LLM clients.
Overview
Tools
Comments
Overview
What is Firecrawl MCP Server?
Firecrawl MCP Server is an implementation of the Model Context Protocol (MCP) that enhances web scraping capabilities for various LLM clients, including Cursor and Claude.
How to use Firecrawl MCP Server?
To use the Firecrawl MCP Server, you can run it using npx or install it manually via npm. Configuration is required to set up the API key and other environment variables.
Key features of Firecrawl MCP Server?
Powerful web scraping with JavaScript rendering support
Automatic retries with exponential backoff
Efficient batch processing with rate limiting
Comprehensive logging and credit usage monitoring
Support for both cloud and self-hosted instances
Use cases of Firecrawl MCP Server?
Scraping content from websites for data analysis
Automating data collection for research purposes
Extracting structured information from web pages using LLM capabilities
FAQ from Firecrawl MCP Server?
Can I use Firecrawl MCP Server for any website?
Yes, as long as the website allows scraping, you can use Firecrawl MCP Server to extract data.
Is there a limit to the number of requests I can make?
Yes, there are rate limits in place to prevent overwhelming the server, but you can configure these settings.
How do I monitor my credit usage?
The server includes a credit usage monitoring feature that alerts you when you reach specified thresholds.
Try in Playground
Server Config
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "firecrawl-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "fc-af1b3ac1a0c2402485402fd0e34da158"
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