# Personal homepage implementation plan

**Goal:** A white, responsive public homepage in the existing GitHub Pages repository, with explicitly selected EvoMyn articles and preserved legacy notes.

**Architecture:** Python's standard library generates a deployable `dist/` from public JSON and local HTML/CSS assets. A separate local MCP client fetches only individually selected records; GitHub never connects to the local library. The homepage uses the verified GitHub login until the owner supplies a display name and biography.

**Tech stack:** Python 3.11+, HTML, CSS, small browser JavaScript, GitHub Actions / Pages; bundled EvoMyn MCP SDK for local export only.

- [x] Add meaningful tests in `tests/test_publishing.py` for excluding unselected/private fields, HTML escaping, unsafe URLs/slugs, and removal of withdrawn pages. Run with `python -m unittest discover -s tests -v` and verify the missing implementation fails.
- [x] Implement `scripts/sync_evomyn.py`: an explicit local selection manifest, `archive_get` per selected ID, strict title/body/date projection, and atomic public export. Empty selection must not require a running service. Never copy attachments, relationships, fields, or the database.
- [x] Implement `scripts/build.py`, `src/page.html`, `src/style.css`, and `src/main.js`: a static homepage, project/article sections, article pages, search, accessible navigation, empty states, escaped text, safe links, and fresh output per build.
- [x] Populate `content/site.json` using only the verified username and existing public Python note; keep `legacy/README.md` intact. No invented biography, dates, projects, or contact details.
- [x] Add `.gitignore`, `.github/workflows/pages.yml`, and maintenance documentation. Only `dist/` becomes the Pages artifact; local selection manifests and the original library remain outside publication.
- [x] Run unit tests, build, a desktop/mobile browser check, navigation/search checks, and an independent code review. Show the local preview to the owner.
- [x] Prepare a reviewable GitHub branch and pull request. Preserve the existing main branch while the owner reviews the first version and supplies biography/project content. Report any Pages configuration or authentication limitation accurately.
