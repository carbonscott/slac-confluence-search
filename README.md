# confluence-search

Experiment: can we query SLAC Confluence **live** instead of ETL-ing it into
SQLite first?

**Yes.** Confluence exposes a REST search API driven by CQL (Confluence Query
Language). It works against `confluence.slac.stanford.edu` with the same personal
access token the `confluence-doc` ETL already uses, responds in 50–300 ms, and
covers 42× more content than the nightly SQLite snapshot.

## Layout

```
confluence-search/
├── README.md                     this file
├── install.sh                    symlinks the skill into ~/.claude/skills/
├── docs/
│   ├── html2md.py                the converter used to produce docs/md
│   ├── raw/*.html                archived Atlassian pages, verbatim
│   └── md/*.md                   same pages as readable Markdown
├── experiments/
│   ├── smoke.py                  does the API exist at all?
│   ├── probe.py                  which parameters/fields work?
│   ├── counts.py                 live coverage vs the ETL database
│   ├── archived.py               why the counts differ
│   └── *-result.txt              captured output of each run
└── skills/confluence-search/     ← the Claude agent skill
    ├── SKILL.md
    ├── reference/cql-cheatsheet.md
    └── scripts/cqlsearch.py
```

## CQL documentation (downloaded here)

| File | Source |
|---|---|
| `docs/md/server-advanced-searching-using-cql.md` | developer.atlassian.com/server/confluence/advanced-searching-using-cql/ |
| `docs/md/server-cql-field-reference.md` | developer.atlassian.com/server/confluence/cql-field-reference/ |
| `docs/md/server-cql-function-reference.md` | developer.atlassian.com/server/confluence/cql-function-reference/ |
| `docs/md/cloud-advanced-searching-using-cql.md` | developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/ |

SLAC runs Confluence **Data Center**, so the `server/` pages are authoritative;
the `cloud/` copy is kept because it is better written and mostly overlaps.
Raw HTML is in `docs/raw/` — re-run `uv run docs/html2md.py` to regenerate the
Markdown (uv resolves `markdownify` and `beautifulsoup4` from the script's own
metadata).

## Running the scripts

