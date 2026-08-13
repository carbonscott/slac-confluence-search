#!/usr/bin/env bash
# Install the confluence-search Claude agent skill, and set up your token.
#
# Designed for a central deployment: one clone in a shared directory, every user
# runs this to symlink it into their own ~/.claude/skills/ and to install their
# own personal access token under their own home. The code is shared; the
# credential never is.
set -euo pipefail

SKILL_NAME="confluence-search"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
SRC="$REPO_ROOT/skills/$SKILL_NAME"
DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MODE="symlink"
FORCE=0
UNINSTALL=0
DO_TOKEN="auto"          # auto | force | skip
TOKEN_FROM=""
VERIFY=1

# $HOME is inherited and lies under sudo/cron; passwd does not. Keep this in
# step with home_dir() in cqlsearch.py or the two will disagree on the path.
user_home() {
  local h
  h="$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6 || true)"
  printf '%s' "${h:-$HOME}"
}
TOKEN_FILE="${CONFLUENCE_TOKEN_FILE:-${XDG_CONFIG_HOME:-$(user_home)/.config}/$SKILL_NAME/token}"
CONFLUENCE_URL="${CONFLUENCE_URL:-https://confluence.slac.stanford.edu}"
PAT_URL="$CONFLUENCE_URL/plugins/personalaccesstokens/usertokens.action"

usage() {
  cat <<EOF
usage: install.sh [options]

  --token          (re)install your personal access token, overwriting any
                   existing one. Reads from stdin when not on a terminal.
  --token-from F   take the token from file F instead of prompting
  --no-token       install the skill only, leave credentials alone
  --no-verify      skip the live call that confirms the token works

  --copy           copy the skill instead of symlinking it
  --dir DIR        install into DIR instead of \$CLAUDE_SKILLS_DIR or ~/.claude/skills
  --force          replace whatever is already at the destination
  --uninstall      remove the installed skill (leaves your token in place)

Token file: $TOKEN_FILE
Mint one at: $PAT_URL
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --token)      DO_TOKEN="force"; shift ;;
    --token-from) TOKEN_FROM="${2:?--token-from needs a file}"; DO_TOKEN="force"; shift 2 ;;
    --no-token)   DO_TOKEN="skip"; shift ;;
    --no-verify)  VERIFY=0; shift ;;
    --copy)       MODE="copy"; shift ;;
    --dir)        DEST_DIR="${2:?--dir needs a directory}"; shift 2 ;;
    --force)      FORCE=1; shift ;;
    --uninstall)  UNINSTALL=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    *)            echo "install.sh: unknown option '$1'" >&2; usage >&2; exit 2 ;;
  esac
done

DEST="$DEST_DIR/$SKILL_NAME"

if [ "$UNINSTALL" -eq 1 ]; then
  if [ ! -e "$DEST" ] && [ ! -L "$DEST" ]; then
    echo "not installed: $DEST"
  elif [ -L "$DEST" ] || [ "$FORCE" -eq 1 ]; then
    rm -rf "$DEST"
    echo "removed $DEST"
  else
    echo "install.sh: $DEST is a real directory, not our symlink." >&2
    echo "            re-run with --force if you are sure." >&2
    exit 1
  fi
  echo "note: your token at $TOKEN_FILE was left in place."
  exit 0
fi

# --- sanity: is the source actually here and intact? ------------------------
for f in "$SRC/SKILL.md" "$SRC/scripts/cqlsearch.py"; do
  [ -f "$f" ] || { echo "install.sh: missing $f — run this from the clone" >&2; exit 1; }
done
chmod +x "$SRC/scripts/cqlsearch.py" 2>/dev/null || true   # no-op on a read-only central clone

mkdir -p "$DEST_DIR"

# --- refuse to clobber someone else's skill ---------------------------------
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  if [ -L "$DEST" ] && [ "$(readlink "$DEST")" = "$SRC" ]; then
    echo "already linked: $DEST -> $SRC"
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
    symlink) ln -s "$SRC" "$DEST"; echo "linked $DEST -> $SRC" ;;
    copy)    cp -R "$SRC" "$DEST"; echo "copied $SRC -> $DEST" ;;
  esac
