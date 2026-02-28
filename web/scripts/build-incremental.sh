#!/usr/bin/env bash
# Incremental build for Aguara Watch.
#
# Instead of regenerating 43K+ skill pages on every build, this script:
# 1. Compares skill content hashes to find what actually changed
# 2. Tells Astro to only generate pages for changed skills
# 3. Merges newly built pages with cached pages from the previous build
#
# Cache directory: web/.cache/skills/ (persisted by CI between runs)
#
# Usage:
#   cd web && bash scripts/build-incremental.sh
#   FORCE_FULL=1 bash scripts/build-incremental.sh  # Force full rebuild

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WEB_DIR="$(dirname "$SCRIPT_DIR")"
cd "$WEB_DIR"

CACHE_DIR="$WEB_DIR/.cache/skills"
PREV_HASHES="$WEB_DIR/.cache/.skill_hashes.prev.json"
CURR_HASHES="$WEB_DIR/public/api/v1/.skill_hashes.json"
CHANGED_SKILLS="$WEB_DIR/.changed_skills.json"
LAYOUT_HASH_FILE="$WEB_DIR/.cache/.layout_hash"

mkdir -p "$CACHE_DIR" "$WEB_DIR/.cache"

# --- Step 1: Check if layout files changed (forces full rebuild) ---
layout_files=(
  "src/layouts/Base.astro"
  "src/components/Header.astro"
  "src/components/Footer.astro"
  "src/pages/skills/[registry]/[...slug].astro"
  "src/lib/constants.ts"
)
layout_hash=""
for f in "${layout_files[@]}"; do
  if [ -f "$f" ]; then
    layout_hash+="$(shasum -a 256 "$f" | cut -d' ' -f1)"
  fi
done
layout_hash=$(echo -n "$layout_hash" | shasum -a 256 | cut -d' ' -f1)

prev_layout_hash=""
if [ -f "$LAYOUT_HASH_FILE" ]; then
  prev_layout_hash=$(cat "$LAYOUT_HASH_FILE")
fi

# --- Step 2: Determine build mode ---
if [ "${FORCE_FULL:-}" = "1" ]; then
  echo "[build] FORCE_FULL=1 — full rebuild"
  rm -f "$CHANGED_SKILLS"
elif [ ! -f "$PREV_HASHES" ]; then
  echo "[build] No previous hashes — full rebuild"
  rm -f "$CHANGED_SKILLS"
elif [ "$layout_hash" != "$prev_layout_hash" ]; then
  echo "[build] Layout files changed — full rebuild"
  rm -rf "$CACHE_DIR"
  mkdir -p "$CACHE_DIR"
  rm -f "$CHANGED_SKILLS"
elif [ ! -f "$CURR_HASHES" ]; then
  echo "[build] No current hashes — full rebuild"
  rm -f "$CHANGED_SKILLS"
else
  # Diff hashes to find changed skills
  echo "[build] Comparing skill hashes..."
  changed=$(python3 -c "
import json, sys

prev = json.load(open('$PREV_HASHES'))
curr = json.load(open('$CURR_HASHES'))

changed = []
for key, h in curr.items():
    if prev.get(key) != h:
        reg, slug = key.split('/', 1)
        changed.append({'registry': reg, 'slug': slug})

# Also handle deleted skills (in prev but not curr) — no HTML to generate, just note
deleted = len(prev) - len(set(prev) & set(curr))
print(json.dumps({'changed': changed, 'deleted': deleted}))
" 2>/dev/null)

  n_changed=$(echo "$changed" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['changed']))")
  n_deleted=$(echo "$changed" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['deleted'])")

  if [ "$n_changed" = "0" ]; then
    echo "[build] No skill data changed (${n_deleted} deleted). Building chrome pages only."
    echo "[]" > "$CHANGED_SKILLS"
  else
    echo "[build] ${n_changed} skills changed, ${n_deleted} deleted — incremental build"
    echo "$changed" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['changed']))" > "$CHANGED_SKILLS"
  fi
fi

# --- Step 3: Save cached skill pages before Astro clears dist/ ---
if [ -d "dist/skills" ] && [ "$(ls -A dist/skills 2>/dev/null)" ]; then
  echo "[build] Saving existing dist/skills/ to cache..."
  rsync -a dist/skills/ "$CACHE_DIR/"
fi

# --- Step 4: Run Astro build ---
echo "[build] Running astro build..."
npm run build

# --- Step 5: Merge cached pages back (don't overwrite newly generated ones) ---
if [ -d "$CACHE_DIR" ] && [ "$(ls -A "$CACHE_DIR" 2>/dev/null)" ]; then
  echo "[build] Merging cached skill pages into dist/..."
  # rsync with --ignore-existing: only copy files that DON'T already exist in dist/
  rsync -a --ignore-existing "$CACHE_DIR/" dist/skills/
fi

# Count total pages
total=$(find dist/skills -name "index.html" 2>/dev/null | wc -l | tr -d ' ')
echo "[build] Total skill pages in dist/: ${total}"

# --- Step 6: Update cache for next run ---
echo "[build] Updating cache..."
rsync -a dist/skills/ "$CACHE_DIR/"

if [ -f "$CURR_HASHES" ]; then
  cp "$CURR_HASHES" "$PREV_HASHES"
fi
echo "$layout_hash" > "$LAYOUT_HASH_FILE"

# Clean up
rm -f "$CHANGED_SKILLS"

echo "[build] Done."
