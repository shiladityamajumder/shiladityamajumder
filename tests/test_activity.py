"""Failure and data-integrity checks for the only network-backed feature."""

from contextlib import redirect_stderr
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_activity as activity


def repo(name="example", pushed="2026-10-01T12:00:00Z", **extra):
    return {"name": name, "private": False, "owner": {"login": "shiladityamajumder"}, "fork": False, "archived": False, "language": "Python", "pushed_at": pushed, **extra}


class ActivityTests(unittest.TestCase):
    def test_generated_links_follow_data_and_preserve_editorial_content(self):
        data = activity.snapshot([repo("project_b"), repo("project-a", "2026-10-02T00:00:00Z")], "shiladityamajumder")
        current = "Biography stays curated.\n<!-- activity-links:start -->\nold\n<!-- activity-links:end -->\nContact details.\n"
        updated = activity.readme_links(data, current)
        self.assertTrue(updated.startswith("Biography stays curated.\n"))
        self.assertTrue(updated.endswith("\nContact details.\n"))
        self.assertIn("[project\\_b](https://github.com/shiladityamajumder/project_b)", updated)
        self.assertLess(updated.index("[project-a]"), updated.index("[project\\_b]"))
        self.assertNotIn("\nold\n", updated)

    def test_unchanged_data_keeps_capture_date_and_creates_no_file_churn(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            original = activity.snapshot([repo()], "shiladityamajumder", "2026-10-01T13:00:00Z")
            activity.publish(original, directory)
            before = {p.name: p.stat().st_mtime_ns for p in directory.iterdir()}
            fresh = activity.snapshot([repo()], "shiladityamajumder", "2026-10-10T06:00:00Z")
            reused = activity.retain_capture_when_unchanged(fresh, directory)
            self.assertEqual(reused["captured_at"], original["captured_at"])
            activity.publish(reused, directory)
            self.assertEqual({p.name: p.stat().st_mtime_ns for p in directory.iterdir()}, before)
            changed = activity.snapshot([repo(pushed="2026-10-10T01:00:00Z")], "shiladityamajumder", "2026-10-10T06:00:00Z")
            self.assertEqual(activity.retain_capture_when_unchanged(changed, directory)["captured_at"], "2026-10-10T06:00:00Z")

    def test_missing_link_markers_abort_before_replacing_any_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "activity"
            original = activity.snapshot([repo("old")], "shiladityamajumder")
            activity.publish(original, directory)
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            readme = Path(temporary) / "README.md"
            readme.write_text("A README without generation markers.")
            with self.assertRaises(ValueError):
                activity.publish(activity.snapshot([repo("new")], "shiladityamajumder"), directory, readme)
            self.assertEqual({p.name: p.read_bytes() for p in directory.iterdir()}, before)
            self.assertEqual(readme.read_text(), "A README without generation markers.")

    def test_failure_keeps_readme_links_as_well_as_artwork(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "activity"
            readme = Path(temporary) / "README.md"
            readme.write_text("<!-- activity-links:start -->\n<!-- activity-links:end -->\n")
            activity.publish(activity.snapshot([repo()], "shiladityamajumder"), directory, readme)
            before = readme.read_bytes()
            with patch.object(activity, "fetch_repositories", side_effect=TimeoutError()), redirect_stderr(io.StringIO()):
                self.assertEqual(activity.main(["--output-dir", str(directory), "--readme", str(readme)]), 0)
            self.assertEqual(readme.read_bytes(), before)

    def test_recent_uses_push_date_and_excludes_profile_forks_archives(self):
        data = activity.snapshot([
            repo("old", "2025-01-01T00:00:00Z"), repo("new"),
            repo("shiladityamajumder", "2026-10-09T00:00:00Z"),
            repo("fork", fork=True), repo("archived", archived=True),
            repo("private", private=True), repo("other-owner", owner={"login": "elsewhere"}),
        ], "shiladityamajumder")
        self.assertEqual([r["name"] for r in activity.recent(data)], ["new", "old"])
        self.assertEqual(len(data["repositories"]), 5)

    def test_api_pagination_does_not_publish_partial_data(self):
        first_page = [repo(f"project-{i}") for i in range(100)]
        response = io.BytesIO(json.dumps(first_page).encode())
        unavailable = HTTPError(activity.API, 503, "unavailable", {}, None)
        with patch.object(activity, "urlopen", side_effect=[response, unavailable]) as fetch:
            with self.assertRaises(HTTPError):
                activity.fetch_repositories("shiladityamajumder")
        self.assertIn("page=2", fetch.call_args_list[1].args[0].full_url)

    def test_failure_retains_all_existing_assets_and_does_not_log_token(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            activity.publish(activity.snapshot([repo()], "shiladityamajumder"), folder)
            before = {p.name: p.read_bytes() for p in folder.iterdir()}
            for error in [HTTPError(activity.API, 403, "rate limited", {}, None), HTTPError(activity.API, 429, "rate limited", {}, None), TimeoutError(), ValueError("invalid response")]:
                log = io.StringIO()
                with patch.object(activity, "fetch_repositories", side_effect=error), patch.dict(activity.os.environ, {"GITHUB_TOKEN": "test-sensitive-token"}), redirect_stderr(log):
                    self.assertEqual(activity.main(["--output-dir", str(folder)]), 0)
                self.assertEqual({p.name: p.read_bytes() for p in folder.iterdir()}, before)
                self.assertNotIn("test-sensitive-token", log.getvalue())

    def test_invalid_response_and_timestamp_never_replace_snapshot(self):
        for rows in [[], {}, [repo(pushed="not-a-date")], [repo(name="bad<svg>")], [repo(fork="false")]]:
            with self.assertRaises((ValueError, KeyError, TypeError)):
                activity.snapshot(rows, "shiladityamajumder")

    def test_replay_retains_real_fetch_date_and_escapes_remote_labels(self):
        captured = "2026-10-10T05:00:00+00:00"
        data = activity.snapshot([repo(language="<unsafe>&")], "shiladityamajumder", captured)
        for mobile in [False, True]:
            rendered = activity.render(data, mobile)
            self.assertIn("&lt;unsafe&gt;&amp;", rendered)
            self.assertIn("10 Oct 2026 · 05:00 UTC", rendered)
            self.assertNotIn("<unsafe>", rendered)
        self.assertEqual(activity.timestamp(captured), datetime(2026, 10, 10, 5, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
