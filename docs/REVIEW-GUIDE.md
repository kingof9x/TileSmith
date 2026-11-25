# Reviewer's guide

For someone reviewing TileSmith's code, documentation or claims: what the app is, how it is put together, how to
check it, and what is known to be weak. Written 2026-11-25 against `main` at commit `1b9364f` (released as v3.10), with the test and code-review changes of
pull request #57.

## What TileSmith is

A pre-production tool for LED video walls. You lay out walls of LED tiles on a canvas, and TileSmith draws test
patterns and pixel maps, works out processor ports and data paths, power circuits, cables, rigging and a pull sheet,
prints labels and a show binder, and sends the canvas live over NDI®, Spout or Syphon. An animated technician can build
the wall tile by tile on screen.

It is a hobby project by one person, written with heavy help from AI coding tools (the README says so). The engineering
figures come from manufacturers' spec sheets and are meant to be checked by a qualified person before a show (see the
disclaimer in the README).

## How it is built

| Part | Where | What it does |
|---|---|---|
| The app | `tilesmith-desktop/app/index.html` (about 2.1 MB, 6,300 long lines) | The whole program: HTML, CSS and JavaScript in one page, no framework and no build step. Every platform runs this same file. |
| Desktop shell | `tilesmith-desktop/main.js`, `package.json` | Electron 44. Opens one window on `index.html`, plus output windows for "send this canvas to a display", and handles screenshots for bug reports and the hand-off to the installer for *Update now*. |
| Native outputs | inside `index.html`, loaded only in the desktop app | NDI® through the NDI® runtime library, and Spout (`bin/spout/SpoutDX.dll`) on Windows, both called through [koffi](https://koffi.dev/) (a foreign function interface for Node). Syphon on Mac through node-syphon (`bin/mac/syphon`). |
| Video export | inside `index.html` | Starts `ffmpeg` as a child process and pipes raw RGBA frames into it (HAP, ProRes, H.264). |
| Mobile apps | `tilesmith-desktop/mobile/` (Capacitor 8), `tilesmith-desktop/android-aistudio/` (Kotlin WebView) | Wrap the same `index.html`; a small bridge (`window.TSM`) saves files through the share sheet. |
| Builds and releases | `.github/workflows/release.yml`, `docs.yml`, `virustotal.yml`, `pr-test-builds.yml` | *Build and release* (run by hand with a version number) builds Windows, Mac, Linux and Android, then *Build documentation* attaches the manuals and spec, then *VirusTotal* scans every file and writes `VIRUSTOTAL.md`. |
| Docs generators | `manual-src/` | Python + Playwright scripts that open the real app, take the screenshots and print the manuals (`make_manual.py`, `make_mobile_manual.py`), the spec (`make_spec.py`) and the README images. |

### Inside `index.html`

- **State.** One settings object `S` holds the selected wall's settings and the project-wide ones; `walls` holds every
  wall on the current canvas (the per-wall keys are listed in `WK`), and `CVS` holds the canvases. `storeWall()` copies
  `S` back into the selected wall. `sync()` brings every panel in line with the state.
- **Drawing.** `render()` draws the master canvas: every wall, its pattern, tile grid, labels, and data and power paths
  (`portPlan()` and `powerPlan()` work those out). `vpDraw()` copies it into the on-screen viewport at the current zoom.
- **The loop.** `loop()` runs on `requestAnimationFrame`. `tick()` steps animations at up to 60 frames a second but
  only calls `render()` when something changed or moves (the build, the DVD logo, animated patterns); a still picture
  is redrawn about four times a second. This keeps CPU use low when nothing moves.
- **Outputs.** NDI®, Spout, Syphon and video export share one `getImageData` read of the canvas per frame.
- **Saving.** Every change is saved 0.4 s later (`saveSoon`): to `state.json` in the user's TileSmith folder on the
  desktop, or `localStorage` on the web. Undo keeps the last 20 snapshots. *Save* writes a `.tilesmith` project file.
- **Translations.** `TR` maps every English string to nine other languages; text is translated in place as panels
  render.
- **Data tables.** Tile models (more than 400, each with its maker's source), processors (`PROC`) and power data are
  plain object literals in the file.

## How to check it

**Run the app.** Open `tilesmith-desktop/app/index.html` in Chrome or Edge for everything except the native outputs,
or `npm install && npm start` in `tilesmith-desktop` for the Electron app.

**Run the tests.** The tests in `manual-src/tests/` are Python scripts that drive the real page with Playwright and
print `PASS`/`FAIL` lines. `run_all.py` runs them all and judges each by its exit code and its output; the GitHub
workflow `.github/workflows/tests.yml` runs the same command on every pull request and push to `main`.

```sh
pip install playwright pillow pypdf && python3 -m playwright install chromium   # pdftotext comes with poppler-utils
(cd manual-src/tools && npm install)                                           # acorn + prettier, for lists_test.py
python3 manual-src/tests/run_all.py                                            # every test, one line each
```

`electron_test.py` starts the real desktop app and needs `npm install` in `tilesmith-desktop` (it prints SKIPPED
without it). `stress_test.py` loads very large projects and long animation runs.

**History:** on `1b9364f` (v3.10), before the runner and workflow existed, 39 of 49 tests passed. The 10 failures were
out-of-date tests (removed Character pack, new tile brands, changed output picker and top bar), two tests with
hardcoded paths or a missing fixture, and some tests exited 0 even when they printed `FAILED`. Pull request #57 fixed
them; [CODE-REVIEW.md](CODE-REVIEW.md) lists every finding from the code review and stress test, what was fixed and
what is still open.

**Check the numbers.** Engineering figures (tiles per port, power per circuit, phase currents) are explained with
worked examples in the manual (chapters 10 to 13) and in `TileSmith-App-Spec.md`, with the maker's source for every
tile model shown in the Engineering panel.

**Check the downloads.** `VIRUSTOTAL.md` lists the SHA-256 and the VirusTotal report of every file in each release.

## Known limitations and risks

- **Security model.** The desktop window runs the page with `nodeIntegration: true` and `contextIsolation: false`, so
  the page has full Node.js access. That is how the native outputs and file saving work. It is acceptable only because
  the page is local and loads no remote code. The code review added guards so the window cannot navigate away from the
  app and links open in the system browser; see [CODE-REVIEW.md](CODE-REVIEW.md).
- **Unsigned builds.** Windows SmartScreen and macOS Gatekeeper warn on first start.
- **Tested in production on Windows only.** Mac, Linux and the mobile apps are experimental (README disclaimer).
- **Third-party runtimes are not bundled** in the GitHub downloads: NDI® Runtime and ffmpeg are installed separately
  (or through *Info › Add-ons*).
- **One 2 MB file.** Easy to ship and to run anywhere, hard to navigate. `manual-src/make_readable_source.py` splits it
  into `app.js` and `style.css` with a function index for reading.
- **Version strings.** `index.html` carries `3.5` in the source; `scripts/set-version.js` stamps the real version at
  build time, so a run from source shows v3.5.
- **Memory.** About 380 to 500 MB on Linux, three quarters of it the Electron runtime. See [MEMORY.md](MEMORY.md).
- **Power and rigging figures are planning figures.** They follow the makers' sheets and common practice (80% loading,
  phasor sums for line-to-line circuits) but have not been checked against a real distro meter or rigging plot.

## Where to read more

- [README](../README.md): features, downloads, building.
- `tilesmith-desktop/TileSmith-Manual.pdf` and `TileSmith-Mobile-Manual.pdf`: the user manuals.
- `tilesmith-desktop/TileSmith-App-Spec.md`: the full written specification (every setting, formula and pattern).
- [CODE-REVIEW.md](CODE-REVIEW.md): findings from the November 2026 code review and stress test.
- `manual-src/WORKFLOW.md`: how releases and parallel pull requests are run.
