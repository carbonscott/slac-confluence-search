#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Why does the ETL snapshot hold more PSDM pages than live CQL reports?

Hypothesis: CQL search hides archived content by default.
Deliberately slow — the instance rate-limited us at ~3s spacing.
"""
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://confluence.slac.stanford.edu"
TOK = open("/sdf/group/lcls/ds/dm/apps/dev/env/confluence.dat").read().strip()
CTX = ssl.create_default_context(cafile="/etc/pki/tls/certs/ca-bundle.crt")


def get(params, path="/rest/api/search", tries=4):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json"})
    delay = 15
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                print(f"    (429, backing off {delay}s)")
                time.sleep(delay)
                delay *= 2
                continue
            return {"error": e.code, "body": e.read().decode("utf-8", "replace")[:200]}
    return {"error": "exhausted"}


print("waiting out the rate limiter...")
time.sleep(30)

TESTS = [
    ('space = PSDM and type = page', "default (implicit status)"),
    ('space = PSDM and type = page and status = current', "status = current"),
    ('space = PSDM and type = page and status = archived', "status = archived"),
    ('space = PSDM and type = page and status in (current, archived, draft)', "status in (...)"),
]

for i, (cql, label) in enumerate(TESTS):
    if i:
        time.sleep(15)
    d = get({"cql": cql, "limit": 1})
    print(f"  {label:<32} totalSize={d.get('totalSize', d)}")