fi

# --- the token --------------------------------------------------------------
have_token() { [ -s "$TOKEN_FILE" ] || [ -n "${CONFLUENCE_TOKEN:-}" ]; }

if [ "$DO_TOKEN" = "auto" ] && have_token; then
  echo "token already configured (${CONFLUENCE_TOKEN:+\$CONFLUENCE_TOKEN}${CONFLUENCE_TOKEN:-$TOKEN_FILE})"
elif [ "$DO_TOKEN" = "skip" ]; then
  echo "skipping token setup (--no-token)"
else
  TOKEN=""
  if [ -n "$TOKEN_FROM" ]; then
    [ -r "$TOKEN_FROM" ] || { echo "install.sh: cannot read $TOKEN_FROM" >&2; exit 1; }
    TOKEN="$(tr -d '\r\n' < "$TOKEN_FROM")"
  elif [ ! -t 0 ]; then
    TOKEN="$(tr -d '\r\n')"          # piped in
  else
    echo
    echo "You need a Confluence personal access token of your own."
    echo "There is no API for the first one — this instance has basic auth"
    echo "disabled, so mint it in a browser:"
    echo "    $PAT_URL"
    echo "(set an expiry; tokens here default to never expiring)"
    echo
    printf 'Paste token (input hidden, Enter when done): '
    read -rs TOKEN || true
    echo
  fi

  if [ -z "$TOKEN" ]; then
    echo "install.sh: no token supplied; skill is installed but unusable." >&2
    echo "            re-run 'install.sh --token' when you have one." >&2
    exit 1
  fi

  ( umask 077
    mkdir -p "$(dirname "$TOKEN_FILE")"
    printf '%s\n' "$TOKEN" > "$TOKEN_FILE" )
  chmod 600 "$TOKEN_FILE"
  unset TOKEN
  echo "wrote $TOKEN_FILE (mode $(stat -c %a "$TOKEN_FILE" 2>/dev/null || echo 600))"
fi

# --- pick an interpreter ----------------------------------------------------
# uv is the supported path: the script's PEP 723 metadata pins python>=3.9 and
# uv provisions exactly that. A bare `python3` is often the system one — 3.6 on
# these login nodes — which cannot even parse the script.
RUNNER=""
if command -v uv >/dev/null 2>&1; then
  RUNNER="uv run --script"
elif command -v python3 >/dev/null 2>&1 &&
     python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
  RUNNER="python3"
fi

if [ -z "$RUNNER" ]; then
  echo
  echo "warning: no usable interpreter found."
  echo "         uv is not installed, and python3 is $(python3 -V 2>&1 || echo absent),"
  echo "         but this script needs python >= 3.9."
  echo "         Install uv (https://docs.astral.sh/uv/) — it fetches its own python."
  VERIFY=0
fi

# --- prove it works ---------------------------------------------------------
if [ "$VERIFY" -eq 1 ] && have_token; then
  echo
  # RUNNER is deliberately unquoted: it may be "uv run --script".
  if CONFLUENCE_TOKEN_FILE="$TOKEN_FILE" $RUNNER "$SRC/scripts/cqlsearch.py" whoami; then
    :
  else
    echo "install.sh: could not verify the token — see the error above." >&2
    echo "            The skill and token are installed; only the check failed." >&2
    echo "            (rate limits can cause this; try again in a minute)" >&2
    exit 1
  fi
fi

# --- environment notes ------------------------------------------------------
if command -v uv >/dev/null 2>&1 && [ -z "${UV_CACHE_DIR:-}" ]; then
  echo
  echo "note: UV_CACHE_DIR is unset, so uv caches under ~/.cache/uv."
  echo "      On quota'd home directories set UV_CACHE_DIR=/tmp/uv-cache-\$USER."
fi

if [ -n "$RUNNER" ]; then
  echo
  echo "done. Try:"
  echo "  $RUNNER $DEST/scripts/cqlsearch.py text 'detector calibration' --limit 5"
fi
