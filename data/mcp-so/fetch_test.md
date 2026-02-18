Toggle Sidebar
Submit
English
Home
Servers
Fetch
Fetch
@
test
Visit Server
4 months ago
#
web-fetching
#
llm-tools
#
html-to-markdown
Web content fetching and conversion for efficient LLM usage
Overview
Tools
Comments
Overview
What is Fetch?
Fetch is a Model Context Protocol (MCP) server designed for web content fetching and conversion, allowing Large Language Models (LLMs) to retrieve and process content from web pages by converting HTML into markdown for easier consumption.
How to use Fetch?
To use Fetch, install it via node.js or pip, and then run the server using the command:
python -m mcp_server_fetch
or with
uvx
as specified in the documentation. You can fetch content by calling the
fetch
tool with a URL.
Key features of Fetch?
Fetches web URLs and extracts their content in markdown format.
Supports configuration options such as maximum length of content and starting index for extraction.
Customizable user-agent and robots.txt compliance settings.
Use cases of Fetch?
Enabling LLMs to access and process data from web pages for various applications.
Converting online articles into a simplified format for analysis.
Assisting in data retrieval tasks for research and data aggregation workflows.
FAQ from Fetch?
Can Fetch handle all types of web content?
Fetch is capable of extracting content from most web pages, although results may vary based on the site's structure and restrictions.
Is Fetch easy to integrate with other tools?
Yes! Fetch is designed to integrate smoothly with LLMs and can be customized to meet specific needs.
Is there any usage limit for Fetch?
Fetch does not impose strict usage limits, but your implementation may be subject to the guidelines of the websites you access.
Try in Playground
Server Config
{
  "mcpServers": {
    "fetch": {
      "args": [
        "mcp-server-fetch"
      ],
      "command": "uvx"
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