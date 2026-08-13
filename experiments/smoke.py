#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""One-shot smoke test: does SLAC Confluence expose the CQL search API?

Deliberately few requests, spaced, because SLAC IT rate-limits this host.
Never prints the token.

The first run of this failed with CERTIFICATE_VERIFY_FAILED: uv-managed pythons
look for /etc/ssl/cert.pem, while SLAC's CA lives in the system bundle. The
explicit ssl context below is that fix.
"""
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://confluence.slac.stanford.edu"
TOKEN_FILE = "/sdf/group/lcls/ds/dm/apps/dev/env/confluence.dat"
CA = "/etc/pki/tls/certs/ca-bundle.crt"
DELAY = 12
CTX = ssl.create_default_context(cafile=CA if os.path.exists(CA) else None)


def token():
    with open(TOKEN_FILE) as f:
        return f.read().strip()


def get(path, params, tok):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {tok}",
        "Accept": "application/json",
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:400], time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, repr(e), time.time() - t0


PROBES = [
    ("/rest/api/search", {"cql": 'space = PSDM and type = page and text ~ "psana"', "limit": 3}),
    ("/rest/api/content/search", {"cql": 'space = PSDM and title ~ "psana"', "limit": 3}),
    ("/rest/api/search", {"cql": 'siteSearch ~ "detector calibration"', "limit": 3}),
]


def main():
    tok = token()
    for i, (path, params) in enumerate(PROBES):
        if i:
            time.sleep(DELAY)
        status, body, dt = get(path, params, tok)
        print(f"\n=== {path}  cql={params.get('cql')!r}")
        print(f"    HTTP {status}  ({dt:.2f}s)")
        if status == 200:
            data = json.loads(body)
            print(f"    keys: {sorted(data.keys())}")
            print(f"    totalSize={data.get('totalSize')} size={data.get('size')}")
            for r in data.get("results", [])[:3]:
                c = r.get("content", r)
                print(f"      - [{c.get('type')}] {r.get('title') or c.get('title')}")
                if "excerpt" in r:
                    print(f"        excerpt: {r['excerpt'][:110]!r}")
                if "url" in r:
                    print(f"        url: {r['url']}")
        else:
            print(f"    body: {body[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
