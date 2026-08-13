#!/usr/bin/env bash
# Deploy the confluence-search Claude agent skill.
#
# This script does ONE job: put the skill where Claude Code will find it. It
# never touches credentials. Tokens are per-user and belong to a separate
# command, `confluence-login`, which ships inside the skill so the people who
# need it have it even if they never see this repo.
#
#   maintainer, once   clone this repo somewhere group-readable
#   maintainer/user    ./install.sh              deploy the skill
#   each user, once    confluence-login          install their own token
#
# The code is shared; the credential never is.
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
usage: install.sh [options]

Deploys the skill. Does not touch tokens — see 'confluence-login' for that.

  --copy       copy the skill instead of symlinking it
  --dir DIR    deploy into DIR instead of \$CLAUDE_SKILLS_DIR or ~/.claude/skills
  --force      replace whatever is already at the destination
  --uninstall  remove the deployed skill (leaves your token alone)
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
    echo "not deployed: $DEST"
  elif [ -L "$DEST" ] || [ "$FORCE" -eq 1 ]; then
    rm -rf "$DEST"
    echo "removed $DEST"
  else
    echo "install.sh: $DEST is a real directory, not our symlink." >&2
    echo "            re-run with --force if you are sure." >&2
    exit 1
  fi
  echo "note: your token file was left in place. Remove it by hand if you"
  echo "      meant to revoke access on this machine."
  exit 0
fi

# --- sanity: is the source actually here and intact? ------------------------
for f in "$SRC/SKILL.md" "$SRC/scripts/cqlsearch.py" "$SRC/scripts/confluence-login"; do
  [ -f "$f" ] || { echo "install.sh: missing $f — run this from the clone" >&2; exit 1; }
done
chmod +x "$SRC/scripts/cqlsearch.py" "$SRC/scripts/confluence-login" 2>/dev/null || true

mkdir -p "$DEST_DIR"

# --- refuse to clobber someone else's skill ---------------------------------
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  if [ -L "$DEST" ] && [ "$(readlink "$DEST")" = "$SRC" ]; then
    echo "already deployed: $DEST -> $SRC"
  elif [ "$FORCE" -ne 1 ]; then
    echo "install.sh: $DEST already exists." >&2
    echo "            re-run with --force to replace it." >&2
    exit 1
  else
    rm -rf "$DEST"
  fi
fi

if [ ! -e "$DEST" ] && [ ! -L "$DEST" ]; then
  case "$MODE" in
    symlink) ln -s "$SRC" "$DEST"; echo "deployed $DEST -> $SRC" ;;
    copy)    cp -R "$SRC" "$DEST"; echo "deployed $SRC -> $DEST (copy)" ;;
  esac
fi

# --- environment notes ------------------------------------------------------
# uv is the supported path: the skill's PEP 723 metadata pins python>=3.9 and uv
# provisions exactly that. A bare python3 is often the system one — 3.6 on these
# login nodes — which cannot even parse the script.
if ! command -v uv >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1 &&
     python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    :
  else
    echo
    echo "warning: no usable interpreter."
    echo "         uv is not installed, and python3 is $(python3 -V 2>&1 || echo absent),"
    echo "         but this skill needs python >= 3.9. The skill is deployed but"
    echo "         will not run until you install uv (https://docs.astral.sh/uv/)."
  fi
elif [ -z "${UV_CACHE_DIR:-}" ]; then
  echo
  echo "note: UV_CACHE_DIR is unset, so uv caches under ~/.cache/uv."
  echo "      On quota'd home directories set UV_CACHE_DIR=/tmp/uv-cache-\$USER."
fi

cat <<EOF

Deployed. Each user now installs their own token — once, on their own account:

  $DEST/scripts/confluence-login

Search results are filtered by whoever's token is in play, so this step cannot
be done for them.
EOF
