#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Capability probe for the SLAC Confluence CQL search API.

Records what works so the skill can be written against reality rather than
against the generic Atlassian docs (SLAC runs Confluence Data Center).
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://confluence.slac.stanford.edu"
TOKEN_FILE = "/sdf/group/lcls/ds/dm/apps/dev/env/confluence.dat"
CA = "/etc/pki/tls/certs/ca-bundle.crt"
DELAY = 5

CTX = ssl.create_default_context(cafile=CA)
TOK = open(TOKEN_FILE).read().strip()


def get(path, params):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace")), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300], time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, repr(e), time.time() - t0


PROBES = [
    ("order by works",
     "/rest/api/search",
     {"cql": 'space = PSDM and type = page order by lastmodified desc', "limit": 3}),
    ("label field",
     "/rest/api/search",
     {"cql": 'label = "psana"', "limit": 3}),
    ("lastmodified range",
     "/rest/api/search",
     {"cql": 'space in (PSDM, PSDMInternal) and lastmodified > "2026-01-01"', "limit": 3}),
    ("expand version/space/ancestors",
     "/rest/api/search",
     {"cql": 'space = PSDM and title ~ "psana"', "limit": 2,
      "expand": "content.version,content.space,content.ancestors"}),
    ("excerpt=highlight vs none",
     "/rest/api/search",
     {"cql": 'text ~ "smalldata"', "limit": 2, "excerpt": "none"}),
    ("big limit (ask 200)",
     "/rest/api/search",
     {"cql": 'space = PSDM and type = page', "limit": 200}),
    ("pagination start=50",
     "/rest/api/search",
     {"cql": 'space = PSDM and type = page', "limit": 3, "start": 50}),
    ("bad cql -> error shape",
     "/rest/api/search",
     {"cql": 'space = PSDM and bogusfield ~ "x"', "limit": 1}),
    ("content by id with body",
     "/rest/api/content/146707279",
     {"expand": "body.view,version,space,ancestors"}),
    ("spaces available",
     "/rest/api/space",
     {"limit": 25}),
]


def summarize(name, status, data, dt):
    print(f"\n### {name}   HTTP {status}  ({dt:.2f}s)")
    if status != 200:
        print(f"    {str(data)[:400]}")
        return
    if isinstance(data, dict) and "results" in data:
        print(f"    totalSize={data.get('totalSize')} size={data.get('size')} "
              f"limit={data.get('limit')} start={data.get('start')}")
        if data.get("_links", {}).get("next"):
            print(f"    next={data['_links']['next'][:90]}")
        for r in data["results"][:3]:
            c = r.get("content", r)
            bits = [f"[{c.get('type')}] {c.get('title') or r.get('title')}"]
            if c.get("version"):
                bits.append(f"v{c['version'].get('number')} by "
                            f"{c['version'].get('by', {}).get('displayName')}")
            if c.get("space"):
                bits.append(f"space={c['space'].get('key')}")
            if c.get("ancestors") is not None:
                bits.append(f"ancestors={len(c['ancestors'])}")
            if r.get("key"):
                bits.append(f"key={r['key']}")
            print("      - " + "  ".join(str(b) for b in bits))
            if r.get("excerpt"):
                print(f"        excerpt[{len(r['excerpt'])}]: {r['excerpt'][:80]!r}")
            elif "excerpt" in r:
                print("        excerpt: <empty>")
            if r.get("friendlyLastModified"):
                print(f"        modified: {r['friendlyLastModified']}")
    else:
        keys = sorted(data.keys()) if isinstance(data, dict) else type(data)
        print(f"    keys: {keys}")
        if isinstance(data, dict):
            print(f"    title={data.get('title')!r} type={data.get('type')}")
            body = data.get("body", {}).get("view", {}).get("value", "")
            print(f"    body.view length={len(body)}")
            anc = data.get("ancestors")
            if anc:
                print("    breadcrumb: " + " > ".join(a.get("title", "?") for a in anc))


def main():
    for i, (name, path, params) in enumerate(PROBES):
        if i:
            time.sleep(DELAY)
        status, data, dt = get(path, params)
        summarize(name, status, data, dt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
