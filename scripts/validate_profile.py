#!/usr/bin/env python3
"""Offline structural validation. No third-party dependencies or network required."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = "{http://www.w3.org/2000/svg}"


class ProfileHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.assets = set()
        self.errors = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in {"script", "iframe", "canvas", "style", "object", "embed"}:
            self.errors.append(f"Unsupported README element: {tag}")
        if any(k.lower().startswith("on") or k == "style" for k in values):
            self.errors.append("README contains event handler or inline CSS")
        if tag in {"picture", "details", "summary"}:
            self.stack.append(tag)
        if tag == "img" and not values.get("alt"):
            self.errors.append("Image missing accessible alt text")
        for attr in ("src", "srcset"):
            if attr in values:
                for entry in values[attr].split(","):
                    self.assets.add(entry.strip().split()[0])

    def handle_endtag(self, tag):
        if tag in {"picture", "details", "summary"}:
            if not self.stack or self.stack[-1] != tag:
                self.errors.append(f"Unbalanced HTML tag: {tag}")
            else:
                self.stack.pop()


def validate():
    errors = []
    readme = (ROOT / "README.md").read_text()
    parser = ProfileHTML()
    parser.feed(readme)
    errors.extend(parser.errors)
    if parser.stack:
        errors.append("Unclosed supported HTML element")
    if readme.count("```") % 2:
        errors.append("Unbalanced fenced code block")
    headings = re.findall(r"^#{1,6} (.+)$", readme, re.M)
    slugs = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
    for target in re.findall(r"\]\(([^)]+)\)", readme):
        if target.startswith("#") and target[1:] not in slugs:
            errors.append(f"Broken section anchor: {target}")
        elif not target.startswith(("#", "https://", "mailto:")) and not (ROOT / target).is_file():
            errors.append(f"Broken local link: {target}")
    for source in parser.assets:
        if not (ROOT / source).is_file():
            errors.append(f"Missing image: {source}")
    artwork = list((ROOT / "assets").rglob("*.svg"))
    for file in artwork:
        try:
            root = ET.parse(file).getroot()
            box = list(map(float, root.attrib["viewBox"].split()))
            if len(box) != 4 or box[0:2] != [0, 0] or box[2] <= 0 or box[3] <= 0:
                errors.append(f"Invalid SVG viewBox: {file.name}")
            if [float(root.attrib["width"]), float(root.attrib["height"])] != box[2:]:
                errors.append(f"Dimensions and viewBox disagree: {file.name}")
            if root.find(NS + "title") is None or root.find(NS + "desc") is None:
                errors.append(f"Missing SVG accessible description: {file.name}")
            ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
            if len(ids) != len(set(ids)):
                errors.append(f"Duplicate SVG id: {file.name}")
            for el in root.iter():
                if el.tag.split("}")[-1] in {"script", "foreignObject", "image"}:
                    errors.append(f"External or unsupported SVG content: {file.name}")
                for k, v in el.attrib.items():
                    if k.startswith("on") or (k.endswith("href") and not v.startswith("#")):
                        errors.append(f"External SVG reference or event handler: {file.name}")
                    for ref in re.findall(r"url\(#([^)]+)\)", v):
                        if ref not in ids:
                            errors.append(f"Broken SVG definition: {file.name} / {ref}")
                if el.tag == NS + "style" and re.search(r"@import|https?://|@font-face", el.text or ""):
                    errors.append(f"External SVG styles: {file.name}")
            if file.relative_to(ROOT).as_posix() not in parser.assets:
                errors.append(f"Unused SVG: {file.relative_to(ROOT)}")
        except (ET.ParseError, KeyError, ValueError):
            errors.append(f"Invalid SVG: {file.name}")
    try:
        data = json.loads((ROOT / "assets/activity/snapshot.json").read_text())
        if not data["captured_at"] or not data["repositories"] or not data["source"].startswith("https://api.github.com/"):
            errors.append("Invalid activity source metadata")
    except (OSError, ValueError, KeyError):
        errors.append("Missing or invalid activity snapshot")
    # YAML syntax is checked separately with actionlint; keep automated CI dependency-free.
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(artwork)} SVGs, {len(parser.assets)} image paths, section anchors, supported HTML, and activity metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
