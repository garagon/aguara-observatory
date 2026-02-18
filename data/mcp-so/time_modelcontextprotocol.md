Toggle Sidebar
Submit
English
Home
Servers
Time
Time
@
modelcontextprotocol
Visit Server
9 days ago
#
time
#
timezone
#
mcp-server
A Model Context Protocol server that provides time and timezone conversion capabilities. This server enables LLMs to get current time information and perform timezone conversions using IANA timezone names, with automatic system timezone detection.
Overview
Tools
Comments
Overview
what is Time MCP Server?
Time MCP Server is a Model Context Protocol server that provides time and timezone conversion capabilities. It enables LLMs to get current time information and perform timezone conversions using IANA timezone names, with automatic system timezone detection.
how to use Time MCP Server?
To use Time MCP Server, you can install it via pip or use uvx for direct execution. After installation, configure it in your Claude or Zed settings. The server provides tools like
get_current_time
and
convert_time
to fetch current time in a specific timezone and convert time between timezones, respectively.
key features of Time MCP Server?
Provides current time information in any IANA timezone.
Converts time between different timezones.
Automatic system timezone detection with the option to override.
Easy integration with Claude and Zed through configuration settings.
use cases of Time MCP Server?
Getting the current time in a specific timezone.
Converting time between different timezones for scheduling and coordination.
Automating time-related queries in applications and services.
FAQ from Time MCP Server?
Can Time MCP Server handle all IANA timezones?
Yes, Time MCP Server supports all IANA timezones for time and timezone conversion.
Is Time MCP Server free to use?
Yes, Time MCP Server is open-source and free to use under the MIT License.
How accurate is the time provided by Time MCP Server?
The time provided by Time MCP Server is highly accurate, relying on system time and IANA timezone data for precision.
Try in Playground
Server Config
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": [
        "mcp-server-time",
        "--local-timezone=America/New_York"
      ]
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