# Maintaining the engineering lab

## Files and sources

- `README.md` owns curated professional copy and links. Only the marked recent-project links are generated.
- `scripts/svg_design.py` owns the SVG vocabulary and design tokens.
- `scripts/generate_assets.py` owns the hand-designed compositions; it generates 20 SVGs, including four explicit static motion fallbacks.
- `scripts/generate_activity.py` generates two activity SVGs, a minimal dated `assets/activity/snapshot.json`, and native recent-project links from public GitHub data.
- `scripts/validate_profile.py` provides dependency-free structural validation.
- `scripts/preview.py` builds an ignored local preview with optional `markdown-it-py`.
- `scripts/verify_visuals.cjs` provides optional browser checks and screenshots using Playwright.

Edit the generators rather than the generated SVG files. After publication, every push to this profile repository rebuilds all artwork, and hourly runs fetch GitHub activity across public repositories. There is no need to edit any SVG when pushing code. For color changes, update the constants in `svg_design.py`; the workflow regenerates the artwork. Identity, employment history, selected-project descriptions, education, and article selections stay curated. The profile retains 5+ years of experience and qualitative engineering strengths rather than performance claims.

## Regenerate and validate

Python 3.11 or newer is sufficient for production asset generation. There are no runtime package dependencies.

```bash
python3 scripts/generate_assets.py
python3 scripts/generate_activity.py
python3 scripts/validate_profile.py
python3 -m unittest discover -s tests -v
git diff --check
```

`generate_activity.py` works without a token for public data. Set `GITHUB_TOKEN` in the environment when authenticated rate limits are needed; do not put credentials in command arguments, code, snapshot files, or the README. Fetches use a timeout, follow pagination to completion, filter public owner repositories, and validate data before staging output. HTTP errors, rate limits, timeouts, and invalid responses print a generic message and leave the previous artwork, data, and generated links intact. Failed updates return success so a network outage does not disrupt the profile.

The capture time advances when repository data changes. If the payload is unchanged, the previous capture date is reused and identical files are not rewritten. This avoids hourly bot commits that only change timestamps. Missing or duplicated README generation markers abort an update before any assets are replaced. Only the region between `activity-links:start` and `activity-links:end` is regenerated; professional content outside it is preserved.

For an offline replay, save an actual raw response and its actual fetch time:

```bash
python3 scripts/generate_activity.py --from-json /tmp/github-repos.json --captured-at '2026-10-10T05:08:10+00:00' --output-dir /tmp/activity-replay
```

The example timestamp must be replaced with the response's real fetch time. Never invent a capture date or repository data.

## GitHub Actions

`update-activity.yml` rebuilds all graphics on **every push to `main` in this profile repository**, **hourly at minute 17 UTC** (minute 47 in India), and manual dispatch. It also fetches activity from all public repositories. A push to another repository does not directly trigger a workflow here; it is picked up by the next hourly poll. No additional source-repository workflows or personal access token are required for polling.

The job uses `github.token`, runs structural validation and the activity tests, and commits changed `assets/` plus generated README links. GitHub schedules can be delayed; this is automatic regeneration rather than per-view live rendering. The workflow file must be on the default branch, Actions must be enabled, and the job needs permission to push to `main`. If branch protection blocks bot pushes, adapt the commit step to a pull-request workflow. See [GitHub's event and schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Concurrency serializes scheduled refreshes. A concurrent user push can cause Git to reject the generated commit; the next refresh retries from the latest `main` without force-pushing. API failures preserve the last committed visualization and its links. Check workflow logs when troubleshooting; an old capture date can mean unchanged data or a failed fetch. Bot commits made with `GITHUB_TOKEN` do not recursively trigger another push run, as described in [GitHub's workflow trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

The profile refresh workflow is the only workflow needed. The unused contribution-snake workflow has been removed. The refresh job is restricted to the original repository so forks do not write back unexpectedly. No remote branches or previously published artifacts were deleted as part of the local cleanup.

## Local preview

The optional preview tools can be installed in temporary directories; they are not dependencies of the profile or hourly workflow.

```bash
python3 -m venv /tmp/engineering-lab-preview-python
/tmp/engineering-lab-preview-python/bin/pip install markdown-it-py
/tmp/engineering-lab-preview-python/bin/python scripts/preview.py
```

Open `preview/index.html` in a browser. The folder is ignored by Git and can be deleted after review; regenerate it whenever needed. It approximates GitHub's Markdown width and theme; it is not proof of profile compatibility. Profile SVGs and `snapshot.json` remain tracked because GitHub displays the committed assets.

For browser automation, use Node 20+:

```bash
npm install --prefix /tmp/engineering-lab-preview-node playwright
/tmp/engineering-lab-preview-node/node_modules/.bin/playwright install chromium
PLAYWRIGHT_MODULE=/tmp/engineering-lab-preview-node/node_modules/playwright node scripts/verify_visuals.cjs
```

The check renders both themes at five widths, checks geometry and overflow, exercises the animated request cycle, verifies static reduced-motion image selection, and writes screenshots plus `preview/validation.json`. For workflow validation, run `actionlint .github/workflows/*.yml` with the official actionlint tool. Neither preview dependencies nor screenshots need to be committed.

## Publishing and future content changes

Review the diff and publish through your normal Git process. This implementation does not push automatically. After publication, use the actual-profile checklist in [DESIGN.md](DESIGN.md#verification-on-the-actual-profile).

Retain the `<picture>` source order: mobile + reduced motion first, reduced motion second, mobile third, desktop image last. Static editions are generated automatically and keep reduced-motion behavior dependable even when an image renderer does not honor internal SVG media queries.

When a project evolves, inspect its source before changing a diagram. In particular, check VisScan's extraction/matching services, FastAPI Auth's JWT and permission dependencies, and Django's authentication, serializer, permission, and database configuration. The source-based description stays curated; the generated files update from the scripts automatically. Keep article and contact links native, accessible, and independently usable.
