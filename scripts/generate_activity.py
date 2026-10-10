#!/usr/bin/env python3
"""Render an honest public repository snapshot; retain every asset on fetch failure."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from svg_design import HIGHLIGHT, MUTED, label, line, svg, text

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"


def fetch_repositories(username):
    """Fetch all pages, never publish a partial response or use private data."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "engineering-lab-profile", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    result = []
    page = 1
    while True:
        req = Request(f"{API}/users/{username}/repos?type=owner&sort=pushed&per_page=100&page={page}", headers=headers)
        with urlopen(req, timeout=25) as response:
            payload = json.load(response)
        if not isinstance(payload, list):
            raise ValueError("Unexpected API response")
        result.extend(payload)
        if len(payload) < 100:
            return result
        page += 1
        if page > 100:
            raise ValueError("Pagination exceeded safety limit")


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("API date is missing timezone")
    return parsed


def snapshot(repositories, username, captured_at=None):
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("No repository data; retain previous snapshot")
    rows = []
    for repo in repositories:
        if repo["private"] or repo["owner"]["login"].lower() != username.lower():
            continue
        name = repo["name"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError("Unexpected repository name")
        if not isinstance(repo["fork"], bool) or not isinstance(repo["archived"], bool):
            raise ValueError("Unexpected repository flags")
        pushed = repo["pushed_at"]
        if pushed:
            timestamp(pushed)
        rows.append({"name": name, "url": f"https://github.com/{username}/{name}", "language": repo["language"], "fork": repo["fork"], "archived": repo["archived"], "pushed_at": pushed})
    if not rows:
        raise ValueError("No public owner repositories; retain previous snapshot")
    # Stable ordering lets reviewers inspect exact source data and reproducible artwork.
    rows.sort(key=lambda r: r["name"].lower())
    return {"username": username, "captured_at": captured_at or datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": f"{API}/users/{username}/repos", "repositories": rows}


def recent(data):
    return sorted((r for r in data["repositories"] if not r["fork"] and not r["archived"] and r["name"].lower() != data["username"].lower() and r["pushed_at"]), key=lambda r: timestamp(r["pushed_at"]), reverse=True)[:3]


def display_name(name, limit=40):
    """Use a conservative width budget as well as a character limit for remote names."""
    budget = limit * .53
    width = 0
    for i, char in enumerate(name):
        unit = 1 if char in "MWmw@" else .72 if char.isupper() else .35 if char in "iltfI._-" else .6
        width += unit
        if i >= limit or width > budget - .8:
            return name[:i] + "…"
    return name


def render(data, mobile=False):
    w, h = (480, 514) if mobile else (1000, 430)
    count = len(data["repositories"])
    date = timestamp(data["captured_at"]).strftime("%d %b %Y · %H:%M UTC")
    s = label(28, 33, "PUBLIC WORK / AUTOMATED INDEX", 12)
    s += line(28, 52, w - 28, 52)
    if mobile:
        s += text(28, 96, "Recent development", 29, weight=500, spacing=-1)
        s += text(452, 94, count, 34, weight=500, anchor="end")
        s += text(452, 116, "PUBLIC REPOS", 10, MUTED, mono=True, anchor="end")
        s += line(28, 137, 452, 137)
        sy = 174
    else:
        s += text(28, 111, "Recent development", 38, weight=500, spacing=-1.5)
        s += text(786, 108, count, 40, weight=500, anchor="end")
        s += label(810, 91, "PUBLIC", 11) + label(810, 110, "REPOSITORIES", 11)
        for x, value in [(28, "REPOSITORY"), (640, "LANGUAGE"), (815, "LAST PUSH")]:
            s += label(x, 150, value, 11)
        s += line(28, 166, 972, 166)
        sy = 202
    rows = recent(data)
    if not rows:
        s += text(28, sy, "No eligible public projects to display.", 17, MUTED)
    for i, repo in enumerate(rows):
        y = sy + i * (99 if mobile else 70)
        s += text(28, y, f"{i + 1:02d}", 13, HIGHLIGHT, mono=True)
        s += text(66, y + 1, display_name(repo["name"], 33 if mobile else 43), 21 if mobile else 23, weight=500, spacing=-.3)
        pushed = timestamp(repo["pushed_at"]).strftime("%d %b %Y")
        language = display_name(repo["language"] or "Unspecified", 23 if mobile else 15)
        if mobile:
            s += text(66, y + 28, language, 17, MUTED)
            s += text(66, y + 54, "Last push / " + pushed, 14, MUTED, mono=True)
        else:
            s += text(640, y + 1, language, 16, MUTED)
            s += text(815, y + 1, pushed, 16, MUTED)
        s += line(66, y + (77 if mobile else 27), w - 28, y + (77 if mobile else 27))
    s += text(28, h - 43, "Data captured / " + date, 12, HIGHLIGHT, mono=True)
    s += text(28, h - 20, "Recently pushed original projects. Updated automatically.", 12 if mobile else 14, MUTED)
    description = f"Public GitHub snapshot fetched {date}. {count} public repositories. Recently pushed non-fork repositories, excluding this profile: " + "; ".join(f'{r["name"]}, {r["language"] or "language not reported"}, pushed {r["pushed_at"]}' for r in rows) + ". These timestamps are repository pushes, not personal contribution counts. Automatically regenerated by GitHub Actions."
    return svg(w, h, "Public development — GitHub repository snapshot", description, s)


def readme_links(data, current):
    """Native, accessible source links follow the graphic and track the same snapshot."""
    start, end = "<!-- activity-links:start -->", "<!-- activity-links:end -->"
    if current.count(start) != 1 or current.count(end) != 1 or current.index(start) > current.index(end):
        raise ValueError("Missing or ambiguous generated-link markers")
    links = []
    for repo in recent(data):
        name = repo["name"].replace("_", "\\_")
        links.append(f'[{name}]({repo["url"]})')
    body = " · ".join(links) if links else "No eligible public projects to display."
    content = start + "\n\n" + body + "\n\n" + end
    return current[:current.index(start)] + content + current[current.index(end) + len(end):]


def retain_capture_when_unchanged(data, directory):
    """Do not create hourly bot commits just to advance a timestamp."""
    try:
        previous = json.loads((directory / "snapshot.json").read_text())
        if all(previous[key] == data[key] for key in ("source", "username", "repositories")):
            timestamp(previous["captured_at"])
            data["captured_at"] = previous["captured_at"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return data


def stage(directory, name, content):
    """Prepare in the output filesystem, then use an atomic rename."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, prefix=".activity-", delete=False) as tmp:
        tmp.write(content)
        return Path(tmp.name), directory / name


def publish(data, directory, readme=None):
    contents = {"activity.svg": render(data), "activity-mobile.svg": render(data, True), "snapshot.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n"}
    # Validate the README region before replacing any outputs.
    next_readme = readme_links(data, readme.read_text()) if readme else None
    directory.mkdir(parents=True, exist_ok=True)
    staged = []
    try:
        for name, content in contents.items():
            target = directory / name
            if not target.exists() or target.read_text() != content:
                staged.append(stage(directory, name, content))
        if readme and readme.read_text() != next_readme:
            staged.append(stage(readme.parent, readme.name, next_readme))
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="shiladityamajumder")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets" / "activity")
    parser.add_argument("--from-json", type=Path, help="Offline replay of a saved raw public API response")
    parser.add_argument("--captured-at", help="Actual UTC fetch timestamp of the offline response")
    parser.add_argument("--readme", type=Path, help="README whose marked activity links should be updated; defaults to the profile README for the normal output directory")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.username):
        parser.error("Invalid GitHub username")
    if args.from_json and not args.captured_at:
        parser.error("Offline replay requires the response's actual --captured-at timestamp")
    if args.captured_at:
        timestamp(args.captured_at)
    try:
        repositories = json.loads(args.from_json.read_text()) if args.from_json else fetch_repositories(args.username)
        data = snapshot(repositories, args.username, args.captured_at if args.from_json else None)
        if not args.from_json:
            data = retain_capture_when_unchanged(data, args.output_dir)
        readme = args.readme
        if readme is None and args.output_dir.resolve() == (ROOT / "assets/activity").resolve():
            readme = ROOT / "README.md"
        publish(data, args.output_dir, readme)
    except HTTPError as exc:
        # Do not log headers, authorization, response bodies, or URLs with credentials.
        print(f"GitHub HTTP {exc.code}; keeping last successful activity assets.", file=sys.stderr)
        return 0
    except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
        print("Activity update unavailable or invalid; keeping last successful assets.", file=sys.stderr)
        return 0
    print(f"Published public API snapshot: {len(data['repositories'])} repositories.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
