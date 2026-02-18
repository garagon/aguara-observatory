Toggle Sidebar
Submit
English
Home
Servers
Github
Github
@
modelcontextprotocol
Visit Server
8 months ago
#
github
#
repository-management
#
api-integration
Repository management, file operations, and GitHub API integration
Overview
Tools
Comments
Overview
what is GitHub MCP Server?
GitHub MCP Server is a tool for managing GitHub repositories, enabling file operations, search functionality, and integration with the GitHub API for seamless collaborative software development.
how to use GitHub MCP Server?
To use this server, set up a GitHub Personal Access Token and integrate it into your application, enabling you to perform various repository management tasks through API calls.
key features of GitHub MCP Server?
Automatic branch creation for file updates and pushes
Comprehensive error handling with clear messages
Preservation of Git history during operations
Support for batch file operations
Advanced search capabilities across repositories, issues, and users
use cases of GitHub MCP Server?
Automating the creation and management of repository files.
Integrating repository management into CI/CD pipelines.
Enabling search functionalities for code and issues in GitHub repositories.
FAQ from GitHub MCP Server?
How do I create a Personal Access Token?
You can create one through GitHub Settings under Developer settings > Personal access tokens.
What kind of operations can I perform with this server?
You can create/update files, search for issues/repositories, create issues/pull requests, and manage branches.
Is this server free to use?
Yes, the server is free to use, but you’ll need a GitHub account to access its features.
Try in Playground
Server Config
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
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