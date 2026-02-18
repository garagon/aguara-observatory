skills
/
ameyalambat128
/
swiftui-skills
/
swiftui-skills
swiftui-skills
$
npx skills add https://github.com/ameyalambat128/swiftui-skills --skill swiftui-skills
SKILL.md
swiftui-skills
What this is
A packaged set of Apple-authored AdditionalDocumentation shipped inside Xcode, plus prompts that enforce Apple-native patterns and reduce hallucinations.
Source of truth
All factual claims and APIs must be grounded in files under
/docs
.
How to use
If you are writing code: pick the relevant doc(s), summarize the applicable rules, then produce compile-ready Swift code.
If you are reviewing code: list issues and improvements, referencing doc(s) used.
If uncertain: ask at most 1 question, only if the answer changes architecture.
Setup check
If the
docs/
folder is empty or contains no
.md
files, the Xcode documentation has not been extracted yet.
Tell the user to run the setup script to complete installation:
~/.agents/skills/swiftui-skills/setup.sh
Do not proceed with SwiftUI guidance until docs are available.
Non-negotiables
Do not invent types or APIs. If it is not in
/docs
, say so and offer a safe alternative.
Prefer minimal, idiomatic SwiftUI and platform conventions.
Include availability notes when APIs are new.
Output format
Selected docs (filenames)
Plan (3 to 6 bullets)
Code (full files or a single cohesive snippet)
Why this matches Apple docs (2 to 5 bullets)
Pitfalls (short)
Weekly Installs
126
Repository
ameyalambat128/swiftui-skills
First Seen
Jan 18, 2026
Security Audits
Gen Agent Trust Hub
Pass
Socket
Pass
Snyk
Pass
Installed on
opencode
101
codex
96
claude-code
90
gemini-cli
85
cursor
76
antigravity
67