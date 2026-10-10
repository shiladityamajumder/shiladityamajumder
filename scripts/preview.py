#!/usr/bin/env python3
"""Build a local Markdown preview. Optional dependency: markdown-it-py."""

import argparse
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def slug(value):
    # The profile uses simple ASCII section names; match GitHub's heading anchors.
    return re.sub(r"[^\w\- ]", "", value.lower()).replace(" ", "-")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "preview" / "index.html")
    args = parser.parse_args()
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        parser.exit(1, "Preview requires markdown-it-py: python -m pip install markdown-it-py\n")
    markdown = MarkdownIt("commonmark", {"html": True})
    tokens = markdown.parse((ROOT / "README.md").read_text())
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            token.attrSet("id", slug(tokens[i + 1].content))
    content = markdown.renderer.render(tokens, markdown.options, {})
    # Use an absolute file base so --output works anywhere, including /tmp.
    base = escape(ROOT.as_uri() + "/", quote=True)
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Engineering Lab — local README preview</title>BASE
<style>
:root {color-scheme:light dark; --page:#ffffff; --text:#1f2328; --border:#d1d9e0; --muted:#59636e; --link:#0969da}
@media(prefers-color-scheme:dark) {:root{--page:#0d1117; --text:#f0f6fc; --border:#3d444d; --muted:#9198a1; --link:#4493f8}}
*{box-sizing:border-box} body{margin:0;background:var(--page);color:var(--text);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
main{max-width:896px;padding:32px;margin:24px auto;border:1px solid var(--border);border-radius:6px}
a{color:var(--link);text-decoration:none} a:hover{text-decoration:underline}
p{margin:16px 0} img{display:block;max-width:100%;height:auto} picture{display:block;margin:20px 0}
h2{font-size:24px;line-height:1.4;border-bottom:1px solid var(--border);padding-bottom:9px;margin:40px 0 18px;font-weight:600}
h3{font-size:20px;line-height:1.5;margin:24px 0 12px;font-weight:600}
blockquote{margin:22px 0;border-left:3px solid #3b82f6;padding:0 20px;color:var(--muted)}
li{margin:7px 0} sub{font-size:12px;line-height:1.5;vertical-align:baseline;color:var(--muted)}
details{margin:20px 0} summary{cursor:pointer;font-weight:500} strong{font-weight:600}
@media(max-width:600px){main{padding:16px;margin:0;border:0;border-radius:0}h2{font-size:22px}h3{font-size:19px}}
</style></head><body><main>CONTENT</main></body></html>'''.replace("BASE", f'<base href="{base}">').replace("CONTENT", content)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
