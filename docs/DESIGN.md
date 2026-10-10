# Systems in Motion — The Engineering Lab

This is a GitHub profile built from Markdown, supported HTML, and local SVG images. There is no application, build service, JavaScript in the README, external font, `foreignObject`, or third-party image widget.

## Visual system

| Role | Color |
| --- | --- |
| Background | `#080D18` |
| Surface | `#111C2E` |
| Primary | `#3B82F6` |
| Highlight | `#60A5FA` |
| Text | `#F8FAFC` |
| Muted | `#94A3B8` |
| Border | `#25344A` |

Blue identifies connections and selected processing nodes. Dark surfaces contain the diagrams in both GitHub themes; native Markdown inherits GitHub's theme. A second light artwork set would add maintenance without improving contrast.

Arial/Helvetica/Liberation Sans form the portable display stack, with system monospace for technical annotations. Editorial weight, a framed architecture study, asymmetric experience typography, ordered section numbers, and generous negative space establish hierarchy. Essential biography, strengths, project descriptions, and contact links remain selectable native text. Diagrams use restrained corner details rather than badge-like side rails; the footer uses sentence-case display typography.

The hero is 1280 × 480. Other desktop graphics use a 1000-unit canvas. At viewport widths up to 600px, `<picture>` selects dedicated 480-unit compositions: stacked hero, experience overview, layered technology map, and folded project flows. This avoids shrinking a desktop diagram into an unreadable mobile strip. Labels describing the artwork also appear in alt text, Markdown, or the technology disclosure.

## Motion and architectural meaning

The hero follows a restrained fourteen-second illustrative request cycle:

1. Client sends a request through the API gateway to FastAPI.
2. FastAPI exchanges data with PostgreSQL and Redis.
3. FastAPI publishes work to RabbitMQ; a Celery worker receives it.
4. A response returns from FastAPI through the gateway to the client.

SMIL packet animation is self-contained. Processing emphasis and the terminal cursor use internal SVG CSS. No animation crosses the name or biography. The graph is an example of synchronous and asynchronous relationships, not a claimed deployment or benchmark; ordering within the animation does not require HTTP responses to wait for worker completion.

Animated graphics include an SVG reduced-motion query. Because embedded SVG media-query behavior differed from standalone SVGs in the preview browser, the README additionally selects explicit static hero and terminal files when reduced motion is requested. These static editions contain no animation elements or CSS animation. Without animation support, the animated hero still shows a complete diagram and hides inactive packets.

The experience panel retains **5+ years** and presents three qualitative strengths: API architecture, distributed workflows, and database engineering. Numerical traffic, latency, and active-user claims were removed at the user's request. There are no simulated measurements, sparklines, or decorative monitoring indicators. The ecosystem represents conceptual layers across multiple projects.

## Content provenance

The repository's original README is the primary source for employers, roles, dates, domains, education, certifications, technologies, Medium articles, and contact details. Both employment entries, DICOM work, geolocation, AWS deployment, and supporting Node.js/NestJS/Fastify experience remain included. Professional accomplishments now describe the engineering work without numerical traffic or performance claims.

Public project source was inspected on 10 October 2026. The diagrams simplify the code; no application was executed and no production or security assessment is implied.

