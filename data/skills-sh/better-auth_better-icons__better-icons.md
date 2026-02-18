skills
/
better-auth
/
better-icons
/
better-icons
better-icons
$
npx skills add https://github.com/better-auth/better-icons --skill better-icons
SKILL.md
Better Icons
Search and retrieve icons from 200+ libraries via Iconify.
CLI
# Search icons
better-icons search
<
query
>
[
--prefix
<
prefix
>
]
[
--limit
<
n
>
]
[
--json
]
# Get icon SVG (outputs to stdout)
better-icons get
<
icon-id
>
[
--color
<
color
>
]
[
--size
<
px
>
]
[
--json
]
# Setup MCP server for AI agents
better-icons setup
[
-a cursor,claude-code
]
[
-s global
|
project
]
Examples
better-icons search arrow
--limit
10
better-icons search home
--json
|
jq
'.icons[0]'
better-icons get lucide:home
>
icon.svg
better-icons get mdi:home
--color
'#333'
--json
Icon ID Format
prefix:name
- e.g.,
lucide:home
,
mdi:arrow-right
,
heroicons:check
Popular Collections
lucide
,
mdi
,
heroicons
,
tabler
,
ph
,
ri
,
solar
,
iconamoon
MCP Tools (for AI agents)
Tool
Description
search_icons
Search across all libraries
get_icon
Get single icon SVG
get_icons
Batch retrieve multiple icons
list_collections
Browse available icon sets
recommend_icons
Smart recommendations for use cases
find_similar_icons
Find variations across collections
sync_icon
Add icon to project file
scan_project_icons
List icons in project
TypeScript Interfaces
interface
SearchIcons
{
query
:
string
limit
?
:
number
// 1-999, default 32
prefix
?
:
string
// e.g., 'mdi', 'lucide'
category
?
:
string
// e.g., 'General', 'Emoji'
}
interface
GetIcon
{
icon_id
:
string
// 'prefix:name' format
color
?
:
string
// e.g., '#ff0000', 'currentColor'
size
?
:
number
// pixels
}
interface
GetIcons
{
icon_ids
:
string
[
]
// max 20
color
?
:
string
size
?
:
number
}
interface
RecommendIcons
{
use_case
:
string
// e.g., 'navigation menu'
style
?
:
'solid'
|
'outline'
|
'any'
limit
?
:
number
// default 10
}
interface
SyncIcon
{
icons_file
:
string
// absolute path
framework
:
'react'
|
'vue'
|
'svelte'
|
'solid'
|
'svg'
icon_id
:
string
component_name
?
:
string
}
API
All icons from
https://api.iconify.design
Weekly Installs
500
Repository
better-auth/better-icons
First Seen
Jan 22, 2026
Security Audits
Gen Agent Trust Hub
Pass
Socket
Pass
Snyk
Warn
Installed on
opencode
373
claude-code
362
gemini-cli
345
codex
318
antigravity
270
cursor
255