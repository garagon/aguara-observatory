Toggle Sidebar
Submit
English
Home
Servers
Aws Kb Retrieval Server
Aws Kb Retrieval Server
@
modelcontextprotocol
Visit Server
10 months ago
research-and-data
#
aws-kb-retrieval
#
mcp-server
#
knowledge-base
An MCP server implementation for retrieving information from the AWS Knowledge Base using the Bedrock Agent Runtime.
Overview
Tools
Comments
Overview
what is AWS Knowledge Base Retrieval Server?
The AWS Knowledge Base Retrieval Server is an MCP server implementation designed to retrieve information from the AWS Knowledge Base using the Bedrock Agent Runtime.
how to use AWS Knowledge Base Retrieval Server?
To use the server, set up your AWS credentials and configure the server in your
claude_desktop_config.json
. You can run it using Docker or npx commands with the necessary environment variables for AWS access.
key features of AWS Knowledge Base Retrieval Server?
RAG (Retrieval-Augmented Generation)
: Retrieve context from the AWS Knowledge Base based on a query and a Knowledge Base ID.
Supports multiple results retrieval
: Option to retrieve a customizable number of results.
use cases of AWS Knowledge Base Retrieval Server?
Retrieving specific information from AWS documentation based on user queries.
Integrating with applications that require dynamic access to AWS Knowledge Base content.
Enhancing customer support tools with quick access to AWS resources.
FAQ from AWS Knowledge Base Retrieval Server?
How do I set up AWS credentials?
Obtain your AWS access key ID, secret access key, and region from the AWS Management Console and ensure they have the necessary permissions.
Can I customize the number of results retrieved?
Yes! You can specify the number of results to retrieve when making a query.
Is there a license for this server?
Yes, the server is licensed under the MIT License, allowing you to use, modify, and distribute it.
Try in Playground
Server Config
{
  "mcpServers": {
    "aws-kb-retrieval": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-aws-kb-retrieval"
      ],
      "env": {
        "AWS_ACCESS_KEY_ID": "YOUR_ACCESS_KEY_HERE",
        "AWS_SECRET_ACCESS_KEY": "YOUR_SECRET_ACCESS_KEY_HERE",
        "AWS_REGION": "YOUR_AWS_REGION_HERE"
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