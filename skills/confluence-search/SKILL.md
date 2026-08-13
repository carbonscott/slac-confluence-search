---
name: confluence-search
description: Search SLAC Confluence live using CQL (Confluence Query Language) via the REST search API. Covers every space your account can see (~200 spaces, tens of thousands of pages), not just the exported PSDM subset. Use for questions about LCLS docs, psana, AMI, smalldata_tools, detectors, DAQ, experiment procedures, meeting notes, or any SLAC wiki content; also for "who wrote/changed X", "what changed recently", "find the page about X".
---

# Confluence live search (CQL)

Query `confluence.slac.stanford.edu` directly. Unlike the SQLite snapshot at
`/sdf/group/lcls/ds/dm/apps/dev/data/confluence-doc/lcls-docs.db` (1,364 docs,
PSDM + PSDMInternal only, rebuilt nightly), this searches **every space the
user's own account can see, always current** — around 200 spaces and tens of
thousands of pages for a typical LCLS account.

Results are filtered by the token owner's permissions, so coverage differs
between users. `cqlsearch.py whoami` says which identity is in play.

## Running the script

No venv, no `pip install`, no dependencies — the script carries PEP 723 inline
metadata and uses only the standard library, so all three of these work. (A
token is the one thing you do need; see **Auth** below.)

```bash
CQL="$SKILL_DIR/scripts/cqlsearch.py"                 # see below
uv run "$CQL" text "detector calibration" --limit 5   # preferred; pins python>=3.9
"$CQL"        text "detector calibration" --limit 5   # shebang runs it through uv
python3 "$CQL" text "detector calibration" --limit 5  # fallback, no uv present
```

`$SKILL_DIR` is the directory holding this `SKILL.md`. When installed with the
repo's `install.sh` that is `~/.claude/skills/confluence-search`:

```bash
CQL=~/.claude/skills/confluence-search/scripts/cqlsearch.py
```

Examples below use `uv run`. Copy `cqlsearch.py` anywhere you like — it is
standard-library-only and has no repo-relative dependencies.

## Auth

Each user needs their own personal access token. It is resolved in this order:

1. `$CONFLUENCE_TOKEN`
2. `$CONFLUENCE_TOKEN_FILE`
3. `~/.config/confluence-search/token` — the default

There is deliberately **no shared fallback path**, so a central install never
authenticates everyone as one account. If the token is missing the script prints
setup instructions; if it is group- or world-readable the script refuses to use
it. `CONFLUENCE_URL` points at a different instance.

If a command fails with a token error, tell the user to run `install.sh --token`
and mint a token at
`https://confluence.slac.stanford.edu/plugins/personalaccesstokens/usertokens.action`.
**Do not** try to read, print, or guess a token yourself.

## Commands

| Command | Use it for |
|---|---|
| `text "<words>"` | Free-text search. Builds the CQL for you. **Start here.** |
| `search "<cql>"` | A raw CQL query when you need full control. |
| `page <id\|url\|title>` | Fetch one page's full body as HTML. |
| `spaces` | List the spaces this account can see (find the right space key). |
| `whoami` | Which identity the token belongs to. One cheap call; good first check. |

### text — the common case

```bash
uv run "$CQL" text "smalldata producer"                    # whole instance
uv run "$CQL" text "psana" --space PSDM --space PSDMInternal
uv run "$CQL" text "DAQ" --type page --recent              # newest first
uv run "$CQL" text "epix" --since "2026-01-01" --limit 20
uv run "$CQL" text "geometry" --field title                # title only
```

`--field siteSearch` ranks like the Confluence UI's own search box; `--field text`
(default) matches body and title.

### search — raw CQL

```bash
uv run "$CQL" search 'space = LCLSIIData and type = page and text ~ "timing"'
uv run "$CQL" search 'creator = currentUser() order by lastmodified desc'
uv run "$CQL" search 'ancestor = 146707279' --limit 50 --all
uv run "$CQL" search 'label = "psana"' --json
```

### page — read the actual content

Search returns ~300-char excerpts. To answer a real question you usually need the
page body:

```bash
uv run "$CQL" page 337058697                    # metadata header + rendered HTML
uv run "$CQL" page 337058697 --out /tmp/p.html  # save instead of printing
uv run "$CQL" page "Area Detector Interface"    # exact title lookup
uv run "$CQL" page 337058697 --format storage   # Confluence storage format
```

The body comes back as **HTML** — read it directly, don't convert it. Confluence
has no Markdown representation, and flattening the markup destroys exactly what
you need: `<a href>` targets for citing sources, heading levels, table structure,
and code-block boundaries. `<script>`, `<style>`, and comments are stripped;
everything else is verbatim.

`--format` picks the representation: `view` (default, rendered), `export`
(`export_view`, absolute links), `storage` (source form with `<ac:>` macros),
`json` (full API response).

## Workflow

1. **Search broadly first** — `text "<words>"` with no `--space`. The DB-era habit
   of restricting to PSDM/PSDMInternal hides most of the wiki.
2. **Read `totalSize`.** Thousands of hits means the query is too vague; add
   `--space`, `--type page`, or more specific words.
3. **Fetch the promising pages** with `page <id>` — excerpts are fragments and
   routinely mislead.
4. **Cite the URL** printed with each hit so the user can open the source.

## Rules

- **Space keys are case-sensitive** and are *not* the display names. `PSDM`,
  `PSDMInternal`, `LCLSIIData` are the LCLS-relevant ones; use `spaces` to find
  others.
- **`~` for text, `=` for exact.** `title ~ "psana"` matches substrings;
  `title = "psana"` demands the whole title. Using `=` on `text` is an error.
- **Quote multi-word values**: `text ~ "detector calibration"`.
- **Attachments dominate some queries.** `lastmodified > now("-7d")` returns
  mostly `.png`/`.vtt` files; add `and type = page`.
- **Rate limits are real.** The instance returns HTTP 429 under roughly
  1 request/second sustained. The script backs off and retries automatically —
  don't wrap it in a tight loop, and prefer one `--limit 50` call over 50 calls.
- **Never print the token** or paste it into a command line.

## Reference

`reference/cql-cheatsheet.md` (next to this file) — fields, operators, functions,
and the quirks verified against *this* instance. Read it before writing a
non-obvious CQL query.

The source repo also carries offline copies of Atlassian's CQL documentation
under `docs/md/`; those are not part of the installed skill.
