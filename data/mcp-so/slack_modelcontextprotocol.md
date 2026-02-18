Toggle Sidebar
Submit
English
Home
Servers
Slack
Slack
@
modelcontextprotocol
Visit Server
9 months ago
#
slack
#
messaging
#
channel-management
Channel management and messaging capabilities
Overview
Tools
Comments
Overview
What is Slack?
Slack is a channel management and messaging solution that enables seamless interaction within workspaces, integrating with various tools for efficiency.
How to use Slack?
To use Slack, create a Slack app, configure necessary bot token scopes, and install the app to your workspace. The system supports various commands to manage channels, post messages, and retrieve user information.
Key features of Slack?
List public channels in the workspace
Post messages to channels
Reply to message threads
Add emoji reactions to messages
Retrieve channel message history
Get detailed user profiles
Use cases of Slack?
Team communication across multiple channels
Project management using message threads
Integrating with third-party applications and services
FAQ from Slack?
What is required to set up Slack?
You need to create a Slack app, configure scopes, and install it in your workspace.
Can Slack be integrated with other tools?
Yes, Slack supports integration with various third-party applications to enhance productivity.
Is there a limit on the number of channels I can manage?
The maximum number of channels returned in a single query can be set to 200, but there is no overall limit on channels within a workspace.
Try in Playground
Server Config
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_TEAM_ID": "T01234567",
        "SLACK_CHANNEL_IDS": "C01234567, C76543210"
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