#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["markdownify", "beautifulsoup4"]
# ///
"""Convert the archived Atlassian CQL doc pages to Markdown.

Usage:  uv run docs/html2md.py     (run from the repo root; uv fetches the deps)
Reads docs/raw/*.html, writes docs/md/*.md next to it.
"""
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify

SOURCE_URL = {
    "server-advanced-searching-using-cql":
        "https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/",
    "server-cql-field-reference":
        "https://developer.atlassian.com/server/confluence/cql-field-reference/",
    "server-cql-function-reference":
        "https://developer.atlassian.com/server/confluence/cql-function-reference/",
    "cloud-advanced-searching-using-cql":
        "https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/",
}

SELECTORS = ["main", "article", "[role=main]", "#content", "div.wrapper"]


def extract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "svg"]):
        tag.decompose()
    for sel in SELECTORS:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 500:
            return str(node)
    return str(soup.body or soup)


def main() -> int:
    raw_dir = Path("docs/raw")
    md_dir = Path("docs/md")
    md_dir.mkdir(parents=True, exist_ok=True)

    for html_path in sorted(raw_dir.glob("*.html")):
        stem = html_path.stem
        md = markdownify(extract(html_path.read_text(encoding="utf-8", errors="replace")),
                         heading_style="ATX", strip=["img"])
        # collapse runs of blank lines left behind by stripped chrome
        lines, out, blanks = md.splitlines(), [], 0
        for line in lines:
            if line.strip():
                blanks = 0
                out.append(line.rstrip())
            else:
                blanks += 1
                if blanks <= 1:
                    out.append("")
        body = "\n".join(out).strip()
        # drop the site chrome that precedes the page's own H1
        for i, line in enumerate(body.splitlines()):
            if line.startswith("# "):
                body = "\n".join(body.splitlines()[i:])
                break
        # drop the "Rate this page" / footer tail
        for marker in ("Was this helpful?", "Rate this page", "Provide feedback about"):
            idx = body.find(marker)
            if idx > 500:
                body = body[:idx].rstrip()
        header = f"<!-- archived from {SOURCE_URL.get(stem, 'unknown')} -->\n\n"
        (md_dir / f"{stem}.md").write_text(header + body + "\n", encoding="utf-8")
        print(f"{stem}.md  {len(body):>7} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
