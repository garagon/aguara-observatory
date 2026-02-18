skills
/
browserbase
/
agent-browse
/
browser
browser
$
npx skills add https://github.com/browserbase/agent-browse --skill browser
SKILL.md
Browser Automation
Automate browser interactions using Stagehand CLI with Claude.
First: Environment Selection (Local vs Remote)
The skill automatically selects between local and remote browser environments:
If Browserbase API keys exist
(BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID in .env file): Uses remote Browserbase environment
If no Browserbase API keys
: Falls back to local Chrome browser
No user prompting
: The selection happens automatically based on available configuration
Setup (First Time Only)
Check
setup.json
in this directory. If
setupComplete: false
:
npm
install
# Install dependencies
npm
link
# Create global 'browser' command
Commands
All commands work identically in both modes:
browser navigate
<
url
>
# Go to URL
browser act
"<action>"
# Natural language action
browser extract
"<instruction>"
[
'{}'
]
# Extract data (optional schema)
browser observe
"<query>"
# Discover elements
browser screenshot
# Take screenshot
browser close
# Close browser
Quick Example
browser navigate https://example.com
browser act
"click the Sign In button"
browser extract
"get the page title"
browser close
Mode Comparison
Feature
Local
Browserbase
Speed
Faster
Slightly slower
Setup
Chrome required
API key required
Stealth mode
No
Yes
Proxy/CAPTCHA
No
Yes
Best for
Development
Production/scraping
Best Practices
Always navigate first
before interacting
View screenshots
after each command to verify
Be specific
in action descriptions
Close browser
when done
Troubleshooting
Chrome not found
: Install Chrome or use Browserbase mode
Action fails
: Use
browser observe
to discover available elements
Browserbase fails
: Verify API key and project ID are set
For detailed examples, see
EXAMPLES.md
.
For API reference, see
REFERENCE.md
.
Weekly Installs
78
Repository
browserbase/agent-browse
First Seen
13 days ago
Security Audits
Gen Agent Trust Hub
Pass
Socket
Pass
Snyk
Warn
Installed on
opencode
56
openclaw
52
claude-code
47
gemini-cli
39
codex
34
antigravity
31