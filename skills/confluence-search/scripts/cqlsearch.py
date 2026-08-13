#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""cqlsearch — query SLAC Confluence live via the CQL search REST API.

Standard library only, so it runs either way:

  uv run cqlsearch.py search 'space = PSDM and text ~ "psana"' --limit 10
  ./cqlsearch.py text "detector calibration" --space PSDM   # uv via shebang
  python3 cqlsearch.py page 146707279                       # no uv needed
  uv run cqlsearch.py spaces

Auth: a Confluence Data Center personal access token (Bearer), resolved in
order from $CONFLUENCE_TOKEN, $CONFLUENCE_TOKEN_FILE, then
~/.config/confluence-search/token. Per-user by design — there is no shared
default, so a central install never authenticates everyone as one account.
Run `cqlsearch.py whoami` to see which identity you are using.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    import pwd                      # unix only; absent on Windows
except ImportError:                 # pragma: no cover
    pwd = None

BASE = os.environ.get("CONFLUENCE_URL", "https://confluence.slac.stanford.edu")
PAT_URL = f"{BASE}/plugins/personalaccesstokens/usertokens.action"


def home_dir() -> str:
    """The invoking user's home.

    $HOME is inherited, so it lies under sudo, cron, and service accounts. The
    passwd database does not.
    """
    if pwd is not None:
        try:
            return pwd.getpwuid(os.getuid()).pw_dir
        except KeyError:
            pass
    return os.path.expanduser("~")


def default_token_file() -> str:
    """Per-user, by construction — never a shared path.

    A shared default would mean every user of a central install silently
    authenticating as whoever owns that file, seeing that account's view of the
    wiki. Deliberately absent: point CONFLUENCE_TOKEN_FILE at a shared file if
    you actually want that.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home_dir(), ".config")
    return os.path.join(xdg, "confluence-search", "token")


TOKEN_FILE = os.environ.get("CONFLUENCE_TOKEN_FILE") or default_token_file()

# S3DF nodes trust SLAC's internal CA through the system bundle; the uv-managed
# pythons look for /etc/ssl/cert.pem instead and fail verification without this.
CA_CANDIDATES = ("/etc/pki/tls/certs/ca-bundle.crt",
                 "/etc/ssl/certs/ca-certificates.crt")

HL_OPEN, HL_CLOSE = "@@@hl@@@", "@@@endhl@@@"
MAX_LIMIT = 200          # server accepts at least this much per page
PAGE_DELAY = 1.0         # between pages of a --all sweep


# --------------------------------------------------------------------------
# transport
# --------------------------------------------------------------------------

def ssl_context() -> ssl.SSLContext:
    cafile = os.environ.get("SSL_CERT_FILE")
    if not cafile:
        cafile = next((c for c in CA_CANDIDATES if os.path.exists(c)), None)
    return ssl.create_default_context(cafile=cafile)


SETUP_HELP = f"""\
error: no Confluence token.

Every user needs their own — results are filtered by *your* wiki permissions.

  1. mint one (browser; there is no API for the first token, this instance
     has basic auth disabled):
       {PAT_URL}
  2. install it:
       install.sh --token          # prompts, writes the file with mode 600
     or by hand:
       mkdir -p {os.path.dirname(TOKEN_FILE)}
       (umask 077; cat > {TOKEN_FILE})   # paste, then Ctrl-D

