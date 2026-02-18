Toggle Sidebar
Submit
English
Home
Servers
Zhipu Web Search
Zhipu Web Search
@
BigModel
Visit Server
9 months ago
#
search
#
search-api
Zhipu Web Search MCP Server is a search engine specifically designed for large models. It integrates four search engines, allowing users to flexibly compare and switch between them. Building upon the web crawling and ranking capabilities of traditional search engines, it enhances intent recognition capabilities, returning results more suitable for large model processing (such as webpage titles, URLs, summaries, site names, site icons, etc.). This helps AI applications achieve "dynamic knowledge acquisition" and "precise scenario adaptation" capabilities.
Overview
Tools
Comments
Overview
what is Zhipu Web Search?
Zhipu Web Search is a specialized search engine designed for large models, integrating four different search engines to allow users to compare and switch between them flexibly. It enhances traditional web crawling and ranking capabilities with improved intent recognition, providing results tailored for large model processing.
how to use Zhipu Web Search?
To use Zhipu Web Search, obtain an API Key from the
Zhipu BigModel Open Platform
and configure it in a compatible client like Cursor. The MCP service can be integrated through simple configuration in the client settings.
key features of Zhipu Web Search?
Integration of multiple search engines for flexible comparisons
Enhanced intent recognition for better result relevance
Support for large model processing with tailored results including titles, URLs, summaries, and site icons
use cases of Zhipu Web Search?
AI applications requiring dynamic knowledge acquisition
Scenarios needing precise adaptation of search results
Research and data analysis leveraging large model capabilities
FAQ from Zhipu Web Search?
What types of search engines does Zhipu Web Search integrate?
It integrates several search engines including Zhipu proprietary engines standard and Zhipu proprietary engines advanced versions, as well as Sogou、Jina and Quark search engines.
How do I obtain an API Key?
You can obtain an API Key from the
Zhipu BigModel Open Platform
.
Can I use Zhipu Web Search with any client?
It supports clients that run the MCP protocol, such as Cursor and Cherry Studio.
Try in Playground
Server Config
{
  "mcpServers": {
    "zhipu-web-search-sse": {
      "url": "https://open.bigmodel.cn/api/mcp/web_search/sse?Authorization={you ak/sk}"
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