Toggle Sidebar
Submit
English
Home
Servers
Redis
Redis
@
modelcontextprotocol
Visit Server
a year ago
databases
#
redis
#
database
#
key-value-store
A Model Context Protocol server that provides access to Redis databases. This server enables LLMs to interact with Redis key-value stores through a set of standardized tools.
Overview
Tools
Comments
Overview
what is Redis?
Redis is a Model Context Protocol server that provides access to Redis databases, enabling LLMs to interact with Redis key-value stores through standardized tools.
how to use Redis?
To use Redis, configure it in the "mcpServers" section of your
claude_desktop_config.json
or run it using Docker or NPX commands as specified in the documentation.
key features of Redis?
Set, get, delete, and list operations for Redis key-value pairs.
Supports optional expiration for keys.
Easy integration with Claude Desktop and Docker.
use cases of Redis?
Storing and retrieving user session data.
Caching frequently accessed data for faster retrieval.
Managing real-time data feeds in applications.
FAQ from Redis?
What is the default Redis URL?
The default Redis URL is "redis://localhost:6379".
Can I run Redis in a Docker container?
Yes! You can run Redis using Docker with the provided command.
Is Redis open source?
Yes! Redis is licensed under the MIT License, allowing free use, modification, and distribution.
Try in Playground
Server Config
{
  "mcpServers": {
    "redis": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp/redis",
        "redis://host.docker.internal:6379"
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