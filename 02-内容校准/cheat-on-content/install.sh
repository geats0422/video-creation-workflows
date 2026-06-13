#!/usr/bin/env bash
#
# cheat-on-content / install.sh
#
# Symlinks the 13 sub-skills into ~/.claude/skills/ so Claude Code can find them
# globally. Re-runnable safely (sf flags overwrite existing links).
#
# After install, in any content project directory: open Claude Code → say "初始化"
# → /cheat-init runs the onboarding.
#
# To uninstall: bash uninstall.sh
#
# Usage:
#   bash install.sh                    # symlink (default; dev-friendly, changes reflect immediately)
#   bash install.sh --copy             # copy instead of symlink (frozen version, dev changes ignored)
#   bash install.sh --reinstall-hooks <project-dir>
#                                      # rewrite hook scripts in an existing user project's .cheat-hooks/
#                                      # (use after git pull when CHANGELOG mentions hook script changes;
#                                      #  does NOT touch .cheat-state.json or any user data)

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

# Resolve the directory containing THIS script (the source root) — needed early for both modes
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

MODE="symlink"

# --- --reinstall-hooks branch: rewrite a user project's hook scripts only ---
if [[ "${1:-}" == "--reinstall-hooks" ]]; then
  PROJECT_DIR="${2:-}"
  if [[ -z "$PROJECT_DIR" ]]; then
    echo "❌ Usage: bash install.sh --reinstall-hooks <path-to-user-project>"
    echo "   The user project must already have been initialized via /cheat-init."
    exit 1
  fi
  if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "❌ Project dir not found: $PROJECT_DIR"
    exit 1
  fi
  if [[ ! -f "$PROJECT_DIR/.cheat-state.json" ]]; then
    echo "❌ $PROJECT_DIR is not a cheat-on-content project (no .cheat-state.json)."
    echo "   Run /cheat-init in that directory first."
    exit 1
  fi

  HOOK_DST="$PROJECT_DIR/.cheat-hooks"
  mkdir -p "$HOOK_DST"

  echo ""
  echo "Reinstalling hook scripts in: $PROJECT_DIR"
  echo "  source: $SCRIPT_DIR/hooks/"
  echo ""

  for hook_script in prediction-immutability.sh session-start.sh log-event.sh; do
    if [[ -f "$SCRIPT_DIR/hooks/$hook_script" ]]; then
      cp "$SCRIPT_DIR/hooks/$hook_script" "$HOOK_DST/$hook_script"
      chmod +x "$HOOK_DST/$hook_script"
      echo "  ✓ updated: .cheat-hooks/$hook_script"
    else
      echo "  ⚠️  missing in source: hooks/$hook_script (skipped)"
    fi
  done

  echo ""
  echo "✅ Hook scripts reinstalled."
  echo ""
  echo "Note: This did NOT touch:"
  echo "  - .cheat-state.json (your data)"
  echo "  - .claude/settings.json (hook registration — should still point at .cheat-hooks/)"
  echo "  - rubric_notes.md / predictions/ / videos/ (your work)"
  echo ""
  echo "If schema also changed (CHANGELOG marks BREAKING), additionally run /cheat-migrate"
  echo "in Claude Code from your project directory."
  echo ""
  exit 0
fi

if [[ "${1:-}" == "--copy" ]]; then
  MODE="copy"
fi

# Sanity check: confirm we're in the cheat-on-content root
for s in "${SKILLS[@]}"; do
  if [[ ! -f "$SCRIPT_DIR/skills/$s/SKILL.md" ]]; then
    echo "❌ Missing: $SCRIPT_DIR/skills/$s/SKILL.md"
    echo "   Are you running install.sh from the cheat-on-content root?"
    exit 1
  fi
done

# Ensure ~/.claude/skills exists
mkdir -p "$HOME/.claude/skills"

echo ""
echo "Installing cheat-on-content (mode: $MODE)"
echo "  source: $SCRIPT_DIR"
echo "  target: $HOME/.claude/skills/"
echo ""

# Detect any existing installation that conflicts
WARNED=0
for s in "${SKILLS[@]}"; do
  TARGET="$HOME/.claude/skills/$s"
  if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    if [[ -L "$TARGET" ]]; then
      EXISTING=$(readlink "$TARGET")
      if [[ "$EXISTING" != "$SCRIPT_DIR/skills/$s" ]]; then
        echo "⚠️  $TARGET already symlinked to: $EXISTING"
        WARNED=1
      fi
    else
      echo "⚠️  $TARGET exists (not a symlink) — will be overwritten"
      WARNED=1
    fi
  fi
done

if [[ $WARNED -eq 1 ]]; then
  echo ""
  read -p "Continue and overwrite? (y/N) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

# Install each sub-skill
for s in "${SKILLS[@]}"; do
  SRC="$SCRIPT_DIR/skills/$s"
  DST="$HOME/.claude/skills/$s"

  # Remove any existing entry first (to allow overwriting non-symlink dirs)
  if [[ -e "$DST" || -L "$DST" ]]; then
    rm -rf "$DST"
  fi

  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$SRC" "$DST"
    echo "  ✓ symlinked: $s"
  else
    cp -R "$SRC" "$DST"
    echo "  ✓ copied:    $s"
  fi
done

echo ""
echo "✅ Install complete!"
echo ""
echo "Next steps:"
echo "  1. cd into your content project (or create one):"
echo "       mkdir ~/my-channel && cd ~/my-channel"
echo ""
echo "  2. Open Claude Code in that directory"
echo ""
echo "  3. In the chat, say:"
echo "       初始化"
echo "       (or: 初始化 cheat-on-content)"
echo ""
echo "Verify install: ls -la ~/.claude/skills/ | grep cheat"
echo ""
if [[ "$MODE" == "symlink" ]]; then
  echo "ℹ️  Mode: symlink — edits to source SKILL.md files take effect immediately."
  echo "   To switch to frozen copy: bash install.sh --copy"
else
  echo "ℹ️  Mode: copy — frozen at install time. Re-run install.sh to update."
fi
echo ""
