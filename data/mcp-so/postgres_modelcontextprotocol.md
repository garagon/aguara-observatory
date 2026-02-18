Toggle Sidebar
Submit
English
Home
Servers
PostgreSQL
PostgreSQL
@
modelcontextprotocol
Visit Server
a year ago
databases
#
postgresql
#
database-access
#
read-only
Read-only database access with schema inspection
Overview
Tools
Comments
Overview
what is PostgreSQL?
PostgreSQL is a Model Context Protocol server providing read-only access to PostgreSQL databases, allowing for schema inspection and execution of read-only queries.
how to use PostgreSQL?
To use PostgreSQL, configure it within the Claude Desktop app by adding the necessary parameters to the "mcpServers" section of the `claude_desktop_config.json` file. Replace the database name in the configuration with your specific database.
key features of PostgreSQL?
Execute read-only SQL queries within a read-only transaction.
Access detailed schema information for each table, including column names and data types.
Automatically discovers schemas from database metadata.
use cases of PostgreSQL?
Inspecting database schemas before performing extensive data analysis.
Running read-only queries to generate reports without altering database states.
Integration with LLMs for database-related tasks in applications.
FAQ from PostgreSQL?
Is PostgreSQL suitable for writing data?
No! PostgreSQL provides read-only access, which means data cannot be modified through this server.
Can I use PostgreSQL with other apps?
Yes! While designed for Claude Desktop, PostgreSQL can be integrated into other applications that can call its endpoints.
How do I get schema information for a table?
Schema information is automatically discovered and can be accessed via the provided schema URL endpoint.
Try in Playground
Server Config
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
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