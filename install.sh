#!/usr/bin/env bash
# Install the confluence-search Claude agent skill.
#
# By default this symlinks skills/confluence-search/ into ~/.claude/skills/, so
# edits in the clone take effect immediately. Use --copy when the skills
# directory lives somewhere that cannot follow a link into this checkout.
set -euo pipefail

SKILL_NAME="confluence-search"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
SRC="$REPO_ROOT/skills/$SKILL_NAME"
DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MODE="symlink"
FORCE=0
UNINSTALL=0

usage() {
  cat <<EOF
usage: install.sh [--copy] [--dir DIR] [--force] [--uninstall]

  --copy       copy the skill instead of symlinking it
  --dir DIR    install into DIR instead of \$CLAUDE_SKILLS_DIR or ~/.claude/skills
  --force      replace whatever is already at the destination
  --uninstall  remove the installed skill
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --copy)      MODE="copy"; shift ;;
    --dir)       DEST_DIR="${2:?--dir needs a directory}"; shift 2 ;;
    --force)     FORCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *)           echo "install.sh: unknown option '$1'" >&2; usage >&2; exit 2 ;;
  esac
done

DEST="$DEST_DIR/$SKILL_NAME"

if [ "$UNINSTALL" -eq 1 ]; then
  if [ ! -e "$DEST" ] && [ ! -L "$DEST" ]; then
    echo "not installed: $DEST"
    exit 0
  fi
  if [ -L "$DEST" ] || [ "$FORCE" -eq 1 ]; then
    rm -rf "$DEST"
    echo "removed $DEST"
  else
    echo "install.sh: $DEST is a real directory, not our symlink." >&2
    echo "            re-run with --force if you are sure." >&2
    exit 1
  fi
  exit 0
fi

# --- sanity: is the source actually here and intact? ------------------------
for f in "$SRC/SKILL.md" "$SRC/scripts/cqlsearch.py"; do
  [ -f "$f" ] || { echo "install.sh: missing $f — run this from the clone" >&2; exit 1; }
done
chmod +x "$SRC/scripts/cqlsearch.py" 2>/dev/null || true

mkdir -p "$DEST_DIR"

# --- refuse to clobber someone else's skill ---------------------------------
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  if [ -L "$DEST" ] && [ "$(readlink "$DEST")" = "$SRC" ]; then
    echo "already installed: $DEST -> $SRC"
    exit 0
  fi
  if [ "$FORCE" -ne 1 ]; then
    echo "install.sh: $DEST already exists." >&2
    echo "            re-run with --force to replace it." >&2
    exit 1
  fi
  rm -rf "$DEST"
fi

case "$MODE" in
  symlink) ln -s "$SRC" "$DEST"; echo "linked $DEST -> $SRC" ;;
  copy)    cp -R "$SRC" "$DEST"; echo "copied $SRC -> $DEST" ;;
esac

# --- post-install checks ----------------------------------------------------
echo
if command -v uv >/dev/null 2>&1; then
  if [ -z "${UV_CACHE_DIR:-}" ]; then
    echo "note: UV_CACHE_DIR is unset, so uv caches under ~/.cache/uv."
    echo "      On quota'd home directories set e.g. UV_CACHE_DIR=/tmp/uv-cache-\$USER."
  fi
else
  echo "note: uv not found. cqlsearch.py is standard-library-only, so"
  echo "      'python3 $DEST/scripts/cqlsearch.py ...' works without it."
fi

TOKEN_FILE="${CONFLUENCE_TOKEN_FILE:-/sdf/group/lcls/ds/dm/apps/dev/env/confluence.dat}"
if [ -z "${CONFLUENCE_TOKEN:-}" ] && [ ! -r "$TOKEN_FILE" ]; then
  echo "note: no readable token at $TOKEN_FILE."
  echo "      Set CONFLUENCE_TOKEN or CONFLUENCE_TOKEN_FILE before searching."
fi

echo
echo "installed. Verify with:"
echo "  python3 $DEST/scripts/cqlsearch.py spaces --filter PSDM"
