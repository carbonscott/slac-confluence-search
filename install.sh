#!/usr/bin/env bash
# Deploy the confluence-search Claude agent skill, and set up your token.
#
# Two separable jobs, because they belong to two different people:
#
#   maintainer, once   clone this repo somewhere group-readable, then
#                      ./install.sh --no-token (or --copy) to deploy the skill
#   each user, once    ./install.sh --token-only, or, if they were handed the
#                      deployed skill and never saw this repo,
#                      `cqlsearch.py login` — which is what this script calls.
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
DO_SKILL=1               # --token-only turns this off
DO_TOKEN="auto"          # auto | force | skip
TOKEN_FROM=""
VERIFY=1
TOKEN_VERIFIED=0         # login already made the live call; don't spend a second one

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
  --token-only     set up the token and nothing else, for a skill someone
                   already deployed for you
  --no-token       deploy the skill only, leave credentials alone
  --no-verify      skip the live call that confirms the token works

  --copy           copy the skill instead of symlinking it
  --dir DIR        install into DIR instead of \$CLAUDE_SKILLS_DIR or ~/.claude/skills
  --force          replace whatever is already at the destination
  --uninstall      remove the installed skill (leaves your token in place)

The token step is 'cqlsearch.py login'. Run that directly if all you have is
the deployed skill directory and not this repo.

Token file: $TOKEN_FILE
Mint one at: $PAT_URL
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --token)      DO_TOKEN="force"; shift ;;
    --token-from) TOKEN_FROM="${2:?--token-from needs a file}"; DO_TOKEN="force"; shift 2 ;;
    --token-only) DO_TOKEN="force"; DO_SKILL=0; shift ;;
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
CQL="$SRC/scripts/cqlsearch.py"
chmod +x "$CQL" 2>/dev/null || true   # no-op on a read-only central clone

# --- pick an interpreter ----------------------------------------------------
# uv is the supported path: the script's PEP 723 metadata pins python>=3.9 and
# uv provisions exactly that. A bare `python3` is often the system one — 3.6 on
# these login nodes — which cannot even parse the script. Chosen before the
# token step, which now runs through it.
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

# --- deploy the skill -------------------------------------------------------
if [ "$DO_SKILL" -eq 0 ]; then
  echo "skipping skill deployment (--token-only)"
else
  mkdir -p "$DEST_DIR"

  # refuse to clobber someone else's skill
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
fi

# --- the token --------------------------------------------------------------
# Handed to `cqlsearch.py login`, the command an end user runs when they were
# given the deployed skill and never saw this repo. Prompting and writing the
# file here as well would be a second implementation of "600-mode, race-free,
# never echoed" to keep in step with the first.
have_token() { [ -s "$TOKEN_FILE" ] || [ -n "${CONFLUENCE_TOKEN:-}" ]; }

if [ "$DO_TOKEN" = "skip" ]; then
  echo "skipping token setup (--no-token)"
elif [ "$DO_TOKEN" = "auto" ] && have_token; then
  echo "token already configured (${CONFLUENCE_TOKEN:+\$CONFLUENCE_TOKEN}${CONFLUENCE_TOKEN:-$TOKEN_FILE})"
else
  if [ -z "$RUNNER" ]; then
    echo "install.sh: no usable interpreter, so the token cannot be installed." >&2
    echo "            Install uv, then re-run 'install.sh --token-only'." >&2
    exit 1
  fi
  # --force unconditionally: whether to overwrite was already decided above —
  # by --token / --token-from / --token-only, or by there being no token yet.
  LOGIN=(login --force)
  if [ -n "$TOKEN_FROM" ]; then LOGIN+=(--from "$TOKEN_FROM"); fi
  if [ "$VERIFY" -ne 1 ]; then LOGIN+=(--no-verify); fi
  echo
  # RUNNER is deliberately unquoted: it may be "uv run --script". stdin passes
  # straight through, so `echo tok | install.sh --token` still works.
  if CONFLUENCE_TOKEN_FILE="$TOKEN_FILE" $RUNNER "$CQL" "${LOGIN[@]}"; then
    if [ "$VERIFY" -eq 1 ]; then TOKEN_VERIFIED=1; fi
  else
    echo "install.sh: the token step failed — see the error above." >&2
    echo "            Re-run 'install.sh --token-only' to try again." >&2
    exit 1
  fi
fi

# --- prove it works ---------------------------------------------------------
# Skipped when login just did it: the instance rate-limits hard enough that a
# second identical call is a real cost.
if [ "$VERIFY" -eq 1 ] && [ "$TOKEN_VERIFIED" -eq 0 ] && have_token; then
  echo
  if CONFLUENCE_TOKEN_FILE="$TOKEN_FILE" $RUNNER "$CQL" whoami; then
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
  if [ "$DO_SKILL" -eq 1 ]; then
    echo "  $RUNNER $DEST/scripts/cqlsearch.py text 'detector calibration' --limit 5"
  else
    echo "  $RUNNER $CQL text 'detector calibration' --limit 5"
  fi
fi
