Toggle Sidebar
Submit
English
Home
Servers
Amap Maps
Amap Maps
@
amap
Visit Server
10 months ago
location-services
#
amap
#
maps
#
location-services
高德地图官方 MCP Server
Overview
Tools
Comments
Overview
What is Amap Maps?
Amap Maps is a server that supports any MCP protocol client, allowing users to easily utilize the Amap Maps MCP server for various location-based services.
How to use Amap Maps?
To use Amap Maps, configure it in a compatible client like Cursor by copying your API key and setting up the server command as specified in the documentation.
Key features of Amap Maps?
Supports multiple location services including geocoding, weather, and distance measurement.
Provides APIs for various transportation modes including walking, driving, and public transit.
Allows for detailed searches of points of interest (POIs) based on keywords or location.
Use cases of Amap Maps?
Converting geographic coordinates to administrative addresses.
Planning routes for cycling, walking, or driving.
Searching for nearby points of interest based on user-defined criteria.
FAQ from Amap Maps?
What types of location services does Amap Maps provide?
Amap Maps provides geocoding, weather information, distance measurement, and route planning for various transportation modes.
Is there a limit to the number of requests I can make?
The usage limits depend on the API key and the specific service being used. Please refer to the Amap documentation for details.
How do I obtain an API key?
You can obtain an API key by creating a project on the Amap developer platform.
Try in Playground
Server Config
{
  "mcpServers": {
    "amap-maps": {
      "command": "npx",
      "args": [
        "-y",
        "@amap/amap-maps-mcp-server"
      ],
      "env": {
        "AMAP_MAPS_API_KEY": "api_key"
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