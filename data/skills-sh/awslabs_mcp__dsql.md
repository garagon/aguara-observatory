skills
/
awslabs
/
mcp
/
dsql
dsql
$
npx skills add https://github.com/awslabs/mcp --skill dsql
SKILL.md
Amazon Aurora DSQL Skill
Aurora DSQL is a serverless, PostgreSQL-compatible distributed SQL database. This skill provides direct database interaction via MCP tools, schema management, migration support, and multi-tenant patterns.
Key capabilities:
Direct query execution via MCP tools
Schema management with DSQL constraints
Migration support and safe schema evolution
Multi-tenant isolation patterns
IAM-based authentication
Reference Files
Load these files as needed for detailed guidance:
development-guide.md
When:
ALWAYS load before implementing schema changes or database operations
Contains:
DDL rules, connection patterns, transaction limits, security best practices
MCP:
mcp-setup.md
When:
Always load for guidance using or updating the DSQL MCP server
Contains:
Instructions for setting up the DSQL MCP server with 2 configuration options as
sampled in
.mcp.json
Documentation-Tools Only
Database Operations (requires a cluster endpoint)
mcp-tools.md
When:
Load when you need detailed MCP tool syntax and examples
Contains:
Tool parameters, detailed examples, usage patterns
language.md
When:
MUST load when making language-specific implementation choices
Contains:
Driver selection, framework patterns, connection code for Python/JS/Go/Java/Rust
dsql-examples.md
When:
Load when looking for specific implementation examples
Contains:
Code examples, repository patterns, multi-tenant implementations
troubleshooting.md
When:
Load when debugging errors or unexpected behavior
Contains:
Common pitfalls, error messages, solutions
onboarding.md
When:
User explicitly requests to "Get started with DSQL" or similar phrase
Contains:
Interactive step-by-step guide for new users
ddl-migrations.md
When:
MUST load when trying to perform DROP COLUMN, RENAME COLUMN, ALTER COLUMN TYPE, or DROP CONSTRAINT functionality
Contains:
Table recreation patterns, batched migration for large tables, data validation
MCP Tools Available
The
aurora-dsql
MCP server provides these tools:
Database Operations:
readonly_query
- Execute SELECT queries (returns list of dicts)
transact
- Execute DDL/DML statements in transaction (takes list of SQL statements)
get_schema
- Get table structure for a specific table
Documentation & Knowledge:
4.
dsql_search_documentation
- Search Aurora DSQL documentation
5.
dsql_read_documentation
- Read specific documentation pages
6.
dsql_recommend
- Get DSQL best practice recommendations
Note:
There is no
list_tables
tool. Use
readonly_query
with information_schema.
See
mcp-setup.md
for detailed setup instructions.
See
mcp-tools.md
for detailed usage and examples.
CLI Scripts Available
Bash scripts for cluster management and direct psql connections. All scripts are located in
scripts/
.
Cluster Management:
create-cluster.sh
- Create new DSQL cluster with optional tags
delete-cluster.sh
- Delete cluster with confirmation prompt
list-clusters.sh
- List all clusters in a region
cluster-info.sh
- Get detailed cluster information
Database Connection:
psql-connect.sh
- Connect to DSQL using psql with automatic IAM auth token generation
Quick example:
./scripts/create-cluster.sh
--region
us-east-1
export
CLUSTER
=
abc123def456
./scripts/psql-connect.sh
See
scripts/README.md
for detailed usage.
Quick Start
1. List tables and explore schema
Use readonly_query with information_schema to list tables
Use get_schema to understand table structure
2. Query data
Use readonly_query for SELECT queries
Always include tenant_id in WHERE clause for multi-tenant apps
Validate inputs carefully (no parameterized queries available)
3. Execute schema changes
Use transact tool with list of SQL statements
Follow one-DDL-per-transaction rule
Always use CREATE INDEX ASYNC in separate transaction
Common Workflows
Workflow 1: Create Multi-Tenant Schema
Goal:
Create a new table with proper tenant isolation
Steps:
Create main table with tenant_id column using transact
Create async index on tenant_id in separate transact call
Create composite indexes for common query patterns (separate transact calls)
Verify schema with get_schema
Critical rules:
Include tenant_id in all tables
Use CREATE INDEX ASYNC (never synchronous)
Each DDL in its own transact call:
transact(["CREATE TABLE ..."])
Store arrays/JSON as TEXT
Workflow 2: Safe Data Migration
Goal:
Add a new column with defaults safely
Steps:
Add column using transact:
transact(["ALTER TABLE ... ADD COLUMN ..."])
Populate existing rows with UPDATE in separate transact calls (batched under 3,000 rows)
Verify migration with readonly_query using COUNT
Create async index for new column using transact if needed
Critical rules:
Add column first, populate later
Never add DEFAULT in ALTER TABLE
Batch updates under 3,000 rows in separate transact calls
Each ALTER TABLE in its own transaction
Workflow 3: Application-Layer Referential Integrity
Goal:
Safely insert/delete records with parent-child relationships
Steps for INSERT:
Validate parent exists with readonly_query
Throw error if parent not found
Insert child record using transact with parent reference
Steps for DELETE:
Check for dependent records with readonly_query (COUNT)
Return error if dependents exist
Delete record using transact if safe
Workflow 4: Query with Tenant Isolation
Goal:
Retrieve data scoped to a specific tenant
Steps:
Always include tenant_id in WHERE clause
Validate and sanitize tenant_id input (no parameterized queries available!)
Use readonly_query with validated tenant_id
Never allow cross-tenant data access
Critical rules:
Validate ALL inputs before building SQL (SQL injection risk!)
ALL queries include WHERE tenant_id = 'validated-value'
Reject cross-tenant access at application layer
Use allowlists or regex validation for tenant IDs
Workflow 5: Table Recreation DDL Migration
Goal:
Perform DROP COLUMN, RENAME COLUMN, ALTER COLUMN TYPE, or DROP CONSTRAINT using the table recreation pattern.
MUST load
ddl-migrations.md
for detailed guidance.
Steps:
MUST validate table exists and get row count with
readonly_query
MUST get current schema with
get_schema
MUST create new table with desired structure using
transact
MUST migrate data (batched in 500-1,000 row chunks for tables > 3,000 rows)
MUST verify row counts match before proceeding
MUST swap tables: drop original, rename new
MUST recreate indexes using
CREATE INDEX ASYNC
Rules:
MUST use batching for tables exceeding 3,000 rows
PREFER batches of 500-1,000 rows for optimal throughput
MUST validate data compatibility before type changes (abort if incompatible)
MUST NOT drop original table until new table is verified
MUST recreate all indexes after table swap using ASYNC
Best Practices
SHOULD read guidelines first
- Check
development_guide.md
before making schema changes
SHOULD use preferred language patterns
- Check
language.md
SHOULD Execute queries directly
- PREFER MCP tools for ad-hoc queries
REQUIRED: Follow DDL Guidelines
- Refer to
DDL Rules
SHALL repeatedly generate fresh tokens
- Refer to
Connection Limits
ALWAYS use ASYNC indexes
-
CREATE INDEX ASYNC
is mandatory
MUST Serialize arrays/JSON as TEXT
- Store arrays/JSON as TEXT (comma separated, JSON.stringify)
ALWAYS Batch under 3,000 rows
- maintain transaction limits
REQUIRED: Use parameterized queries
- Prevent SQL injection with $1, $2 placeholders
MUST follow correct Application Layer Patterns
- when multi-tenant isolation or application referential itegrity are required; refer to
Application Layer Patterns
REQUIRED use DELETE for truncation
- DELETE is the only supported operation for truncation
SHOULD test any migrations
- Verify DDL on dev clusters before production
Plan for Horizontal Scale
- DSQL is designed to optimize for massive scales without latency drops; refer to
Horizontal Scaling
SHOULD use connection pooling in production applications
- Refer to
Connection Pooling
SHOULD debug with the troubleshooting guide:
- Always refer to the resources and guidelines in
troubleshooting.md
Additional Resources
Aurora DSQL Documentation
Code Samples Repository
PostgreSQL Compatibility
IAM Authentication Guide
CloudFormation Resource
Weekly Installs
61
Repository
awslabs/mcp
First Seen
Jan 22, 2026
Security Audits
Gen Agent Trust Hub
Fail
Socket
Fail
Snyk
Warn
Installed on
claude-code
48
kiro-cli
40
opencode
32
codex
28
gemini-cli
27
github-copilot
20