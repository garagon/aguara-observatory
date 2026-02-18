Toggle Sidebar
Submit
English
Home
Servers
Sentry
Sentry
@
modelcontextprotocol
Visit Server
a year ago
research-and-data
#
sentry
#
error-tracking
#
issue-analysis
Retrieving and analyzing issues from Sentry.io
Overview
Tools
Comments
Overview
what is Sentry?
Sentry is a Model Context Protocol server designed for retrieving and analyzing issues from Sentry.io. It enables developers to inspect error reports, stack traces, and debugging information efficiently.
how to use Sentry?
To use Sentry, install it via pip or the recommended uv tool, set your Sentry authentication token, and invoke it through command line or integration in development environments like Claude Desktop or Zed.
key features of Sentry?
Retrieve and analyze Sentry issues by ID or URL.
Detailed insights into issue including title, status, timestamps, and stack traces.
Support for debugging with the MCP inspector.
use cases of Sentry?
Analyzing application errors in real-time.
Retrieving historical error reports for diagnostics.
Debugging and improving application reliability by inspecting stack traces.
FAQ from Sentry?
How do I install Sentry?
You can install Sentry via pip using the command 'pip install mcp-server-sentry' or by using the uv tool.
What programming languages does Sentry support?
Sentry can be used with any programming language that can communicate with Sentry.io, as it primarily retrieves data from the Sentry API.
Is there support for multiple Sentry projects?
Yes, Sentry can handle multiple projects as long as you provide the corresponding authentication token for each project.
Try in Playground
Server Config
{
  "mcpServers": {
    "sentry": {
      "command": "uvx",
      "args": [
        "mcp-server-sentry",
        "--auth-token",
        "YOUR_SENTRY_TOKEN"
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