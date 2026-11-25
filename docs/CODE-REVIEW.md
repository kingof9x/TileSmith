# Code review and stress test, November 2026

A review of the desktop app (Electron, `tilesmith-desktop/`) to prepare it for an outside reviewer: what was checked,
what was found, what was fixed, and what is still open. The app version reviewed is main at `1b9364f` (v3.10 docs).

## What was reviewed

| Part | Size | How it was checked |
|---|---|---|
| `tilesmith-desktop/app/index.html` | 2.1 MB; about 4,750 lines of JavaScript plus the tile catalogue, translations and embedded test-pattern images | Read section by section, ESLint (undefined names, duplicate keys, unreachable code), CPU profiles of the hot paths, the stress tests below |
| `tilesmith-desktop/main.js` | Electron main process, 66 lines before this review | Read in full; run in real Electron 44 under Xvfb |
| `manual-src/tests/` | 48 Playwright tests | Run in full; the 10 that failed were traced to their cause |

Not covered: the Android / iOS wrappers beyond their existing tests, NDI®, Spout and Syphon on real hardware (needs
Windows / macOS and a GPU), and the documentation scripts in `manual-src/`.

## How to run the checks

```
pip install playwright pillow pypdf && python -m playwright install chromium   # pdftotext comes with poppler-utils
(cd manual-src/tools && npm install)                                          # for lists_test.py
python3 manual-src/tests/run_all.py                                           # every test, one line each
python3 manual-src/tests/run_all.py stress electron                           # just these two
```

`run_all.py` judges each test by its exit code and by what it prints (some older tests print FAILED but exit 0).
`electron_test.py` runs the real desktop app; it needs `npm install` in `tilesmith-desktop` and prints SKIPPED without
it. The new GitHub workflow `.github/workflows/tests.yml` runs everything on each pull request.

## Fixed in this review

| # | Finding | Severity | Fix | Proof |
|---|---|---|---|---|
| 1 | The app window has Node.js access (nodeIntegration on, contextIsolation off). A clicked web link that was not one of the app's own handled links would navigate that window to a website, which would then have full access to the computer. | High | `main.js` now refuses any navigation away from the app, sends web and mail links to the system browser, and refuses child windows that are not `about:blank` (output windows and print previews are blank windows the page writes into). | `electron_test.py`: a clicked link and `window.open` of a web address both stay out of the app. Before the fix the same click navigated the window away. |
| 2 | **Update now** downloaded the new installer and ran it without checking it. | Medium | The download must match the SHA-256 GitHub publishes for the release file (`digest`) before it runs; on a mismatch nothing is installed. Releases without a digest behave as before. | `electron_test.py` (wrong digest refused, right digest installs, no digest installs). |
| 3 | Autosave wrote `state.json` in place. A crash or power cut during the write left a half file; the next start could not read it, silently started fresh, and the next autosave destroyed the old session. | Medium | Autosave writes `state.json.tmp` and renames it over `state.json` (atomic on Windows, macOS and Linux). An unreadable `state.json` is kept as `state.json.unreadable-<time>` and the user is told. | `electron_test.py` with a truncated `state.json`. |
| 4 | Pictures inside a project file (logo, DVD logo, pattern and box images, crew photos) could be any address. Opening a hand-edited or hostile project made the app fetch from the internet (a tracking pixel) or read a local file, and a picture from another origin blocks reading the canvas back for NDI®, Spout / Syphon, PNG and video. | Medium | Only embedded `data:image/...` pictures are loaded; anything else is ignored. Two places that assumed the picture always loads now check. | `stress_test.py` part 2: no network requests. Before the fix: requests to both test addresses. |
| 5 | The tile catalogue listed **YES TECH Xtra 1.9** twice with different figures (163 W from the YES TECH sheet, 145 W further down). JavaScript keeps the last, so power planning used 145 W. | Medium (power numbers) | The duplicate is removed; the manufacturer figure (163 W, also the safer one for circuit loading) is kept with a comment. **Please confirm against the current YES TECH sheet.** | ESLint `no-dupe-keys` now clean. |
| 6 | 10 of 49 tests failed on main: 7 because the app had moved on and the tests had not (output checkboxes since multi-output, a new wall starts without power circuits, new brands, the cable label now comes before circuit labels, Character packs removed, the bug-report button moved, mocks without `process.execPath`) and 3 because of paths on one machine (`/home/claude/...`, an old scratchpad, a `/tmp` fixture). | Process | Tests updated to the current behaviour (each change commented), `charpack_test.py` removed with its feature, `techstyle_test.py` rewritten for Classic / Hand-drawn / Backlit, all tests find the app from the checkout (`tests/_paths.py`), `run_all.py` added. | 48 of 48 pass, plus the two new tests. |
| 7 | Wall totals (`wst`) added up every tile on every call, and the tile cache (`pieces`) built a 12-field key string on every call, thousands of times per frame. Tile-position labels measured their text on every tile of every frame. | Low (speed) | `pieces()` checks its cache field by field first; `wst()` is kept with the cached tiles; text widths are cached. | `stress_test.py` timings: refreshing the panels (`sync`) on ten 64 × 64 walls 360 ms -> 250-290 ms; one wired 64 × 64 wall 40 ms -> 23-28 ms; drawing about 10 % faster. |

