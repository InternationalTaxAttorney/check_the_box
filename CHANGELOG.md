# Changelog

## 1.1.0 (2026-10-06)

- The answer choices are now shuffled, so the correct answer isn't always in the same position.
- Wrong answers now start with "That is incorrect." instead of relying only on the red background.
- The canonical URL is no longer hardcoded to andrewmitchel.com. Set `CTB_CANONICAL_URL` in the host app's config; otherwise the page's own URL is used.
- Added `ruff` to the dev dependencies.
- Fixed the `Corp.` abbreviation and removed unused code and data.

## 1.0.1 (2026-10-06)

- Added a page title (`title` template variable), which host apps' `header_footer.html` can use for the `<title>` tag.

## 1.0.0 (2026-10-06)

- Restructured as a uv-managed package (`src/check_the_box`) that exposes a Flask Blueprint (`ctb_bp`), so the same code runs on andrewmitchel.com and as a standalone app.
- Moved the JSON data and templates inside the package so they install with it.
- Added a standalone app (`uv run check-the-box`) and tests.
- Fixed the standalone app rendering a template that didn't exist (`index_new.html`).
- Fixed the canonical URL to match the live route (`/resources/check_the_box`).
- Replaced `requirements.txt` with `pyproject.toml` and `uv.lock`.