- **VisScan:** [file extraction](https://github.com/shiladityamajumder/visscan/blob/main/app/utils/file_utils.py), [OpenAI parsing](https://github.com/shiladityamajumder/visscan/blob/main/app/services/resume_parser.py), [relevance calculation](https://github.com/shiladityamajumder/visscan/blob/main/app/services/relevance_checker.py), and [MiniLM/cosine similarity](https://github.com/shiladityamajumder/visscan/blob/main/app/utils/similarity_utils.py). Job descriptions are parsed separately. Bulk uploading, a frontend dashboard, and multi-job ranking are excluded because the project README describes them as future work.
- **FastAPI Auth:** [service layer](https://github.com/shiladityamajumder/fastapi/blob/main/fastapi-auth/src/auth/service.py), [JWT/current-user resolution](https://github.com/shiladityamajumder/fastapi/blob/main/fastapi-auth/src/auth/utils.py), [role dependencies](https://github.com/shiladityamajumder/fastapi/blob/main/fastapi-auth/src/auth/permissions.py), and [SQLAlchemy database setup](https://github.com/shiladityamajumder/fastapi/blob/main/fastapi-auth/src/database.py). The graphic separates login/token issuance from later protected requests in its annotation. It does not assert a particular database engine or production readiness.
- **Django REST Auth & CRUD:** [JWT configuration and SQLite default](https://github.com/shiladityamajumder/django-rest-api-auth-crud/blob/main/demo_project/demo_project/settings.py), [permission classes](https://github.com/shiladityamajumder/django-rest-api-auth-crud/blob/main/demo_project/app/permissions.py), and [service CRUD views](https://github.com/shiladityamajumder/django-rest-api-auth-crud/blob/main/demo_project/service/views.py). The protected flow does not imply every route requires authentication, or that every defined permission class applies to every endpoint.

Activity is sourced from the public [GitHub repository API](https://api.github.com/users/shiladityamajumder/repos). The checked-in snapshot records the data capture time and repository metadata. The public count includes forks and archived repositories; the recent list excludes forks, archives, and this profile and sorts by `pushed_at`. The editorial index shows repository names, languages, and push dates, with matching native source links regenerated in the README. A repository push may include collaborator activity. It is not a contribution count, commit frequency, or personal productivity measure.

All artwork regenerates automatically on every profile-repository push and hourly through GitHub Actions; other public repository pushes appear on the next scheduled fetch. Existing snapshot data is retained on API failures. Unchanged payloads reuse their real capture date, so polling does not create timestamp-only commits. Identity, employment, featured-project descriptions, and writing remain intentionally curated; automation does not infer personal accomplishments from GitHub metadata.

## Validation performed

- Parsed all 22 SVGs and checked dimensions, descriptions, IDs, internal references, and absence of external or unsupported SVG content.
- Calculated contrast for white, muted, and highlight text against both artwork surfaces; all six combinations exceed 4.5:1.
- Checked all README image paths, local links, heading anchors, supported HTML, and activity metadata.
- Rendered light and dark previews at 360, 390, 600, 768, and 960px; inspected desktop and mobile screenshots. Browser geometry checks found no clipped or overlapping text and no page overflow.
- Verified picture selection, explicit reduced-motion sources, one packet per sampled request phase, animation in an image embedding, and static rendering with reduced motion.
- Executed nine activity tests covering selection, pagination, invalid responses, HTTP 403/429, timeouts, retention of assets and README links, escaping, timestamps, link updates, marker validation, unchanged-data behavior, and non-disclosure of tokens.
- Validated the profile refresh workflow with actionlint v1.7.12. The unused contribution-snake workflow has been removed.
- Submitted the README to GitHub's Markdown rendering API, which retained the picture elements, mobile media attributes, and details blocks. This does not reproduce the full profile image-proxy/browser pipeline.
- The profile and three project repository URLs returned HTTP 200. Linked source files were fetched successfully from GitHub's raw endpoint; some GitHub file-view URLs returned transient HTTP 503 during batch checks. Medium returned HTTP 403 and LinkedIn HTTP 999, so those original links are preserved and require human verification.

## Verification on the actual profile

After the user publishes the files, inspect the GitHub profile on desktop and mobile, in both themes, with reduced motion enabled and disabled. Confirm relative `<picture>` sources resolve in the profile context, image caching refreshes after asset changes, animations survive the image pipeline, section links navigate correctly, and articles/contact links open normally. If a client suppresses animation, the complete static appearance remains usable. The hourly workflow must be observed on GitHub; it has not been run remotely or pushed as part of this implementation.