Also new: a map of how the page works at the top of its main script, section headers where they were missing, a
header for `main.js`, and a comment above **every** top-level function in `index.html` (what it does, its inputs and
outputs, and why where it is not obvious), above the main data tables (`S`, `LIM`, `WK`, `walls`, `UN`, `REC`...) and
at each step inside the largest functions (`render`, `info`, `tick`, the input handler). About 1,280 comment lines in
all. GitHub does not show a file this size in the browser ("View raw" works); search the file for `// name(` to find
the comment for any function.

## Stress test results

`manual-src/tests/stress_test.py`:

* **HTML in every text field** of a busy project (three walls, wiring, distro, locations, labels, cable lengths,
  rigging): shown as text in 275 places, never run. All project text goes through `esc()`; the XML, SVG and PDF
  writers escape too. (`esc` does not escape `'`; every attribute in the code uses double quotes, keep it that way.)
* **850 damaged projects** (random fields set to wrong types and extreme values; 150 in the test, 700 more in two longer runs):
  no errors when opening and then using every panel, render, plans, spec sheet, labels and undo. The loader only takes
  known keys of the right type and clamps numbers to `LIM`.
* **Scale** (headless Chromium, drawing on the CPU, so slower than a desktop with a GPU):

| Project | Tiles | Draw one frame | Refresh panels | Autosave | Undo snapshot |
|---|---|---|---|---|---|
| Default wall | 24 | 1 ms | 2 ms | < 1 ms | < 1 ms |
| One 64 × 64 wall (the maximum), 4K canvas, data and power wired | 4,096 | about 100 ms | about 25 ms | < 1 ms | < 1 ms |
| Ten 64 × 64 walls | 40,960 | about 1.5 s | about 0.27 s | < 1 ms | 1 ms |

Saved state stays small (4-12 KB without pictures) because walls are stored as settings, not tile lists.

## Open findings (not changed)

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| A | **Node.js in the page.** The page calls `require()` directly (files, NDI® through koffi, Spout / Syphon, ffmpeg, updates). With `contextIsolation` off and no sandbox, any script that ever ran in the page would have the user's full access. Today the risk is contained by escaping (finding 1 of the stress test) and by the navigation lock above. | Medium (architecture) | Move every Node.js use into a preload script exposed with `contextBridge` (a list of about 15 functions: read/write file, NDI®, Spout, Syphon, spawn ffmpeg, updater) and turn on `contextIsolation` and `sandbox`. Large change; worth doing before any feature that shows outside content. |
| B | **No Content-Security-Policy.** | Low | Add one once A is done (the page uses inline scripts, so a useful policy needs A first). |
| C | **ffmpeg add-on downloads are not checked.** ffmpeg comes from gyan.dev (Windows) or osxexperts.net / evermeet.cx (Mac) and on Windows 10 `7zr.exe` from 7-zip.org; each is run after download without a checksum. Downloads are HTTPS only. | Medium | Pin versions and check a SHA-256 listed in the app (gyan.dev publishes `.sha256` files), or ship ffmpeg in the installer. |
| D | **Drawing cost grows with tile count.** The master canvas is drawn in full on the CPU (`willReadFrequently`) for each changed frame; at the 64 × 64 maximum on several walls a frame takes over a second here and typing lags. Usual shows (a few hundred tiles) draw in a few ms. | Low | The plan already agreed: cache the parts that do not move (tiles, labels, wiring) in a layer and redraw only what moves. |
| E | **One 2.1 MB file with global state.** About 760 top-level functions share globals (`S`, `walls`, `CVS`...). It works and the tests reach into it easily, but it is hard to review in parts. ESLint lists 107 unused variables, worth a clean-up pass. | Low (maintainability) | Split into modules only as part of a planned rewrite; until then keep the section headers and the map at the top current. |
| F | **Version strings in the source read 3.5** until `scripts/set-version.js` stamps the release number into `index.html`, `main.js` and the package files. The build workflow does this, and fails if a stamp in the page is missed. | Info | None; a reviewer running from source sees 3.5. |
| G | Real NDI®, Spout and Syphon output, video export with ffmpeg and the installers were not exercised here (no Windows / macOS, no GPU). The existing tests use stand-ins for those libraries. | Info | Check on a real show machine before a release. |
