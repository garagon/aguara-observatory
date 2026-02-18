Toggle Sidebar
Submit
English
Home
Servers
GitLab
GitLab
@
modelcontextprotocol
Visit Server
a year ago
developer-tools
#
gitlab
#
project-management
#
api
GitLab API, enabling project management
Overview
Tools
Comments
Overview
what is GitLab MCP Server?
GitLab MCP Server is an API that enables project management and file operations through the GitLab platform. It facilitates various Git-related tasks using a user-friendly interface.
how to use GitLab MCP Server?
To use the GitLab MCP Server, create a Personal Access Token on GitLab, configure your Claude Desktop application to include your token and GitLab API URL, and employ the various API endpoints for specific tasks like creating projects and managing files.
key features of GitLab MCP Server?
Automatic Branch Creation
: Automatically creates branches if they do not exist during file operations.
Comprehensive Error Handling
: Provides clear error messages for common issues encountered.
Git History Preservation
: Maintains Git history accurately without the need for force pushing.
Batch Operations Support
: Allows both single-file and multi-file operations.
use cases of GitLab MCP Server?
Managing GitLab project repositories programmatically.
Automating file creation and updates across multiple GitLab projects.
Facilitating team collaboration through issue and merge request management.
FAQ from GitLab MCP Server?
How do I create a Personal Access Token?
Visit User Settings > Access Tokens in GitLab to generate a token with the necessary scopes.
Is there a limit on the number of operations I can perform?
There may be rate limits based on your GitLab account type. Monitor your API usage to avoid exceeding limits.
Can I use GitLab MCP Server for self-hosted GitLab instances?
Yes! You can configure the
GITLAB_API_URL
environment variable to point to your self-hosted instance.
Try in Playground
Server Config
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-gitlab"
      ],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
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