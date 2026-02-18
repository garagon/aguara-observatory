Toggle Sidebar
Submit
English
Home
Servers
Google Maps
Google Maps
@
modelcontextprotocol
Visit Server
a year ago
location-services
#
google-maps
#
location-services
#
map-api
Location services, directions, and place details
Overview
Tools
Comments
Overview
what is Google Maps?
Google Maps is a location services API that provides directions, place details, and geographic data to enhance applications with mapping functionalities.
how to use Google Maps?
To use the Google Maps API, you need to obtain an API key from Google and then integrate it into your application by configuring it according to your needs. You can access various functionalities such as geocoding, searching for places, and getting directions.
key features of Google Maps?
Geolocation services for converting addresses to coordinates and vice versa
Search and retrieve detailed information about places
Calculate distances and times between locations
Get directions for different modes of transport
Elevation data for specified locations
use cases of Google Maps?
Developing navigation software for personal and commercial use
Real estate applications for displaying property locations
Transportation logistics to calculate routes and delivery times
Event planning tools for location-based services
FAQ from Google Maps?
How do I get a Google Maps API key?
You can get a Google Maps API key by following the instructions found on the Google Maps documentation site.
What types of services does the Google Maps API provide?
The Google Maps API offers various services including geocoding, place searching, distance matrix calculations, directions, and elevation data.
Is there a cost associated with using Google Maps?
Google Maps has a pay-as-you-go pricing model, where costs depend on the usage and the specific services you access.
Try in Playground
Server Config
{
  "mcpServers": {
    "google-maps": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GOOGLE_MAPS_API_KEY",
        "mcp/google-maps"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "<YOUR_API_KEY>"
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