Or set CONFLUENCE_TOKEN / CONFLUENCE_TOKEN_FILE to override."""


def token_source() -> str:
    """Where the token came from. Never returns the token itself."""
    if os.environ.get("CONFLUENCE_TOKEN"):
        return "$CONFLUENCE_TOKEN"
    return TOKEN_FILE


def read_token_file(path: str) -> str:
    try:
        mode = os.stat(path).st_mode
    except OSError as e:
        sys.exit(f"error: cannot stat {path}: {e}")
    if mode & 0o077:
        # Group trees here are setgid and group-writable, so an inherited umask
        # leaks the token easily. Fail at setup rather than quietly.
        sys.exit(f"error: {path} is readable by group or others "
                 f"(mode {mode & 0o777:03o}).\n"
                 f"  fix: chmod 600 {path}")
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError as e:
        sys.exit(f"error: cannot read {path}: {e}")


def get_token() -> str:
    tok = os.environ.get("CONFLUENCE_TOKEN")
    if tok:
        return tok.strip()
    if not os.path.exists(TOKEN_FILE):
        sys.exit(SETUP_HELP)
    tok = read_token_file(TOKEN_FILE)
    if not tok:
        sys.exit(f"error: {TOKEN_FILE} is empty.\n\n{SETUP_HELP}")
    return tok


class Client:
    """Thin GET client with 429 backoff. The SLAC instance rate-limits."""

    def __init__(self, verbose: bool = False):
        self.ctx = ssl_context()
        self.token = get_token()
        self.verbose = verbose

    def get(self, path: str, params: dict, tries: int = 5) -> dict:
        url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        })
        delay = 10.0
        for attempt in range(tries):
            try:
                with urllib.request.urlopen(req, timeout=60, context=self.ctx) as r:
                    return json.loads(r.read().decode("utf-8", "replace"))
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                if e.code == 429 and attempt < tries - 1:
                    wait = float(e.headers.get("Retry-After") or delay)
                    if self.verbose:
                        print(f"  (429 rate limited, sleeping {wait:.0f}s)",
                              file=sys.stderr)
                    time.sleep(wait)
                    delay *= 2
                    continue
                if e.code == 400:
                    sys.exit(f"CQL error (HTTP 400): {extract_message(body)}")
                if e.code == 401:
                    sys.exit(f"error: HTTP 401 — token rejected. It is invalid, "
                             f"expired, or revoked.\n"
                             f"  token came from: {token_source()}\n"
                             f"  mint a new one:  {PAT_URL}\n"
                             f"  then re-run:     install.sh --token")
                sys.exit(f"HTTP {e.code} for {path}: {extract_message(body)}")
            except urllib.error.URLError as e:
                sys.exit(f"network/TLS error for {path}: {e.reason}\n"
                         f"hint: export SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt")
        sys.exit("error: retries exhausted (rate limited)")


def extract_message(body: str) -> str:
    try:
        return json.loads(body).get("message", body[:300])
    except Exception:  # noqa: BLE001
        return body[:300]


# --------------------------------------------------------------------------
# formatting
# --------------------------------------------------------------------------

def clean_excerpt(text: str, markers: bool = False) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    if markers:
        text = text.replace(HL_OPEN, "**").replace(HL_CLOSE, "**")
    else:
        text = text.replace(HL_OPEN, "").replace(HL_CLOSE, "")
    return " ".join(text.split())


SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)\b.*?</\1\s*>")
COMMENT_RE = re.compile(r"(?s)<!--.*?-->")


def strip_noise(markup: str) -> str:
    """Drop <script>, <style>, and comments. Everything else is kept verbatim.

    Page bodies are handed to an LLM, which reads HTML natively — links, heading
    levels, table structure and code blocks all carry meaning and are left alone.
    Only markup that renders to nothing is removed.
    """
    return COMMENT_RE.sub("", SCRIPT_STYLE_RE.sub("", markup)).strip()


def print_hit(i: int, r: dict, markers: bool) -> None:
    c = r.get("content", {}) or {}
    title = clean_excerpt(r.get("title") or c.get("title") or "(untitled)", markers)
    ctype = c.get("type") or r.get("entityType") or "?"
    space = (c.get("space") or {}).get("key") or ""
    ident = c.get("id") or ""
    url = r.get("url") or ""
    if url.startswith("/"):
        url = BASE + url
    print(f"\n[{i}] {title}")
    meta = [b for b in (ctype, f"space={space}" if space else "",
                        f"id={ident}" if ident else "",
                        r.get("friendlyLastModified", "")) if b]
    print(f"    {'  |  '.join(meta)}")
    if url:
        print(f"    {url}")
    ex = clean_excerpt(r.get("excerpt", ""), markers)
    if ex:
        print(f"    {ex[:400]}")


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_search(args) -> int:
    client = Client(verbose=args.verbose)
    params = {"cql": args.cql, "limit": min(args.limit, MAX_LIMIT),
              "start": args.start, "excerpt": args.excerpt}
    if args.expand:
        params["expand"] = args.expand
    elif not args.json:
        params["expand"] = "content.space,content.version"

    data = client.get("/rest/api/search", params)
    results = data.get("results", [])
    total = data.get("totalSize")

    if args.all and total and total > len(results):
        want = args.limit if args.limit < MAX_LIMIT else total
        start = args.start + len(results)
        while len(results) < min(want, total) and start < total:
            time.sleep(PAGE_DELAY)
            params["start"] = start
            page = client.get("/rest/api/search", params)
            batch = page.get("results", [])
            if not batch:
                break
            results.extend(batch)
            start += len(batch)
        results = results[:want]

    if args.json:
        json.dump({"cql": args.cql, "totalSize": total, "returned": len(results),
                   "results": results}, sys.stdout, indent=2)
        print()
        return 0

    print(f"cql: {args.cql}")
    print(f"{total} match(es); showing {len(results)}")
    for i, r in enumerate(results, 1):
        print_hit(i, r, args.markers)
    if total and total > len(results):
        print(f"\n... {total - len(results)} more; "
              f"use --start {args.start + len(results)} or --all")
    return 0


def cmd_text(args) -> int:
    """Convenience wrapper that builds the CQL for you."""
    words = args.words.replace('"', r"\"")
    clauses = [f'{args.field} ~ "{words}"']
    if args.space:
        keys = ", ".join(args.space)
        clauses.append(f"space = {keys}" if len(args.space) == 1
                       else f"space in ({keys})")
    if args.type:
        clauses.append(f"type = {args.type}")
    if args.since:
        clauses.append(f'lastmodified > "{args.since}"')
    cql = " and ".join(clauses)
    if args.recent:
        cql += " order by lastmodified desc"
    args.cql = cql
    return cmd_search(args)


PAGE_ID_RE = re.compile(r"(?:pageId=|/pages/(?:viewpage\.action\?pageId=)?)(\d+)")

# --format name -> the body representation Confluence expands under. There is no
# Markdown representation; every one of these is markup.
BODY_KEY = {"view": "view", "export": "export_view",
            "storage": "storage", "json": "view"}


def cmd_page(args) -> int:
    client = Client(verbose=args.verbose)
    target = args.target
    m = PAGE_ID_RE.search(target)
    if m:
        page_id = m.group(1)
    elif target.isdigit():
        page_id = target
    else:
        hits = client.get("/rest/api/content/search",
                          {"cql": f'title = "{target}"', "limit": 1})
        rs = hits.get("results", [])
        if not rs:
            sys.exit(f"no page titled {target!r}")
        page_id = rs[0]["id"]

    body_key = BODY_KEY[args.format]
    data = client.get(f"/rest/api/content/{page_id}",
                      {"expand": f"body.{body_key},version,space,ancestors"})
    title = data.get("title", "")
    space = (data.get("space") or {}).get("key", "")
    ver = data.get("version") or {}
    crumb = " > ".join(a.get("title", "?") for a in data.get("ancestors", []))
    body = ((data.get("body") or {}).get(body_key) or {}).get("value", "")

    if args.format == "json":
        json.dump(data, sys.stdout, indent=2)
        print()
        return 0
    out = strip_noise(body)

    header = (f"# {title}\n\n"
              f"- space: {space}\n"
              f"- id: {page_id}\n"
              f"- version: {ver.get('number')} by "
              f"{(ver.get('by') or {}).get('displayName')} ({ver.get('when')})\n"
              f"- breadcrumb: {crumb}\n"
              f"- url: {BASE}/pages/viewpage.action?pageId={page_id}\n\n---\n\n")
    text = header + out
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote {args.out} ({len(text)} chars)")
    else:
        print(text)
    return 0


def cmd_whoami(args) -> int:
    """One cheap call that proves the token works and says who it belongs to."""
    me = Client(verbose=args.verbose).get("/rest/api/user/current", {})
    print(f"{me.get('displayName') or '?'} <{me.get('username') or '?'}>")
    print(f"  instance: {BASE}")
    print(f"  token:    {token_source()}")
    print("  note:     search results are filtered by your own permissions —")
    print("            another account sees a different set of spaces.")
    return 0


def cmd_spaces(args) -> int:
    client = Client(verbose=args.verbose)
    start, rows = 0, []
    while True:
        d = client.get("/rest/api/space", {"limit": 100, "start": start,
                                           "type": args.type})
        batch = d.get("results", [])
        rows.extend(batch)
        if len(batch) < 100:
            break
        start += len(batch)
        time.sleep(PAGE_DELAY)
    for s in sorted(rows, key=lambda s: s.get("key", "")):
        if args.filter and args.filter.lower() not in json.dumps(s).lower():
            continue
        print(f"{s.get('key', ''):<20} {s.get('type', ''):<10} {s.get('name', '')}")
    print(f"\n{len(rows)} spaces visible to this token")
    return 0


# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cqlsearch",
        description="Query SLAC Confluence live via the CQL search API.")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_search_flags(sp):
        sp.add_argument("--limit", type=int, default=10)
        sp.add_argument("--start", type=int, default=0)
        sp.add_argument("--all", action="store_true",
                        help="paginate until --limit (or everything) is collected")
        sp.add_argument("--json", action="store_true", help="raw JSON results")
        sp.add_argument("--expand", default="",
                        help="e.g. content.body.view,content.ancestors")
        sp.add_argument("--excerpt", default="highlight",
                        choices=["highlight", "indexed", "none"])
        sp.add_argument("--markers", action="store_true",
                        help="keep search highlights as **bold** in excerpts")

    s = sub.add_parser("search", help="run a raw CQL query")
    s.add_argument("cql")
    add_search_flags(s)
    s.set_defaults(func=cmd_search)

    t = sub.add_parser("text", help="free-text search; builds the CQL for you")
    t.add_argument("words")
    t.add_argument("--space", action="append",
                   help="space key; repeatable (PSDM, PSDMInternal, ...)")
    t.add_argument("--type", help="page | blogpost | attachment | comment")
    t.add_argument("--since", help='e.g. "2026-01-01" or "now(-30d)"')
    t.add_argument("--field", default="text",
                   choices=["text", "title", "siteSearch"],
                   help="text=body+title, siteSearch=whole-site relevance ranking")
    t.add_argument("--recent", action="store_true",
                   help="order by lastmodified desc instead of relevance")
    add_search_flags(t)
    t.set_defaults(func=cmd_text)

    g = sub.add_parser("page", help="fetch one page by id, URL, or exact title")
    g.add_argument("target")
    g.add_argument("--format", default="view",
                   choices=["view", "export", "storage", "json"],
                   help="body representation: view=rendered HTML (default), "
                        "export=export_view HTML, storage=Confluence storage "
                        "format, json=full API response")
    g.add_argument("--out", help="write to file instead of stdout")
    g.set_defaults(func=cmd_page)

    w = sub.add_parser("whoami", help="who this token authenticates as")
    w.set_defaults(func=cmd_whoami)

    sp = sub.add_parser("spaces", help="list spaces this token can see")
    sp.add_argument("--type", default="global", choices=["global", "personal"])
    sp.add_argument("--filter", help="substring filter")
    sp.set_defaults(func=cmd_spaces)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
