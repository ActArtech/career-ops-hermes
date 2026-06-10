#!/usr/bin/env bash
set -euo pipefail

# Career-Ops Hermes — Install skills into ~/.hermes/skills/
#
# Usage: ./install.sh [--force]
#   --force  Overwrite existing skills without confirmation

HERMES_SKILLS_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$PROJECT_DIR/skills"
FORCE="${1:-}"

echo "=== Career-Ops Hermes Installer ==="
echo "Project: $PROJECT_DIR"
echo "Hermes skills: $HERMES_SKILLS_DIR"
echo ""

if [ ! -d "$HERMES_SKILLS_DIR" ]; then
    echo "Creating Hermes skills directory: $HERMES_SKILLS_DIR"
    mkdir -p "$HERMES_SKILLS_DIR"
fi

COUNT=0
SKIPPED=0

for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    target_dir="$HERMES_SKILLS_DIR/$skill_name"
    
    if [ -d "$target_dir" ] && [ "$FORCE" != "--force" ]; then
        echo "  SKIP: $skill_name (already exists, use --force to overwrite)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    
    echo "  INSTALL: $skill_name"
    rm -rf "$target_dir"
    cp -r "$skill_dir" "$target_dir"
    COUNT=$((COUNT + 1))
done

echo ""
echo "Done: $COUNT skills installed, $SKIPPED skipped"
echo ""
echo "To use, open Hermes in this directory:"
echo "  cd $PROJECT_DIR && hermes"
echo ""
echo "The AGENTS.md file in this directory is auto-loaded by Hermes"
echo "when the working directory is set to this project."
