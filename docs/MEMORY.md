# Memory use

How much RAM the TileSmith desktop app uses, how it was measured, and what the numbers do and do not tell you.

**Short answer:** TileSmith 3.10 (Electron) used about **380 to 410 MB** with the default project and about **500 MB**
with a large show (four walls of 200 tiles on a 4K canvas), counted across all six of its processes. An empty
Electron window on the same machine used about **286 MB**, so roughly three quarters of TileSmith's memory is the
Electron/Chromium runtime itself and about 100 to 220 MB is the app.

There is no native (Rust) version of TileSmith yet, so there is nothing to compare these figures with. A rewrite has
been discussed (see [kingof9x/Tilesmith-RUST](https://github.com/kingof9x/Tilesmith-RUST), which holds only a README
and copies of the docs). When one exists, measure it with the same script and the same states so the comparison is
like for like.

## Results

TileSmith **3.10**, the released Linux AppImage (`TileSmith-linux-x64.AppImage` from the v3.10 release, Electron 44,
Chromium 152), measured on 2026-11-25. Each state was held for 40 seconds before sampling. Raw numbers, including
every process on its own, are in [`memory-results-3.10-linux.json`](memory-results-3.10-linux.json).

| State | Processes | PSS (headline) | USS (private) | RSS (over-counts) |
|---|---:|---:|---:|---:|
| Empty Electron 44 window (no TileSmith), for reference | 6 | 286 MiB | 168 MiB | 609 MiB |
| Idle, default project (one 6 × 4 wall) | 6 | 384 MiB | 256 MiB | 706 MiB |
| LED build animation running | 6 | 392 MiB | 264 MiB | 715 MiB |
| DVD screensaver running | 6 | 410 MiB | 281 MiB | 733 MiB |
| Idle again after both | 6 | 408 MiB | 279 MiB | 731 MiB |
| Big show, idle (4 walls × 200 tiles, 3840 × 2160 canvas, data and power wiring shown) | 6 | 500 MiB | 373 MiB | 822 MiB |
| Big show, LED build running | 6 | 502 MiB | 375 MiB | 824 MiB |

Where it goes, idle with the default project (PSS): renderer (the page itself) 129 MiB, GPU process 108 MiB, main
process 88 MiB, network/utility process 27 MiB, two zygote helpers 32 MiB.

Repeat runs on the same machine landed within about 5% of each other (idle: 361 to 384 MiB PSS over four runs).

## How it was measured

- **Tools:** [`manual-src/tools/measure_memory.py`](../manual-src/tools/measure_memory.py) reads `/proc/<pid>/smaps_rollup`
  for the app's whole process tree and adds it up.
  [`manual-src/tools/memory_scenarios.js`](../manual-src/tools/memory_scenarios.js) starts the app with Playwright, puts it
  in each state and calls the first script.
- **Machine:** a cloud Linux container (4 vCPU Intel Xeon 2.1 GHz, 16 GB RAM, kernel 6.18), no screen and no graphics
  card. The app ran under Xvfb (a virtual X display, 1920 × 1080), so Chromium drew with its software renderer
  (SwiftShader). Settings and saved state started empty each run (`HOME` and `XDG_CONFIG_HOME` pointed at an empty
  folder).
- **To repeat it** (Linux, from the repository root):

  ```sh
  ./TileSmith-linux-x64.AppImage --appimage-extract          # gives squashfs-root/tilesmith
  export HOME=$(mktemp -d) XDG_CONFIG_HOME=$HOME/.config        # start from no saved settings
  xvfb-run -a -s "-screen 0 1920x1080x24" node manual-src/tools/memory_scenarios.js squashfs-root/tilesmith
  # or one quick number for any app:
  xvfb-run -a python3 manual-src/tools/measure_memory.py --wait 20,60 -- squashfs-root/tilesmith --no-sandbox
  ```

## What the three numbers mean

- **PSS** (proportional set size) splits each shared memory page between the processes that share it, so adding PSS
  across processes does not count anything twice. It is the fairest single figure for "what this app costs in RAM", and
  it is the headline here.
- **USS** (unique set size) is memory only that process uses: what you would get back by quitting it. It is close to
  Windows Task Manager's default *Memory* column (private working set).
- **RSS** (resident set size) counts shared libraries again in every process, so adding RSS across processes
  over-counts. It is what `top` and `ps` show by default.

## Reading other people's numbers

- **Count every process.** Electron starts a main process, a renderer per window, a GPU process, a network/utility
  process and helpers. Task Manager, Activity Monitor and `top` list each one on its own line, and some of them are
  small (one zygote here used under 1 MiB of private memory). One line on its own is not the app.
- **Same states, same machine.** Memory grows with canvas size and tile count (100 MB more for the big show above) and
  a little after an animation has run, so compare like with like.
- **Platform differs.** These are Linux figures with software rendering. On Windows and macOS with a real graphics card
  the GPU process and the totals will be different; they have not been measured yet. To measure on Windows, add up the
  *Memory (private working set)* of every `TileSmith.exe` in Task Manager's Details tab, which is close to the USS
  column above.

## Keeping it down

The manual's chapter "Keeping CPU and memory use low" has the practical tips: fit the canvas to the walls, use a lower
frame rate, and stop animations you are not using. Uploaded images are kept in memory and in the saved project as data
URLs, so very large images add to both.
