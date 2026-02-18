skills
/
anomalyco
/
opencode
/
bun-file-io
bun-file-io
$
npx skills add https://github.com/anomalyco/opencode --skill bun-file-io
SKILL.md
Use this when
Editing file I/O or scans in
packages/opencode
Handling directory operations or external tools
Bun file APIs (from Bun docs)
Bun.file(path)
is lazy; call
text
,
json
,
stream
,
arrayBuffer
,
bytes
,
exists
to read.
Metadata:
file.size
,
file.type
,
file.name
.
Bun.write(dest, input)
writes strings, buffers, Blobs, Responses, or files.
Bun.file(...).delete()
deletes a file.
file.writer()
returns a FileSink for incremental writes.
Bun.Glob
+
Array.fromAsync(glob.scan({ cwd, absolute, onlyFiles, dot }))
for scans.
Use
Bun.which
to find a binary, then
Bun.spawn
to run it.
Bun.readableStreamToText/Bytes/JSON
for stream output.
When to use node:fs
Use
node:fs/promises
for directories (
mkdir
,
readdir
, recursive operations).
Repo patterns
Prefer Bun APIs over Node
fs
for file access.
Check
Bun.file(...).exists()
before reading.
For binary/large files use
arrayBuffer()
and MIME checks via
file.type
.
Use
Bun.Glob
+
Array.fromAsync
for scans.
Decode tool stderr with
Bun.readableStreamToText
.
For large writes, use
Bun.write(Bun.file(path), text)
.
NOTE: Bun.file(...).exists() will return
false
if the value is a directory.
Use Filesystem.exists(...) instead if path can be file or directory
Quick checklist
Use Bun APIs first.
Use
path.join
/
path.resolve
for paths.
Prefer promise
.catch(...)
over
try/catch
when possible.
Weekly Installs
102
Repository
anomalyco/opencode
First Seen
Jan 22, 2026
Security Audits
Gen Agent Trust Hub
Pass
Socket
Pass
Snyk
Pass
Installed on
opencode
90
claude-code
64
gemini-cli
62
codex
61
github-copilot
56
antigravity
45