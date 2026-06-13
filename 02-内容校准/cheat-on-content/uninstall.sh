#!/usr/bin/env bash
#
# cheat-on-content / uninstall.sh
#
# Removes the 13 sub-skills from ~/.claude/skills/.
#
# Does NOT touch any content project's data (.cheat-state.json, predictions/,
# rubric_notes.md, candidates.md, etc.) — those live in your content directories
# and uninstalling the skill leaves your work intact.
#
# To re-install: bash install.sh

set -euo pipefail

SKILLS=(
  cheat-init
  cheat-learn-from
  cheat-seed
  cheat-score
  cheat-predict
  cheat-shoot
  cheat-publish
  cheat-retro
  cheat-bump
  cheat-recommend
  cheat-trends
  cheat-status
  cheat-migrate
)

echo ""
echo "Removing cheat-on-content from ~/.claude/skills/"
echo ""

REMOVED=0
for s in "${SKILLS[@]}"; do
  TARGET="$HOME/.claude/skills/$s"
  if [[ -L "$TARGET" ]]; then
    rm "$TARGET"
    echo "  ✓ removed symlink:   $s"
    REMOVED=$((REMOVED + 1))
  elif [[ -d "$TARGET" ]]; then
    rm -rf "$TARGET"
    echo "  ✓ removed directory: $s"
    REMOVED=$((REMOVED + 1))
  else
    echo "  · not found:         $s (skipped)"
  fi
done

echo ""
if [[ $REMOVED -gt 0 ]]; then
  echo "✅ Uninstalled $REMOVED skill(s)."
else
  echo "ℹ️  Nothing to uninstall."
fi
echo ""
echo "Note: your content projects' data (predictions/, rubric_notes.md, .cheat-state.json,"
echo "      .cheat-hooks/, candidates.md, etc.) are NOT touched. They live in each content"
echo "      project directory. To clean a specific content project, delete those files manually."
echo ""
echo "To re-install: bash install.sh (from cheat-on-content source root)"
echo ""
