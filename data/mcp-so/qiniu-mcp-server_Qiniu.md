Toggle Sidebar
Submit
English
Home
Servers
Qiniu MCP Server
Qiniu MCP Server
@
Qiniu
Visit Server
10 months ago
#
storage
#
image-processing
基于七牛云产品构建的 Model Context Protocol (MCP) Server，支持用户在 AI 大模型客户端的上下文中通过该 MCP Server 来访问七牛云存储资源、利用 Dora 服务进行图片操作等。

如果有什么需求欢迎在下方评论，您也可以在 github 仓库中提 issue。
Overview
Tools
Comments
Overview
What is Qiniu MCP Server?
Qiniu MCP Server is an S3 resource server based on the Model Control Protocol (MCP) that supports access and management of Qiniu Cloud Kodo storage services.
How to use Qiniu MCP Server?
To use Qiniu MCP Server, clone the repository, set up a virtual environment, install dependencies, configure environment variables, and start the server using the provided commands.
Key features of Qiniu MCP Server?
Supports listing storage buckets.
Supports listing objects within buckets.
Supports reading object content.
Use cases of Qiniu MCP Server?
Managing cloud storage resources efficiently.
Integrating with web applications for object storage management.
Accessing and retrieving data from Qiniu Cloud Kodo.
FAQ from Qiniu MCP Server?
What are the prerequisites for using Qiniu MCP Server?
Python 3.12 or higher and the uv package manager are required.
How do I install the server?
Clone the repository, create a virtual environment, and install dependencies using the provided commands.
What types of files does the server support?
The server supports text files (Markdown, plain text) and image files (all standard formats).
Try in Playground
Server Config
{
  "mcpServers": {
    "qiniu": {
      "command": "uvx",
      "args": [
        "qiniu-mcp-server"
      ],
      "env": {
        "QINIU_ACCESS_KEY": "YOUR_ACCESS_KEY",
        "QINIU_SECRET_KEY": "YOUR_SECRET_KEY",
        "QINIU_REGION_NAME": "YOUR_REGION_NAME",
        "QINIU_ENDPOINT_URL": "YOUR_ENDPOINT_URL",
        "QINIU_BUCKETS": ""
      },
      "disabled": false
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