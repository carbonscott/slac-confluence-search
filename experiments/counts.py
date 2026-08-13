#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Compare live CQL search coverage against the ETL SQLite snapshot."""
import json
import sqlite3
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://confluence.slac.stanford.edu"
TOK = open("/sdf/group/lcls/ds/dm/apps/dev/env/confluence.dat").read().strip()
CTX = ssl.create_default_context(cafile="/etc/pki/tls/certs/ca-bundle.crt")
DB = "/sdf/group/lcls/ds/dm/apps/dev/data/confluence-doc/lcls-docs.db"


def get(path, params):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", "replace")[:200]}


QUERIES = [
    ('space = PSDM and type = page', "PSDM pages"),
    ('space = PSDMInternal and type = page', "PSDMInternal pages"),
    ('space in (PSDM, PSDMInternal) and type = page', "both spaces, pages"),
    ('space in (PSDM, PSDMInternal)', "both spaces, all content types"),
    ('space in (PSDM, PSDMInternal) and type = attachment', "both spaces, attachments"),
    ('space in (PSDM, PSDMInternal) and type = blogpost', "both spaces, blogposts"),
    ('space in (PSDM, PSDMInternal) and type = comment', "both spaces, comments"),
]

print("=== live CQL totals (/rest/api/search) ===")
for i, (cql, label) in enumerate(QUERIES):
    if i:
        time.sleep(3)
    d = get("/rest/api/search", {"cql": cql, "limit": 1})
    print(f"  {label:<34} totalSize={d.get('totalSize', d)}")

print("\n=== same via /rest/api/content/search ===")
for cql, label in [('space = PSDM and type = page', "PSDM pages"),
                   ('space = PSDMInternal and type = page', "PSDMInternal pages")]:
    time.sleep(3)
    d = get("/rest/api/content/search", {"cql": cql, "limit": 1})
    print(f"  {label:<34} totalSize={d.get('totalSize', d)}")

print("\n=== ETL SQLite snapshot ===")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
print(f"  documents                          {con.execute('select count(*) from documents').fetchone()[0]}")
for row in con.execute(
        "select substr(breadcrumb, 1, instr(breadcrumb||' > ', ' > ')-1) top, count(*) "
        "from documents group by top order by 2 desc limit 6"):
    print(f"    top-level {row[0]!r:<45} {row[1]}")
print("  newest last_modified:",
      con.execute("select max(last_modified) from documents").fetchone()[0])
con.close()
