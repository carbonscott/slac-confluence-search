# confluence-search

Ask Claude about anything on the SLAC wiki and get answers with links to the
real pages.

It searches Confluence **live**, so it sees every space your own account can
see — not the small subset the nightly export covers — and it is never out of
date. Works in Claude Code and in the shared LCLS opencode install.

---

## Quick start

### 1. Get the skill

**Using the shared opencode install on S3DF?** It is already there. Skip to
step 2.

**Setting up your own Claude Code?** Clone and deploy:

```bash
git clone git@github.com:carbonscott/slac-confluence-search.git
cd slac-confluence-search
./install.sh
```

That links the skill into `~/.claude/skills/`. It never touches credentials.

### 2. Get a token

You need your own Confluence personal access token. Nobody can give you one:
results are filtered by *your* wiki permissions, so a shared token would show
you someone else's view of the wiki.

Mint it in a browser:

**https://confluence.slac.stanford.edu/plugins/personalaccesstokens/usertokens.action**

Set an expiry (90 days is reasonable) and copy the value — it is shown **once**.

→ [Illustrated walkthrough](docs/token-setup/getting-a-token.md) for the
screen-by-screen version.

### 3. Register the token

Run `confluence-login` and paste it at the prompt. It is not on your `PATH`; the
path depends on where the skill was deployed:

```bash
# shared opencode install on S3DF
/sdf/group/lcls/ds/dm/apps/dev/opencode/skills/confluence-search/scripts/confluence-login

# your own Claude Code
~/.claude/skills/confluence-search/scripts/confluence-login
```

Input is hidden. The token is saved to `~/.config/confluence-search/token` with
mode 600, and one live call confirms it works:

```
wrote /home/you/.config/confluence-search/token (mode 600)

Cong Wang <cwang31@slac.stanford.edu>
  instance: https://confluence.slac.stanford.edu
```

Seeing your own name means you are done. **You register the token once**, even if
you use both Claude Code and opencode — it lives in your home directory, not
inside either skill.

### 4. Ask it something

> `@confluence-search` find notes about epixuhr

> `@confluence-search` what does the wiki say about smalldata producers?

> `@confluence-search` who changed the DAQ timing page recently?

Claude runs the searches, reads the promising pages, and cites the URLs so you
can open the source.

---

## When it stops working

**"no Confluence token"** — you have not done step 3, or you are on a machine
where you have not done it yet.

**HTTP 401** — the token expired or was revoked. Mint a new one (step 2) and
install it over the old one:

```bash
<same path as step 3>/confluence-login --force
```

**Check who you are** at any time:

```bash
<skill-dir>/scripts/cqlsearch.py whoami
```

---

## For maintainers: central deployment

One clone, many users, two jobs that belong to different people.

```bash
# once: clone somewhere group-readable
git clone git@github.com:carbonscott/slac-confluence-search.git \
  /sdf/group/lcls/ds/dm/apps/dev/tools/confluence-search

# deploy the skill — never touches a credential
/sdf/group/.../confluence-search/install.sh
/sdf/group/.../confluence-search/install.sh --dir /some/shared/skills

# each user, once: their own token (step 3 above)
```

`install.sh` deploys and nothing else; `confluence-login` registers a token and
nothing else. Neither can do the other's job, and you cannot register tokens on
your users' behalf in any case.

| Flag | Effect |
|---|---|
| `--copy` / `--symlink` | force one mode; the default is chosen from the destination |
| `--dir DIR` | a skills directory other than `~/.claude/skills` |
| `--force` | replace an existing entry that isn't ours |
| `--uninstall` | remove the deployed skill (the user's token stays) |

**Symlink or copy is decided by where the destination is.** Under your home it
symlinks, so `git pull` updates you immediately. Anywhere else it copies, and
says why: a symlink in a shared tree points back into one person's clone, which
everyone else usually cannot read.

**For the LCLS shared opencode tree, prefer `deploy.sh` and the manifest** in
`deploy-opencode` over this script — it also fixes group ownership and creates
the `agents/` symlink. Manifest entry:

```json
{
  "name": "confluence-search",
  "repo": "carbonscott/slac-confluence-search",
  "ref": "main",
  "cron": null,
  "central_data": null
}
```

---

## What is in this repo

```
claude/skills/confluence-search/     for Claude Code users
opencode/skills/confluence-search/   rsynced into the shared opencode tree
install.sh                           deploys the skill
docs/token-setup/                    the illustrated token walkthrough
docs/findings.md                     how it works, what was measured, gotchas
docs/md/, docs/raw/                  Atlassian's query-syntax docs, offline
```

`claude/` and `opencode/` hold **identical, duplicated** content — the layout the
LCLS deploy manifest expects. Any edit must be applied to both; `diff -r` between
them should be empty before you commit.

---

## Under the hood

[docs/findings.md](docs/findings.md) covers how the search actually works, the
measured coverage against the old SQLite export, API latency, the TLS and
rate-limit gotchas, and two defects found in the existing ETL.

The short version: it queries Confluence's REST search API directly, with your
token, and hands the agent page bodies as HTML. Nothing is cached, nothing is
synced, and there is no database to keep up to date.
