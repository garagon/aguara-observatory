Toggle Sidebar
Submit
English
Home
Servers
Baidu Map
Baidu Map
@
baidu-maps
Visit Server
a year ago
location-services
#
baidu-map
#
location-services
#
map-api
百度地图核心API现已全面兼容MCP协议，是国内首家兼容MCP协议的地图服务商。
Overview
Tools
Comments
Overview
what is Baidu Map?
Baidu Map is a core API service that is fully compatible with the MCP protocol, making it the first map service provider in China to support this protocol.
how to use Baidu Map?
To use Baidu Map, you need to create a server-side API key (AK) on the Baidu Map Open Platform and then integrate the API using either Python or Typescript SDKs.
key features of Baidu Map?
Provides 8 core API interfaces including geocoding, reverse geocoding, place search, route planning, and weather queries.
Supports integration with intelligent assistants that are compatible with the MCP protocol.
use cases of Baidu Map?
Geocoding addresses to coordinates.
Retrieving detailed information about places of interest (POIs).
Planning routes for driving, walking, or public transport.
Querying current weather based on location.
FAQ from Baidu Map?
What is the MCP protocol?
The MCP protocol is a standard for integrating various services and tools in a unified manner. More details can be found in the official MCP documentation.
Is there a cost to use Baidu Map API?
The usage of Baidu Map API may vary; please check the Baidu Map Open Platform for pricing details.
How can I troubleshoot issues with the API?
You can refer to the official documentation or community forums for troubleshooting tips.
Try in Playground
Server Config
{
  "mcpServers": {
    "baidu-map": {
      "command": "npx",
      "args": [
        "-y",
        "@baidumap/mcp-server-baidu-map"
      ],
      "env": {
        "BAIDU_MAP_API_KEY": "xxx"
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