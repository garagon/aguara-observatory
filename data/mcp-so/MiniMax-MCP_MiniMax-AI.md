Toggle Sidebar
Submit
English
Home
Servers
MiniMax MCP
MiniMax MCP
@
MiniMax-AI
Visit Server
10 months ago
developer-tools
#
text-to-speech
#
mcp
#
image-generation
#
text-to-image
#
video-generation
#
image-to-video
Official MiniMax Model Context Protocol (MCP) server that enables interaction with powerful Text to Speech, image generation and video generation APIs.
Overview
Tools
Comments
Overview
What is MiniMax MCP?
MiniMax MCP is an official server for the MiniMax Model Context Protocol that facilitates interaction with advanced Text to Speech and video/image generation APIs.
How to use MiniMax MCP?
To use MiniMax MCP, obtain your API key from MiniMax, install the required Python package manager
uv
, and configure your MCP client (like Claude Desktop or Cursor) to connect to the MiniMax server.
Key features of MiniMax MCP?
Enables Text to Speech capabilities
Supports video and image generation
Allows voice cloning
Integrates with various MCP clients like Claude Desktop and Cursor
Use cases of MiniMax MCP?
Broadcasting segments of news with generated speech.
Cloning voices for personalized audio content.
Generating videos for educational or entertainment purposes.
Creating images based on textual descriptions.
FAQ from MiniMax MCP?
What clients can use MiniMax MCP?
MiniMax MCP can be used with clients like Claude Desktop, Cursor, and others that support MCP.
Is there a cost associated with using MiniMax MCP?
Yes, using these tools may incur costs depending on the API usage.
How do I configure my client to use MiniMax MCP?
Follow the setup instructions provided in the documentation for your specific client.
Try in Playground
Server Config
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": [
        "minimax-mcp"
      ],
      "env": {
        "MINIMAX_API_KEY": "<insert-your-api-key-here>",
        "MINIMAX_MCP_BASE_PATH": "<local-output-dir-path>",
        "MINIMAX_API_HOST": "https://api.minimaxi.chat",
        "MINIMAX_API_RESOURCE_MODE": "<optional, [url|local], url is default, audio/image/video are downloaded locally or provided in URL format>"
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