Every `.py` here carries [PEP 723](https://peps.python.org/pep-0723/) inline
metadata and a `#!/usr/bin/env -S uv run --script` shebang, so nothing needs a
venv, a `pip install`, or a `requirements.txt`:

```bash
uv run docs/html2md.py                 # deps declared inline, fetched on demand
uv run experiments/probe.py            # stdlib only
./skills/confluence-search/scripts/cqlsearch.py spaces   # shebang → uv
```

| Script | `dependencies` |
|---|---|
| `docs/html2md.py` | `markdownify`, `beautifulsoup4` |
| everything else | none — standard library |

`cqlsearch.py` is deliberately stdlib-only so it also runs as plain
`python3 cqlsearch.py …` on a host without uv. Copy it anywhere; it has no
repo-relative dependencies.

## Install

```bash
./install.sh          # symlink the skill into ~/.claude/skills/, then set up your token
```

That is the whole thing. It links `skills/confluence-search/` into your skills
directory, prompts for your personal access token, writes it to
`~/.config/confluence-search/token` with mode 600, and makes one live call to
confirm it works:

```
linked /home/you/.claude/skills/confluence-search -> /sdf/group/.../skills/confluence-search
wrote /home/you/.config/confluence-search/token (mode 600)

Cong Wang <cwang31@slac.stanford.edu>
  instance: https://confluence.slac.stanford.edu
  token:    /home/you/.config/confluence-search/token
```

Other options:

| Flag | Effect |
|---|---|
| `--token` | (re)install the token, overwriting an existing one. Reads stdin when not a terminal. |
| `--token-from FILE` | take the token from a file instead of prompting |
| `--no-token` / `--no-verify` | install the skill only / skip the live check |
| `--copy` | copy instead of symlinking, for hosts that can't follow the link |
| `--dir DIR` | a skills directory other than `~/.claude/skills` |
| `--force` / `--uninstall` | replace an existing entry / remove the skill (your token stays) |

`install.sh` only touches the skill directory and your token; `docs/` and
`experiments/` stay in the clone. It refuses to clobber an unrelated existing
entry unless you pass `--force`.

## Getting a token

Every user needs their own — search results are filtered by **your** Confluence
permissions, so this is not a credential anyone can share with you.

Mint one in a browser at
[Profile → Settings → Personal Access Tokens](https://confluence.slac.stanford.edu/plugins/personalaccesstokens/usertokens.action),
set an expiry, and paste it when `install.sh` asks.

There is no way to automate that first step: the PAT REST API
(`/rest/pat/latest/tokens`) can create and revoke tokens, but only for a caller
who already has one, and this instance answers username/password auth with
`403 Basic Authentication has been disabled on this instance`.

The token is resolved at every invocation, in this order:

1. `$CONFLUENCE_TOKEN`
2. `$CONFLUENCE_TOKEN_FILE`
3. `~/.config/confluence-search/token`

There is deliberately no shared default path. A shared one would mean every user
of a central install silently authenticating as whoever owns that file, seeing
that account's view of the wiki and getting results they cannot reproduce in
their own browser. Point `CONFLUENCE_TOKEN_FILE` at a shared file if you
genuinely want that. `cqlsearch.py` refuses to read a token file that is group-
or world-readable, and `cqlsearch.py whoami` prints the identity in play.

## Central deployment

One clone, many users. Put the repo somewhere group-readable and have each
person run `install.sh` from it:

```bash
# once, by a maintainer
git clone <this-repo> /sdf/group/lcls/ds/dm/apps/dev/tools/confluence-search

# once, by each user
/sdf/group/lcls/ds/dm/apps/dev/tools/confluence-search/install.sh
```

Everyone symlinks the same files, so `git pull` in the central clone updates all
users at once. Credentials stay per-user because the token path is resolved from
the invoking account's home directory (via the passwd database, not `$HOME`,
which is inherited and wrong under `sudo` and cron).

Two things to plan for:

- **A shared git checkout gets object-ownership conflicts** when several people
  pull. Either designate one maintainer who pulls, or
  `git config core.sharedRepository group` on the central clone.
- **Rate limiting is a shared resource.** The instance throttles aggressively
  and appears to have a per-IP component — anonymous requests trip it within a
  few calls. Users on the same login node may therefore throttle each other.
  Worth measuring before a wide rollout; see the gotchas below.

## Using it directly

The script needs no install at all — it is standard-library-only with PEP 723
metadata:

```bash
CQL=~/.claude/skills/confluence-search/scripts/cqlsearch.py   # or any copy
uv run "$CQL" text "detector calibration" --limit 5
uv run "$CQL" search 'space = LCLSIIData and type = page and text ~ "timing"'
uv run "$CQL" page 337058697
uv run "$CQL" spaces
```

`page` returns the page body as **HTML** with a Markdown metadata header. There is
no Markdown conversion: Confluence offers no Markdown representation, and the
flattener this prototype originally shipped cost every `<a href>` target, heading
level, and code-block boundary to save ~40% of the characters. The consumer is an
LLM, which reads HTML natively. `<script>`, `<style>`, and comments are stripped;
`--format` selects `view` (default) / `export` / `storage` / `json`.

## Findings

### 1. The search API works, and it is fast

| Endpoint | Purpose |
|---|---|
| `GET /rest/api/search?cql=…` | site search with excerpts and highlights |
| `GET /rest/api/content/search?cql=…` | content-only results |
| `GET /rest/api/content/{id}?expand=body.view` | full page body |
| `GET /rest/api/space` | space enumeration |

Typical latency 50–300 ms, including `limit=200` responses. Auth is the existing
PAT sent as `Authorization: Bearer` — no separate credential needed.

### 2. Live search is 42× broader than the ETL snapshot

| | Live CQL | SQLite snapshot |
|---|---|---|
| Pages reachable | 57,666 | 1,364 documents |
| Spaces | 207 global | 2 (PSDM, PSDMInternal) |
| Freshness | current | nightly, up to 24 h stale |
| Content types | page, blogpost, attachment, comment | page only |

A search for "detector calibration" returns hits in `LCLSIIData` — a space the
ETL never exported, and where much of the current LCLS-II detector documentation
actually lives.

Measured with one LCLS account (`cwang31`). Confluence filters by permission, so
these are that account's numbers, not properties of the instance — another user
sees a different set. The comparison against the ETL holds regardless: the
snapshot is 2 spaces for everyone.

### 3. The ETL database carries 48 stale documents

The nightly cron exports `PSDM PSDMInternal` only, producing 1,144 Markdown files
(240 + 904). The database holds 1,364 rows. 48 of those rows have no Markdown file
under either space root — they are the `ami/` and LCLS-II tree from an earlier,
broader export. `md_to_sql.py` inserts and updates but never deletes, so rows
outlive their source pages.

Separately, `agents/confluence-doc.md` in the opencode tree still advertises
**1,591 pages** and a 599/932/60 hierarchy breakdown. The live database has 1,364.

### 4. Two gotchas worth remembering

**TLS.** uv-managed pythons on S3DF look for `/etc/ssl/cert.pem` and fail with
`CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain`. SLAC's
CA is in `/etc/pki/tls/certs/ca-bundle.crt`; `cqlsearch.py` finds it
automatically, but any other client needs `SSL_CERT_FILE` set.

**Rate limits, stickier than they look.** Sustained authenticated requests at
~3 s spacing tripped `HTTP 429 Rate limit exceeded` after roughly ten calls —
and once tripped it stayed tripped through a 30 s pause. Unauthenticated and
failed-auth requests trip it within about three calls, which suggests a per-IP
component on top of any per-token one: users sharing a login node may throttle
each other. `cqlsearch.py` honours `Retry-After` and backs off exponentially.
Prefer one `--limit 200` call over many small ones, and never write a tight
retry loop against it.

**No `status` field.** This Confluence version rejects `status = current`, so
archived content cannot be filtered out in CQL.

## Where this could go

The live API makes the ETL optional for *search*, though not for everything:

- **Keep the ETL** if you need offline access, full-text ranking you control, or
  joins against other LCLS data.
- **Prefer live CQL** for coverage, freshness, and zero maintenance.
- **Hybrid**: use CQL to discover pages instance-wide, then cache only the pages
  that matter into SQLite. That would fix the coverage gap and the stale-row
  problem at once.
