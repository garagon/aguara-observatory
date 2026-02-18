Toggle Sidebar
Submit
English
Home
Servers
Mailtrap Email Sending MCP
Mailtrap Email Sending MCP
@
Mailtrap
Visit Server
10 months ago
developer-tools
#
mailtrap
#
email-api
#
transactional-emails
An MCP server that provides a tool for sending transactional emails via Mailtrap
Overview
Tools
Comments
Overview
what is Mailtrap Email API?
Mailtrap Email API is a server tool designed for sending transactional emails through Mailtrap, allowing developers to integrate email functionalities into their applications seamlessly.
how to use Mailtrap Email API?
To use the Mailtrap Email API, configure your environment with the necessary API token and sender email, then utilize the provided commands to send emails through the API.
key features of Mailtrap Email API?
Easy integration for sending transactional emails.
Support for various email parameters including CC and BCC.
Configuration options for different environments (Claude Desktop, Cursor, VS Code).
use cases of Mailtrap Email API?
Sending automated emails for user registrations.
Notifying users about password resets.
Sending order confirmations and shipping updates.
FAQ from Mailtrap Email API?
Is Mailtrap Email API free to use?
Mailtrap offers a free tier, but additional features may require a paid plan.
Can I use Mailtrap Email API for bulk emails?
Mailtrap is primarily designed for transactional emails, not bulk email campaigns.
How do I troubleshoot email sending issues?
Check your API token and email configurations, and refer to the documentation for common troubleshooting steps.
Try in Playground
Server Config
{
  "mcpServers": {
    "mailtrap": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-mailtrap"
      ],
      "env": {
        "MAILTRAP_API_TOKEN": "your_mailtrap_api_token",
        "DEFAULT_FROM_EMAIL": "your_sender@example.com"
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