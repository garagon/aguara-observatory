Toggle Sidebar
Submit
English
Home
Servers
GBOX Android MCP
GBOX Android MCP
@
babelcloud
Visit Server
6 months ago
developer-tools
#
android
#
linux
#
agent
#
browser
#
mcp
#
sandbox
GBOX provides environments for AI Agents to operate computer and mobile devices.

Mobile Scenario: Your agents can use GBOX to develop/test android apps, or run apps on the Android to complete various tasks(mobile automation).

Desktop Scenario: Your agents can use GBOX to operate desktop apps such as browser, terminal, VSCode, etc(desktop automation).

MCP: You can also plug GBOX MCP to any Agent you like, such as Cursor, Claude Code. These agents will instantly get the ability to operate computer and mobile devices.
Overview
Tools
Comments
Overview
what is Gbox?
Gbox is an open-source project that provides a self-hostable sandbox for MCP (Multi-Client Protocol) integration and other AI agent use cases, enabling secure local command execution for AI clients.
how to use Gbox?
To use Gbox, install it via Homebrew, set up the environment, and export the MCP configuration to your AI client like Claude Desktop or Cursor.
key features of Gbox?
Self-hostable sandbox for AI agents
Integration with MCP clients for local command execution
Support for running sandboxes in Kubernetes clusters
Command-line tool for managing sandbox containers
use cases of Gbox?
Generating diagrams and PDFs from AI clients.
Analyzing and comparing market data.
Processing local files and executing arbitrary tasks.
FAQ from Gbox?
What platforms does Gbox support?
Currently, Gbox supports macOS, with plans for Linux and Windows in the future.
How do I update Gbox?
Use Homebrew to update Gbox and reinitialize the environment.
Can I contribute to Gbox?
Yes! Contributions are welcome, and you can submit a Pull Request after discussing major changes.
Try in Playground
Server Config
{
  "mcpServers": {
    "gbox-android": {
      "command": "npx",
      "args": [
        "-y",
        "@gbox.ai/mcp-android-server@latest"
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