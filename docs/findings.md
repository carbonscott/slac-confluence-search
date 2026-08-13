# Findings

Why this skill exists, and what was measured along the way. All numbers taken
2026-08-12 against `confluence.slac.stanford.edu`.

The question: can we query SLAC Confluence **live** instead of ETL-ing it into
SQLite first? Yes — Confluence exposes a REST search API driven by CQL
(Confluence Query Language), it responds in 50–300 ms, and it covers far more
content than the nightly snapshot.

## 1. The search API works, and it is fast

| Endpoint | Purpose |
|---|---|
| `GET /rest/api/search?cql=…` | site search with excerpts and highlights |
| `GET /rest/api/content/search?cql=…` | content-only results |
| `GET /rest/api/content/{id}?expand=body.view` | full page body |
| `GET /rest/api/space` | space enumeration |

Typical latency 50–300 ms, including `limit=200` responses. Auth is a personal
access token sent as `Authorization: Bearer`.

Use `/rest/api/search`, not `/rest/api/content/search`: only the former returns
`excerpt`, `friendlyLastModified`, and a result `url`.

## 2. Live search is 42× broader than the ETL snapshot

| | Live CQL | SQLite snapshot |
|---|---|---|
| Pages reachable | 57,666 | 1,364 documents |
| Spaces | 207 global | 2 (PSDM, PSDMInternal) |
| Freshness | current | nightly, up to 24 h stale |
| Content types | page, blogpost, attachment, comment | page only |

A search for "detector calibration" returns hits in `LCLSIIData` — a space the
ETL never exported, and where much of the current LCLS-II detector documentation
actually lives. "epixuhr" returns 835 matches, the top hits in `ppareg`, another
space the snapshot does not carry.

Measured with one LCLS account (`cwang31`). Confluence filters by permission, so
these are that account's numbers, not properties of the instance — another user
sees a different set. The comparison against the ETL holds regardless: the
snapshot is 2 spaces for everyone.

## 3. Page bodies come back as HTML, deliberately

Confluence Data Center offers `body.view`, `body.export_view`, `body.storage`
and `body.styled_view` — all markup. **There is no Markdown representation.**

An earlier version flattened the HTML to plain text. Measured on page 337058697,
that saved 42% of the characters (12,208 → 7,072) but destroyed every `<a href>`
target, heading level, and code-block boundary — while the consumer is an LLM
that reads HTML natively and is asked to cite source URLs. The flattener was
removed.

`body.export_view` is **not** smaller than `body.view` on this instance (13.2 KB
vs 12.2 KB on that page), so `view` is the default. Only `<script>`, `<style>`
and comments are stripped.

## 4. The ETL database carries 48 stale documents

The nightly cron exports `PSDM PSDMInternal` only, producing 1,144 Markdown files
(240 + 904). The database holds 1,364 rows. 48 of those rows have no Markdown file
under either space root — they are the `ami/` and LCLS-II tree from an earlier,
broader export. `md_to_sql.py` inserts and updates but never deletes, so rows
outlive their source pages.

Separately, `agents/confluence-doc.md` in the opencode tree still advertises
**1,591 pages** and a 599/932/60 hierarchy breakdown. The live database has 1,364.

Both are out of scope for this skill, recorded so they are not lost.

## 5. Gotchas worth remembering

**TLS.** uv-managed pythons on S3DF look for `/etc/ssl/cert.pem` and fail with
`CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain`. SLAC's
CA is in `/etc/pki/tls/certs/ca-bundle.crt`; `cqlsearch.py` finds it
automatically, but any other client needs `SSL_CERT_FILE` set. Off S3DF — a
laptop, say — neither path exists, and the CA must be trusted some other way.

**Rate limits, stickier than they look.** Sustained authenticated requests at
~3 s spacing tripped `HTTP 429 Rate limit exceeded` after roughly ten calls —
and once tripped it stayed tripped through a 30 s pause. Unauthenticated and
failed-auth requests trip it within about three calls, which suggests a per-IP
component on top of any per-token one: users sharing a login node may throttle
each other. `cqlsearch.py` honours `Retry-After` and backs off exponentially.
Prefer one `--limit 200` call over many small ones, and never write a tight
retry loop against it.

**No `status` field.** This Confluence version rejects `status = current`, so
archived content cannot be filtered out in CQL. Tested directly; do not retry it.

**No API for the first token.** The PAT REST API (`/rest/pat/latest/tokens`) can
create and revoke tokens, but only for a caller who already has one, and this
instance answers username/password auth with `403 Basic Authentication has been
disabled on this instance`. The first token must come from a browser.

## 6. Where this could go

The live API makes the ETL optional for *search*, though not for everything:

- **Keep the ETL** if you need offline access, full-text ranking you control, or
  joins against other LCLS data.
- **Prefer live CQL** for coverage, freshness, and zero maintenance.
- **Hybrid**: use CQL to discover pages instance-wide, then cache only the pages
  that matter into SQLite. That would fix the coverage gap and the stale-row
  problem at once.

## Archived Atlassian documentation

Offline copies live in `docs/md/`, converted from `docs/raw/`:

| File | Source |
|---|---|
| `server-advanced-searching-using-cql.md` | developer.atlassian.com/server/confluence/advanced-searching-using-cql/ |
| `server-cql-field-reference.md` | developer.atlassian.com/server/confluence/cql-field-reference/ |
| `server-cql-function-reference.md` | developer.atlassian.com/server/confluence/cql-function-reference/ |
| `cloud-advanced-searching-using-cql.md` | developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/ |

SLAC runs Confluence **Data Center**, so the `server/` pages are authoritative;
the `cloud/` copy is kept because it is better written and mostly overlaps.
Re-run `uv run docs/html2md.py` to regenerate the Markdown.

## Running the other scripts

Every `.py` here carries [PEP 723](https://peps.python.org/pep-0723/) inline
metadata and a `#!/usr/bin/env -S uv run --script` shebang, so nothing needs a
venv or a `requirements.txt`:

```bash
uv run docs/html2md.py       # deps declared inline: markdownify, beautifulsoup4
uv run experiments/probe.py  # stdlib only
```

`cqlsearch.py` is deliberately stdlib-only so it can be copied anywhere. That is
not the same as running under *any* python: it declares `requires-python =
">=3.9"`, and the system python on SLAC login nodes is 3.6, which cannot parse
the file at all.
