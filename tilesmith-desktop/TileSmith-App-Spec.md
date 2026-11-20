# TileSmith 3.10 - app specification for building a clone

Generated 2026-11-20 from TileSmith v3.10 (`app/index.html`). This file describes what the app does, how it looks,
how every feature behaves and the exact numbers and formulas behind it, so another AI model or developer can rebuild it,
for example as an Android app. Tables of presets, processors, patterns, settings and formats are read from the app
itself when this file is generated, so they match the version it ships with. Section 15 has notes for Android.

## 1. What the app is

TileSmith is a pixel-mapping and test-pattern tool for LED video walls, used by LED technicians at events.

- The user lays out one or more **LED walls** (grids of LED tiles, also called cabinets or panels) on a **canvas**: the
  video raster a media server or LED processor outputs (for example 1920x1080).
- Each wall shows a **test pattern** (pixel maps, colour bars, gradients, uploaded images).
- An **engineering panel** works out pixels, area, weight, power, processor ports and power circuits.
- **Data wiring** (which processor port feeds which tiles) and **power wiring** (which circuit feeds which tiles) can be
  planned automatically or by hand and are drawn on the canvas.
- An animated **technician** builds each wall tile by tile, for live display or video.
- The canvas is sent live as an **NDI®** video source, shared with other programs on the same computer through
  **Spout** (Windows) or **Syphon** (Mac), and can be recorded to video, exported as PNG, layered SVG or PSD, a PDF (full raster, spec sheet and cable labels) or
  a Resolume Arena Advanced Output preset.

Everything runs offline in one HTML page (vanilla JS + Canvas 2D). The desktop build wraps it in Electron and adds
NDI® output (via the NDI® runtime library), Spout output on Windows (SpoutDX.dll from the Spout SDK), Syphon output on
Mac (Syphon.framework via node-syphon) and video export (via ffmpeg). All settings save automatically.

## 2. Glossary

- **Canvas**: the full output raster (cw x ch px). Anything not covered by a lit tile is black.
- **Wall**: a grid of `cols x rows` cells at canvas offset (ox, oy). Wall size in px = cols x tw by rows x th.
- **Tile / cabinet / panel**: one LED product unit, tw x th px and wmm x hmm mm, with weight and max watts.
- **Piece**: one physical tile placed on the wall. Normally one per grid cell; with half tiles a piece can be half a
  cell, or a full tile offset by half a cell or turned on its side (section 6).
- **Lit tile**: a tile the technician has placed (during the build only lit tiles show the pattern).
- **Port (P#) / return (R#)**: a processor output feeding a chain of tiles; R# marks the last tile of a chain.
- **Circuit**: a power circuit feeding a chain of tiles. Socapex cable = 6 circuits.

## 3. Screen layout

Desktop: three columns. Left panel (settings, 350 px), centre (top bar + viewport), right panel (engineering, 310 px).
Below 900 px wide the columns stack. Colours: dark UI (`--bg`, `--pn` panel, `--ac` teal accent #22a0ac-ish, `--am`
amber for the version). Header: "TileSmith v3.10" and subtitle "LED Wall Pixel Map & Test Pattern Generator".

### 3.1 Left panel sections and submenus (in order)

Sections are collapsible `<details>`; submenus are nested collapsible blocks. Sections marked with the wall name edit
the selected wall.

Top-level sections open and close freely. Submenus open one at a time within their parent: opening a submenu closes
the other open submenus that share its parent (nested submenus and other sections are left alone), 0.32 s after the
click so a second click can still land on the same header. Double-clicking a submenu header opens it and keeps the
others open. Add canvas opens the new canvas alone. Header text is not selectable.

- **Canvases**
  - Canvas 1 1920×1080
    - LED walls
    - Tile model
      - Tile details
    - Size of LED Wall
    - Wall position
    - Test pattern
    - Tile borders & overlays
- **Engineering**
  - LED processor
    - Data wiring
  - Cabinet IDs
  - Power
    - Supply
    - Load
    - This wall
  - Cable lengths
  - Rigging
  - Locations
  - Show binder
- **Animation Options**
  - Test pattern
  - DVD screensaver
  - LED build
  - Tile faults
  - Technicians
  - Video export
- **Output options**
  - NDI® options
  - Spout / Syphon options
- **Label printing options**

Visibility rules:
- Data wiring (inside LED processor) and all processor fields appear only when a processor other than None is picked;
  otherwise a hint "Pick a processor to see tiles per port and plan data wiring."
- Everything under Power except the "Power distribution" checkbox (including the Power wiring submenu) appears only
  when that box is ticked.
- Half-tile controls appear only when the wall's tile model has a half version (section 6).
- Tile-shade color appears directly under the Test pattern list, only for tileshade and tileshade-clean.
- Image fit appears only for image patterns; HAP type only for the HAP format; DVD controls only when DVD is on.

### 3.2 Top bar

Buttons: **New Project**, **Save**, **Open**, **Undo ▾**, **Show entire canvas**, **Center canvas**, **Data**, **Power**, **Phase**, **Next pattern**, **Start NDI®**, **Start Spout / Syphon**, **Export PNG**, **Export PDF**, **Export binder**, **Export layers ▾**, **Resolume XML ▾**, **Start LED Build**, **Start DVD Screensaver**, **Start Tile Faults**, **ⓘ Info**, **Report a bug / feedback**, **Hide Engineering Data**. Then a red recording status, the zoom level (e.g. "41%") and an fps readout ("still" when nothing
moves). Resolume XML is a drop-down (One slice per LED wall / One slice per tile). "Export layers ▾" is a drop-down (Layered SVG… / Layered PSD…). "Start NDI®" toggles NDI; while
live it is green with a dot and reads "Stop NDI®". Right after it, "Start Spout" (Windows) or "Start Syphon" (Mac)
toggles that output the same way ("Stop Spout" / "Stop Syphon", green); the button is hidden in the web version and in a
desktop build made without the Spout/Syphon files. Short messages (NDI started/stopped/errors, Resolume saved, Next
pattern name) appear as a toast at the bottom centre for 2.5-9 s. In a cramped viewport (narrower than 640 px or a
window under 520 px tall) the top bar wraps onto several rows. After the export buttons: "Start LED Build" / "Stop LED Build",
"Start DVD Screensaver" / "Stop DVD Screensaver" and a Zoom slider (log2 of zoom relative to Show entire canvas, -2 to +4).
Right after "Center canvas", "Data" and "Power" toggle `S.showData`/`S.showPow` (the same flags as the "Show data paths" /
"Show power runs on the canvas" checkboxes in Engineering) and get a `tgon` CSS class (accent-coloured border/text) while on;
turning either off also exits its tile-by-tile wiring edit mode if it was active.
The last item in the bar is a full-width `.bar-split` row (`justify-content:space-between`, always wraps onto its own line):
a nested group with "ⓘ Info" and "Report a bug / feedback" sits at its left end and "Hide Engineering Data" sits at its right end.
That button reads "Hide Engineering Data" while the panel is shown and "Show Engineering Data" while it is hidden; it toggles `S.hideEng`; while true, `#app` gets a `no-eng` class that sets `#right{display:none}` and, at
widths over 900 px, collapses that grid column to 0 so the viewport expands to fill the freed space, same as the panel being
hidden on mobile. The button gets the `tgon` class (and is highlighted) while the panel is shown, and is itself hidden below
900 px, since the phone layout already collapses the panel under its own `<details id="engD">` disclosure. "Report a bug /
feedback" captures a screenshot (via `getDisplayMedia`, a picker the user confirms; falls back to just the LED viewport canvas
if denied or unsupported), opens a dialog to draw on it (colour and width pickers, Undo, Clear markup) and add a text
description, then on "Download screenshot & open email" downloads the marked-up image as
`tilesmith-bugreport-<timestamp>.png` and opens a `mailto:tilesmithapp@gmail.com` link pre-filled with the description (a
mailto link cannot attach a file, so the user attaches the downloaded PNG by hand).

**UI font** ("ⓘ Info" → Preferences, at the bottom of the popup): a `<select data-k="font">` choosing `S.font`, one of
`JetBrains Mono` (default), `OpenDyslexic` or `Current` (the original `Barlow,system-ui,sans-serif` stack). Both JetBrains
Mono and OpenDyslexic ship embedded in `index.html` as base64 `@font-face` woff2 data URIs (regular and bold weights, Latin
subset, SIL Open Font License), so no network access is needed to render them. `sync()` sets
`--font-ui` on `:root` to the chosen family and `body{font-family:var(--font-ui)}` picks it up everywhere in the UI; canvas-
drawn text (tile labels, PDF/label exports) is unaffected and stays on Barlow. The choice is stored in `S.font` and saved and
restored like any other setting.

**Output options** (section after Animation Options): first "Take over a display", one row per non-primary display (up to
three: Display 2-4, numbered with the primary display first, then left to right), each with its size in device pixels, a
Canvas drop-down when there are several canvases, and a Take over / Release button. The desktop app lists displays through
Electron's screen API and opens a borderless full-screen window there (frame name tsout:<display id>:<canvas id>); in
Chrome/Edge the Window Management API (getScreenDetails, permission "window-management", button "Find displays") lists
them and a pop-up opens on the display with a one-click full-screen button. Each canvas drives at most one display; the
per-canvas "Send this canvas to a display" menu controls the same outputs. Then the NDI® options and Spout/Syphon options
submenus.

### 3.3 Viewport (centre)

Shows the canvas scaled (zoom V.z, pan V.x/V.y) on a dark background with a drop shadow, a cyan outline around the
canvas, and an amber outline around each wall (solid for the selected wall when there are several, dashed otherwise).
No text labels around the canvas. The viewport is only a preview of the canvas; nothing drawn on the viewport overlay
goes to the output.

- Scroll wheel zooms around the pointer, 0.9x / 1.1x per notch, max 500%. Minimum = min(25%, 80% of the zoom that fits
  the canvas plus every wall in the viewport). At the minimum zoom everything is centred.
- Drag empty space to pan. Drag a wall to move it (unless an editing mode is on).
- Walls snap to canvas edges and other walls' edges within 10 screen px (magenta dashed guides while dragging); after
  dropping, overlapping walls are pushed apart to keep a 2 px gap. Hold Alt to place freely.
- Click a wall to select it. Show entire canvas (the old Reset fit) fits the canvas (margin min(60 px, 10% of the viewport)); Center canvas keeps the
  zoom and centres the canvas; New Project asks, then resets every setting, wall, crew and logo to the start-up defaults
  (S_DEF); the canvas also refits when the window resizes. Undo menu (top bar, "Undo (n) v"): a snapshot of the whole design (all
  settings except images and play state, every wall's keys, the selected wall, crew and logos) is compared after every
  input/change/click and at the end of a wall/marking/wiring drag; if it differs the previous snapshot is pushed as a step
  named after the control ("Columns -> 9", "Add wall", "Moved LED Wall", "Marked half tiles"). Typing in one box within 1.5 s
  is one step. Up to 20 steps; the menu lists them newest first and picking step n restores the state before it (n undos);
  a Redo item appears on top after an undo. Ctrl/Cmd+Z undoes, Ctrl/Cmd+Y or Ctrl/Cmd+Shift+Z redoes (not while typing in a
  text or number box). Selecting a wall, panning/zooming, playing and exporting are not steps. New Project is one step.
- Editing modes (one at a time): manual data wiring, manual power wiring, Mark half tiles, Remove tiles. In these modes
  the cursor is a crosshair over the selected wall and drags edit instead of moving the wall. While Remove tiles or
  Mark half tiles is on, empty spots of the selected wall show a red dashed outline with an X (viewport only).

### 3.4 Engineering data panel (right; a collapsible menu after the settings on phones)

Collapsible "Entire canvas" section then one section per wall, as two-column tables (label, value). Rows in section 9.

### 3.5 Language
The UI is written in English. TR maps each English text to its translations in LIX order (es, pt-BR, de, fr, zh-CN,
ja, ko, it, nl; a shorter row falls back to English for the missing languages); tr() looks texts up with
whitespace collapsed and trAll() translates the page's text (elements marked data-notr are skipped).
Info > Preferences > Language (select[data-lang]) picks English, Español, Português (Brasil), Deutsch, Français,
Italiano, Nederlands, 简体中文, 日本語 or 한국어 (zh-* maps to zh-CN, pt-* to pt-BR). Chinese, Japanese and Korean add the
system CJK fonts after the UI font. PDF and binder exports stay in English. The choice is kept in
localStorage "tilesmith-lang", and the first launch follows navigator.language.

## 4. Data model and saved settings

Global settings live in one object `S`. Per-wall settings (keys marked "per wall") are copied between `S` and the
selected wall object whenever the selection changes, so the UI always edits `S`. State is saved (debounced 400 ms) as
JSON `{sv:23, S:{...}, walls:[...], cur, crew, logo, dvd}`: in localStorage key `tilesmith-state-v1` (web) or
`state.json` in the user data folder (desktop: `%APPDATA%/TileSmith`, `~/Library/Application Support/TileSmith`).
Images are stored as data URLs. On load, values are type-checked and clamped to their limits; walls that use a named
preset get the preset's current figures; legacy half marks are converted to a layout. "Reset saved settings" (Info
dialog) deletes the state and reloads.

### 4.1 Global settings

| Key | Default | Meaning |
|---|---|---|
| `cw` | 1920 | Canvas width in px (16-8192) of the selected canvas. Each canvas is a raster sent over its own NDI / Spout / Syphon source and recorded to its own video. Projects store every canvas in cvs:[{name,cw,ch,cur,walls}] with ac = the selected canvas (its walls are the top-level walls, cvs[ac].walls is null). |
| `ch` | 1080 | Canvas height in px (16-8192). |
| `bc` | #22d3ee | Tile border colour (overlay drawn on every lit tile). |
| `bt` | 3 | Tile border thickness in px (1-8). |
| `tpos` | true | Show tile position arrows on every lit tile (any pattern). |
| `ids` | true | Show tile ID labels "T05 [C5:R1]". |
| `addr` | false | Show each tile's pixel address range label. |
| `mm` | false | Show each tile's size in mm label. |
| `speed` | 1 | Build animation speed multiplier (0.25-5). |
| `dvdOn` | false | DVD screensaver on/off. |
| `dvdSrc` | TileSmith logo | DVD logo source: TileSmith logo \| Text \| Uploaded image. |
| `dvdText` | TILESMITH | Text used when dvdSrc = Text. |
| `dvdArea` | Each LED wall | Bounce inside: Each LED wall (one logo per wall) \| Whole canvas (one logo). |
| `dvdSize` | 20 | Logo height as % of the area's shorter side (5-60). |
| `dvdSpeed` | 1 | Bounce speed multiplier (0.25-3). Base speed = 0.25 x shorter side per second. |
| `dvdCorner` | 10 | Corner hit chance slider 0-100 (100 = about 45% of bounces hit a corner). |
| `dvdTint` | true | Recolour the logo at every bounce. |
| `dvdLoop` | false | Perfect loop mode (motion repeats exactly). |
| `dvdLoopLen` | 30 | Perfect loop length in seconds (4-600). |
| `dvdLoopCorners` | true | Perfect loop includes exactly two corner hits per loop (else none). |
| `rcard` | any | Engineering > LED processor: receiving card family in the tile (any, brompton, novastar, helios, evision). Narrows the processor list; resets to any when the tile does not allow it. |
| `procAll` | false | Engineering > LED processor (UI label "Show incompatible processors"): show every processor instead of only those listed for the selected wall's tile. The currently chosen processor is always listed; if the tile does not list it, an amber warning shows. Compatibility comes from ROE brochure Processing Platform lines (CMP table: Carbon, Carbon MkII, Graphite, Black Pearl BP2V2, Ruby 2.2/2.6, Vanish V5S/V8S MkII, V8T, ST V4ST/V6ST, Black Quartz, Jet, Topaz, Meru, Sierra, Diamond); tiles not in the table are unrestricted; the list follows the selected wall; #procWarn names every wall on any canvas whose tile does not list the chosen processor. Download config file (experimental): NovaStar = zip of NovaLCT .scr per canvas (DSCI header, DVI info, Standard screens of 17-byte cabinet regions, adjust info; 16-bit byte-sum checksums) + wiring CSV/JSON; other brands = wiring CSV/JSON. Canvas output: per-canvas display picker opens a borderless full-screen window (frame name tsout:<display id>:<canvas id>) drawn 1:1 in device pixels. |
| `vIntro` | 5 | Video export: seconds of blank canvas before the build (0-60). |
| `vHold` | 10 | Video export: seconds holding the finished wall (0-120). |
| `vLed` | true | Video export: tick to include the LED build video (blank intro, live build, final hold). |
| `vDvd` | false | Video export: tick to include the DVD logo perfect-loop video (desktop only; needs Bounce a logo and Perfect loop). With both ticked, one Export video click makes two files, LED build first. |
| `vCodec` | HAP (.mov) | Video export format (see Video formats). |
| `hapFmt` | hap | HAP flavour: hap \| hap_alpha \| hap_q. |
| `proc` | None | LED processor model (or None). Gates all data/port features. |
| `fps` | 60 | Processor frame rate in Hz (affects pixels per port). |
| `bpc` | 8 | Processor bit depth (8, 10, 12). |
| `ull` | false | Brompton Ultra Low Latency (halves port capacity). |
| `ppx` | 0 | Pixels per port in use (from spec, editable). |
| `pports` | 1 | Ports per processor / sending card (editable). |
| `ret` | true | Old global Return lines switch (no UI now); only seeds wred for walls in old projects. |
| `showData` | true | Draw data paths on the canvas. |
| `pvolt` | 120 | Mirror of the current wall's circuit voltage (its supply's cv); set by pwMirror, not the user. |
| `pamps` | 20 | Mirror of the current wall's breaker (its supply's cb, capped at the connector rating); set by pwMirror. |
| `derate` | true | Load circuits to 80% (continuous load rule). |
| `showPow` | true | Draw power runs on the canvas. |
| `resSl` | One slice per LED wall | Resolume XML slice mode: One slice per LED wall \| One slice per tile. |
| `loop` | false | Restart the build animation continuously. |
| `loopHold` | 3 | Seconds to pause before restarting (0-600). |
| `ndiName` | TileSmith-LED-Out | NDI source name (default TileSmith-LED-Out). |
| `ndiFps` | 60 | NDI frame rate (see NDI). |
| `ndiIdle` | false | Save CPU: when nothing moves, send about 4 frames per second instead of the full rate. |
| `shName` | TileSmith | Spout sender name (Windows) or Syphon server name (Mac), default TileSmith. Applies the next time it starts. |
| `shFps` | 60 | Spout/Syphon frame rate while NDI is off: 60, 50, 30 or 25 (while NDI runs, its rate is used). |
| `shIdle` | true | Spout/Syphon Save CPU (default on): a still picture is sent about 4 times a second instead of the full rate. |
| `shGpu` | Automatic | Spout graphics card (Windows): Automatic (the high-performance card) or a card name from the list. The receiver must be on the same card. |
| `lblWhat` | Data and power | Label printing: which cables to label: Data and power (default), Data only, Power only. |
| `lblPow` | Cable and circuit labels | Power labels: "Cable and circuit labels" (default), "Circuit labels only", "Cable labels only". |
| `lblSize` | Avery 5163 (10 per US Letter sheet) | Label sheet preset: Avery 5160 (30 per US Letter), Avery 5163 (10 per US Letter), Avery L7160 (21 per A4), Label roll 62 x 29 mm, or Custom label roll. |
| `lblLayout` | Two identical panels | Wrap layout: Two identical panels (default), Flag fold-over (second panel rotated 180 degrees), Text in the middle, colour on the ends. |
| `lblFlag` | Big end blocks | Colour flag style: Big end blocks (default), Top and bottom bars, Big corner squares. |
| `lblWall` | Wall-shade block + name (several walls only) | Wall mark: Wall-shade block + name (several walls only, default), Always show wall mark, Wall tint + block (light tint of the wall shade as label background). |
| `lblW` | 62 | Custom roll label width in mm (20-300). |
| `lblH` | 29 | Custom roll label height in mm (10-300). |
| `lblCopies` | 1 | Copies printed of each cable end (1-4). |
| `lblColor` | true | Colour the labels: data labels are completely green (primary) or red (return); power labels carry a flag in the wall's Tile-shade colour; off = plain labels, no flags or wall marks. |
| `lblJump` | false | Also print labels for the tile-to-tile links (data and power jumpers). |
| `lblKeep` | true | Sheets: keep the two ends of one cable in the same row (pad with a blank cell). |
| `lblSkip` | 1 | First label position to use on a sheet (skips used labels). |
| `hat` | #ffcc00 | Technician hard hat colour. |
| `vest` | #b6ff00 | Technician vest colour. |
| `tstyle` | Classic | Technician character style: Classic \| Hand-drawn (Rocketbox workers rendered with three.js and an ink shader; files in app/crew, loaded only when picked; Classic is drawn without WebGL) \| Backlit (dark Canvas 2D figure with a rim of wall light and reflective tape). |
| `logo` | TILESMITH | Vest logo text. |
| `cd` | true | Show crew details editor and name tags. |
| `play` | true | Build animation playing (not saved). |
| `addonAsk` | true | At start (desktop app), show a note when the NDI® Runtime or ffmpeg is missing, with Set up (opens Info > Add-ons), Not now and Don’t ask again (sets this to false). |
| `bShow` |  | Export binder / pull sheet: show name, printed on every page title and used in the file name. |
| `bVenue` |  | Export binder: venue, printed under the title. |
| `bDate` |  | Export binder: load-in date (free text), printed under the title. |
| `spT` | 5 | Pull sheet spares: extra tiles as % of the tiles in use (0-100, rounded up). |
| `spC` | 1 | Pull sheet spares: extra cables per cable length (0-20). |
| `cidFmt` | Processor : port : tile (1:P2:07) | Cabinet ID style: "Processor : port : tile (1:P2:07)" or "Port - tile (P12-07, as on the cable labels)". |
| `cidStk` | false | Cabinet ID sheet: add one sticker per tile on the label sheet. |
| `cabOn` | false | Engineering > Cable lengths ticked: work out every data and power run and list the cables to take (needs a processor or power distribution). |
| `cunit` | m | Cable length units: m \| ft. Changing it converts the distances, limits and owned lengths. |
| `cslack` | 10 | Slack added to every run in % (0-100). |
| `clenD` | 1, 3, 5, 10, 15, 20, 30, 50 | Data cable lengths you own, comma separated, in cunit. |
| `clenP` | 1, 3, 5, 10, 15, 25 | Power cable lengths you own, comma separated, in cunit. |
| `fibLim` | 90 | Copper limit in cunit (default 90 m / 295 ft); Auto walls with a longer data run go over fibre. |
| `fibBox` | 10 | Ports per fibre breakout box at the wall: 4 \| 10 \| 16. |
| `fibNat` | false | Processor has fibre outputs, so no converter is needed at the processor. |
| `fibTr` | opticalCON QUAD | Fibre trunk type: opticalCON DUO (1 breakout box per trunk) \| opticalCON QUAD (2 boxes per trunk). |
| `fibLen` | 50, 100, 150, 300 | Fibre trunk lengths you own, comma separated, in cunit. |
| `fibTail` | 1, 3, 5, 10 | Copper tail lengths you own (breakout box to the first tile), comma separated, in cunit. |
| `lyrFmt` | svg | Export layers format last used: svg \| psd. |
| `lyrOff` | [] | Layers unticked in the Export layers dialog (bg, pat, grid, lab, data, pow). |
| `lyrGrp` | A | Export layers grouping: A by kind (default) \| B folder per wall \| C folder per kind with a layer per wall. |
| `zones` | [] | Zones: [{id, name, c (colour)}] in pull sheet order, at most 20 (see Zones). |
| `zHide` | [] | Zone ids whose walls are hidden in the viewport only. |
| `zProc` | 0 | Zone of the processor (0 = no zone). |
| `pf` | 1 | Power factor 0.5-1 (default 1). Usable watts per circuit = V x A x (0.8) x PF; amps everywhere = W / (V x PF). |
| `pload` | Max (spec) | Design load for distro and leg totals: Max (spec) \| Typical (% of max) \| Measured (W per tile). Circuits are always checked at max. |
| `ptyp` | 40 | Typical design load in % of each tile's max watts (1-100, default 40). |
| `pmeas` | 0 | Measured design load in watts per tile (0-5000; 0 = use max; never above a tile's max). |
| `dists` | [] | Distros: [{id, name, sys (120/208 V 3-phase wye \| 127/220 V 3-phase wye \| 230/400 V 3-phase wye \| 120/240 V split phase \| Single phase), amps per leg, soca, l2130, l1430, edison (output counts), map (Socapex leg map, default ABCABC), type (distro \| house), cv (circuit voltage), cb (circuit breaker A), outl (house: outlets per house circuit), hb (house breaker A)}], at most 12. Power is on while there is at least one. |
| `pcab` | {} | Power patch: "canvas index:cable number" -> {d: distro id ('' = left unpatched on purpose), o: output key (soca1, l21302, edison3 ...), r: leg rotation 0-2}. |
| `pshare` | [] | Shared circuits (2fer / 3fer): [canvas index, [wall, run], [wall, run](, [wall, run])]. |
| `autoBal` | false | Rebalance every distro after every wiring change. |
| `phaseView` | true | Colour power runs by phase (A white, B amber, C blue) and label them "1-1 A" when distros exist. |
| `trayOpen` | true | Power tray under the viewport expanded. |
| `pwv` | 2 | Power settings version: 2 = supplies own the circuit voltage and breaker. Older projects (no pwv) are migrated by pwMigrate. |
| `gOn` | false | Limit the plan to the gear on hand (gProc, gTr, gBox): walls step down from their method, in priority order, with the reason shown. |
| `gProc` | 2 | Processors on hand (0-50). |
| `gTr` | 2 | Fibre trunks on hand (0-50). |
| `gBox` | 2 | Fibre breakout boxes on hand (0-50). |
| `rlink` | true | Backup processors need a link / sync cable (added to the pull sheet and drawn in the signal path). |
| `rigOn` | false | Engineering > Rigging ticked: work out bumpers, truss, ground bases and hoist loads for every wall and add them to the pull sheet. Loads assume the weight is shared evenly (planning figures only). |
| `rparts` | {} | Rigging parts rules per tile model: {model: [[name, qty, per (tile \| column \| row \| wall \| hoist point), kg]]}, at most 40 rows each. |
| `glOn` | false | Tile faults running (Start tile faults): the faulty tiles show their fault on the canvas until Fix glitch sends a technician to swap them. |
| `glType` | Dead tile | Fault shown: one of the 12 fault types (Dead tile, Flicker, Colour channel out, Stuck pixels, Data chain break, Module out, Scrambled tile, Frozen tile, Calibration mismatch, Scan line fault, Noise and sparkle, Power circuit tripped) or Random mix (each tile its own fault). |
| `glPick` | Tiles I pick | Faulty tiles: Tiles I pick (click tiles in the viewport) \| Random. |
| `glN` | 3 | How many random faulty tiles (1-200). |
| `font` | JetBrains Mono | UI font: JetBrains Mono (default), OpenDyslexic, or Current (the original Barlow-based stack). Set from Preferences in the Info popup; applies to the app chrome via --font-ui, not to canvas-drawn text. |
| `hideEng` | false | Hide the Engineering data panel entirely. Toggled from the Hide / Show Engineering Data button in the top bar (desktop only). |
| `updAuto` | true | Check for updates when TileSmith starts (desktop and phone apps): at most once a day, asks the GitHub API for the latest release and, when it is newer than APP_VERSION, shows a note with Download (the file for this platform), Release notes and Not now. |

### 4.2 Per-wall settings

| Key | Default | Meaning |
|---|---|---|
| `half` | [] | Legacy half-tile marks from v3.2 previews ([col,row,side]); converted to "lay" on load. |
| `gone` | [] | Removed tiles on a plain grid: list of [col,row]. |
| `lay` | {} | Half-tile layout: {} for a plain grid, or {s: split "h"\|"w", uc/ur: unit grid size when last edited, p: [[u,v,unitsWide,unitsTall],...]}. |
| `gx` | 0 | Wall key: how far (px) the top-left of the wall's real tiles sits right of the full tile grid. Set by the app, not the user; ox/oy are the canvas position of those tiles. |
| `gy` | 0 | Wall key: like gx, downwards (a converted top row makes it half a tile). |
| `name` | LED Wall | Wall name. |
| `ox` | 0 | Wall X offset on the canvas in px (-20000..20000). |
| `oy` | 0 | Wall Y offset on the canvas in px. |
| `cols` | 6 | Columns of tiles (1-64). |
| `rows` | 4 | Rows of tiles (1-64). |
| `preset` | Unilumin UpadIV 2.6 | Tile model preset name ("Custom" once any tile field is edited). The UI picks Brand first, then a model of that brand; user presets live in localStorage "tilesmith-tiles-v1" ({name:[wmm,hmm,tw,th,pitch,kg,wmax,dmm]}) and are copied into the project file as "ut" for every preset a wall uses (on open a differing same-name tile is kept as "Name (from project)"); PINFO holds extra spec-sheet facts per model (receiving card, brightness, refresh, IP, curving, hanging height with an over-limit warning); models in PEST have estimated figures flagged as MISSING DATA in Engineering and the PDF. |
| `rcfg` |  | Per wall: id (SHA-256 hex) of the NovaStar receiving card file (.rcfg/.rcfgx) the wall uses, or empty. Files live in IndexedDB tilesmith-rcfg/files {id,name,ext,size,data,models[],vendor,revision,added}; saved projects carry the used ones as rc:{id:{name,ext,vendor,revision,models,added,data:base64}} (autosave does not), opening a project merges them into the library; Download config file adds them under receiving-card-files/ with a README of which walls use each. |
| `tw` | 192 | Tile width in px. |
| `th` | 192 | Tile height in px. |
| `wmm` | 500 | Tile width in mm. |
| `hmm` | 500 | Tile height in mm. |
| `dmm` | 70 | Tile depth in mm. |
| `kg` | 6.3 | Tile weight in kg. |
| `wmax` | 120 | Tile max power in W. |
| `pitch` | 2.6 | Pixel pitch in mm. |
| `pat` | tileshade | Test pattern (see Patterns). |
| `pfit` | Stretch to wall | Image fit for image patterns (see Image fit). |
| `pdir` | none | Scroll direction: none \| diagonal ↘ \| diagonal ↗ \| horizontal → \| vertical ↓. |
| `pspd` | 1 | Scroll speed (0-3). |
| `shadeC` | #3f8080 | Tile-shade colour (tileshade, tileshade-clean). |
| `patImg` | null | Uploaded custom pattern image (kept up to 8192 px). |
| `boxMode` | Nothing | Branded pattern centre box: Nothing \| Text \| Logo. |
| `boxText` |  | Centre box text. |
| `boxCol` | #ffffff | Centre box text colour. |
| `boxImg` | null | Centre box logo image. |
| `corner` | Top-left | Build start corner (Tech starts at): Top-left \| Top-right \| Bottom-left \| Bottom-right. |
| `dir` | Horizontal | Tile placement order: Horizontal (row at a time) \| Vertical. |
| `wmode` | None | Data wiring pattern: None \| Snake \| Linear \| Manual. |
| `wcorner` | Top-left | Data wiring start corner. |
| `wdir` | Horizontal | Data wiring direction: Horizontal \| Vertical. |
| `wfill` | Fewest ports | Data wiring preference, how tiles are shared between ports: Fewest ports \| Whole rows or columns \| One continuous path \| Horizontal \| Vertical (see Wiring). |
| `wman` | [] | Manual data chains: list of ports, each a list of tiles ([col,row] on a plain grid, "u,v" keys on a half-tile layout). |
| `pmode` | None | Power wiring pattern: None \| Snake \| Linear \| Manual. |
| `pcorner` | Top-left | Power wiring start corner. |
| `pwdir` | Horizontal | Power wiring direction. |
| `pfill` | Fewest circuits | Power wiring preference (UI label "Wiring preference"): Fewest circuits \| Whole rows or columns \| One continuous path \| Horizontal \| Vertical (see Power). |
| `plink` | 0 | Power link limit: max tiles per circuit (0 = none). |
| `pman` | [] | Manual power chains (same format as wman). |
| `bmode` | Ground stack | Wall key: how the wall goes up and how it is rigged: Ground stack (from the floor up) \| Flown from motors (bumpers on hoists, top row first) \| Flown from truss (bumpers on slings from a truss). |
| `cdD` | 25 | Wall key: distance from the processor to the wall, in cunit (0-3000). |
| `cdP` | 15 | Wall key: distance from the distro to the wall, in cunit (0-3000). |
| `cin` | Bottom left | Wall key: where the cables arrive at the wall: Bottom left \| Bottom centre \| Bottom right \| Top left \| Top centre \| Top right. Each run = distance + climb along the wall to its first tile (no diagonals) + cslack, rounded up to a length you own. |
| `wfib` | Auto | Wall key: data to this wall: Auto (fibre when the longest copper data run is over fibLim) \| Fibre \| Copper. |
| `zone` | 0 | Wall key: the wall's zone id (0 = no zone). |
| `pown` | true | Per wall: start this wall on its own cable (default on), so walls too far apart never share a Socapex; unused circuits on it are spare. |
| `pcabs` | 0 | Per wall: cables run to this wall (0 = as many as it needs). Circuits past them are marked over capacity. |
| `pmk` | 0 | Per wall, internal: the power link limit TileSmith last set from the maker data (PWR), so a limit the user lowered is kept. |
| `pfeed` |  | Wall key: id of the supply (S.dists) that feeds the wall ('' = the first supply). |
| `pdt` | Socapex (6 circuits per cable) | Wall key: the wall's cable, "Socapex (6 circuits per cable)" (default), "L14-30 (2 circuits per cable)" "L21-30 (3 circuits per cable)" or "powerCON to Edison (1 circuit per cable)"; only types its supply has outputs for. |
| `wred` | Loop | Wall key: redundancy for this wall: Full (backup processor, own route) \| Backup processor (same port numbers) \| Loop (spare ports, same processor) \| Spare processor (on the truck) \| None. Old projects get Loop, or None when ret was off. |
| `wpri` | 1 | Wall key: redundancy priority (1-99, 1 = covered first when gear is short). |
| `rbw` | 2 | Wall key: bumper width in tiles (1-4). |
| `rbkg` | 9 | Wall key: weight of one bumper in kg (0-500). |
| `rpts` | 2 | Wall key: pickups per bumper (1 or 2). |
| `rwll` | 500 | Wall key: hoist rating in kg (1-20000); hoist points over it are flagged. |
| `tsec` | 1, 2, 3 | Wall key: truss section lengths owned in m, comma separated; the truss (wall width + tex each side) is made from the largest that fit first. |
| `tkgm` | 8 | Wall key: truss weight in kg per m (0-200). |
| `thn` | 3 | Wall key: hoists on the truss (1-50). |
| `tex` | 0.5 | Wall key: extra truss each side of the wall in m (0-20). |
| `rgbw` | 2 | Wall key: ground base width in tiles (1-4), for Ground stack. |
| `rgkg` | 14 | Wall key: weight of one ground base in kg (0-500). |
| `glk` | [] | Wall key: faulty tiles of the wall: [[tile key, fault index]]. |

New wall ("Add wall"): copy of the selected wall's settings but 4x3, build from top-left horizontal, pattern = first of
['tileshade', 'SMPTEbars', 'sweep', 'circles', 'rgbramp', 'ramp'] not used yet, tile-shade colour from ['#3f8080', '#448040', '#7a4a9e', '#9e5a3a', '#3a5a9e', '#8a7a2a'] by index, name "Wall N". It is placed to the right of the
rightmost wall (2 px gap) if it fits on the canvas, else below the lowest wall, else offset 40 px. "Duplicate" copies
the wall (including manual wiring) and names it "... copy". "Remove" deletes the selected wall (at least one remains).
Canvas presets: 1080p Full HD (1920x1080), 4K UHD (3840x2160), 2K DCI (2048x1080), 4K DCI (4096x2160), 720p HD (1280x720), 32:9 Banner (3840x1080). "Fit canvas to walls" moves walls so none is left/above 0 and sets the canvas to their bounding
box (clamped 16-8192). Wall position buttons: Top-Left (0,0), Center Both, Top-Center, Bottom-Left, Bottom-Center.
Quick sizes: 4x3, 6x4, 8x5, 10x6, 16x9.

## 5. Tile models (presets)

Picking a preset fills tw, th, wmm, hmm, pitch, kg, wmax, dmm. Editing any of those switches the preset to "Custom".
Density = 1e6 / (pitch^2) px/m^2; Typical power = 40% of max. Brand menu (PBR): ROE, Absen, Unilumin, INFiLED, AOTO,
Gloshine, YES TECH, Owl Vision, Custom. The Model menu shows only the picked brand; models listed in TSER (key -> series name)
sit in one optgroup per series, the rest come first ungrouped. "Find a tile" (#tFind, input type=search with datalist #tFindL)
lists every preset and own tile with "series · pitch mm · W×H"; picking one exactly (change event, or a datalist pick in the
input event) sets the preset, applies it, and clears the box; partial text does nothing. Catalog round 1 (2026-11-14) added
209 models (INFiLED 167, Gloshine 17, AOTO 14, Absen 11) from the makers' own spec pages / sheets; each has PINFO.src (from
TSRC) shown as a "Source" row in Engineering > LED Tiles and the PDF; where a sheet gives only W/m^2, max W = W/m^2 x panel area.
INFiLED depth comes from each series brochure. The list is grouped by manufacturer (Custom last); ROE is split into one group per series (ROE Amber, ROE Black Marble, ... ROE Vanish Acoustics) in the order of the ROES array. YES TECH max watts = the higher W/m^2 figure on the spec sheet x cabinet area, rounded
up. ROE figures come from the cabinet pages on roevisual.com (per panel, as printed). 23 ROE models have a half panel (HALF table, 'h' = two halves stacked make the full tile).

| Preset | W mm | H mm | px W | px H | Pitch mm | kg | Max W | Depth mm |
|---|---|---|---|---|---|---|---|---|
| ROE Amber AB1.5 | 600 | 337.5 | 384 | 216 | 1.5625 | 8.5 | 180 | 55 |
| ROE Amber AB1.8 | 600 | 337.5 | 320 | 180 | 1.875 | 8.5 | 170 | 55 |
| ROE Black Marble BM2 Matte | 609.6 | 609.6 | 216 | 216 | 2.82 | 18.6 | 310 | 133 |
| ROE Black Marble BM2V2-PC Matte (Black LED) | 609.6 | 609.6 | 216 | 216 | 2.82 | 18.6 | 310 | 133 |
| ROE Black Marble BM2V2-PC Matte (White LED) | 609.6 | 609.6 | 216 | 216 | 2.82 | 18.6 | 310 | 133 |
| ROE Black Marble BM4 Glass | 609.6 | 609.6 | 128 | 128 | 4.76 | 23.4 | 290 | 142 |
| ROE Black Marble BM4 Matte | 609.6 | 609.6 | 128 | 128 | 4.76 | 17.5 | 290 | 135 |
| ROE Black Marble BM4 Mirror | 609.6 | 609.6 | 128 | 128 | 4.76 | 23.4 | 290 | 142 |
| ROE Black Marble BM5 PC Matte | 600 | 600 | 104 | 104 | 5.7692 | 13.5 | 270 | 103 |
| ROE Black Marble BM5 Glass | 600 | 600 | 104 | 104 | 5.7692 | 18.3 | 270 | 110 |
| ROE Black Marble BM2i Matte (interactive floor) | 609.6 | 609.6 | 216 | 216 | 2.82 | 18.6 | 310 | 133 |
| ROE Black Marble BM4i (interactive floor) | 609.6 | 609.6 | 128 | 128 | 4.76 | 17.5 | 290 | 135 |
| ROE Black Pearl BP2V2 | 500 | 500 | 176 | 176 | 2.84 | 9.35 | 190 | 90 |
| ROE Black Quartz BQ3.9 | 500 | 1000 | 128 | 256 | 3.9 | 22 | 360 | 82.62 |
| ROE Black Quartz BQ3.9 Half | 500 | 500 | 128 | 128 | 3.9 | 9.8 | 190 | 82.62 |
| ROE Black Quartz BQ4.6 | 500 | 1000 | 108 | 216 | 4.6 | 22 | 370 | 82.62 |
| ROE Black Quartz BQ4.6 Half | 500 | 500 | 108 | 108 | 4.6 | 9.8 | 190 | 82.62 |
| ROE Black Quartz BQ6.2 | 500 | 1000 | 80 | 160 | 6.25 | 22 | 450 | 82.62 |
| ROE Black Quartz BQ6.2 Half | 500 | 500 | 80 | 80 | 6.25 | 9.8 | 230 | 82.62 |
| ROE Carbon CB3 | 600 | 1200 | 160 | 320 | 3.75 | 13.2 | 540 | 77 |
| ROE Carbon CB3 Half | 600 | 600 | 160 | 160 | 3.75 | 7.5 | 260 | 77 |
| ROE Carbon CB5 | 600 | 1200 | 104 | 208 | 5.77 | 13.85 | 500 | 77 |
| ROE Carbon CB5 Half | 600 | 600 | 104 | 104 | 5.77 | 7.95 | 250 | 77 |
| ROE Carbon CB8 | 600 | 1200 | 72 | 144 | 8.33 | 12.68 | 430 | 72 |
| ROE Carbon CB8 Half | 600 | 600 | 72 | 72 | 8.33 | 7.05 | 220 | 72 |
| ROE Carbon CB8-Transparent | 600 | 1200 | 72 | 144 | 8.33 | 10.9 | 430 | 70 |
| ROE Carbon CB8-Transparent Half | 600 | 600 | 72 | 72 | 8.33 | 6 | 220 | 70 |
| ROE Carbon MkII CB3 | 600 | 1200 | 160 | 320 | 3.75 | 14.4 | 600 | 79 |
| ROE Carbon MkII CB3 Half | 600 | 600 | 160 | 160 | 3.75 | 7.8 | 290 | 79 |
| ROE Carbon MkII CB5 | 600 | 1200 | 104 | 208 | 5.77 | 13.6 | 480 | 79 |
| ROE Carbon MkII CB5 Half | 600 | 600 | 104 | 104 | 5.77 | 7.2 | 250 | 79 |
| ROE Carbon MkII CB8 | 600 | 1200 | 72 | 144 | 8.33 | 11 | 530 | 79 |
| ROE Carbon MkII CB8 Half | 600 | 600 | 72 | 72 | 8.33 | 6 | 260 | 79 |
| ROE Carbon Full Spectrum CB5 MkII RGBCA | 600 | 1200 | 104 | 208 | 5.77 | 15.5 | 300 | 80 |
| ROE Carbon Full Spectrum CB5 MkII RGBW | 600 | 1200 | 104 | 208 | 5.77 | 17.5 | 750 | 80 |
| ROE Coral S0.9 | 600 | 337.5 | 640 | 360 | 0.9375 | 5.4 | 60 | 29.2 |
| ROE Coral S1.2 | 600 | 337.5 | 480 | 270 | 1.25 | 5.4 | 60 | 29.2 |
| ROE Coral S1.5 | 600 | 337.5 | 384 | 216 | 1.5625 | 5.4 | 60 | 29.2 |
| ROE Denali DL0.7 | 600 | 337.5 | 768 | 432 | 0.78125 | 5.5 | 70 | 29.2 |
| ROE Denali DL0.9 | 600 | 337.5 | 640 | 360 | 0.9375 | 5.5 | 95 | 29.2 |
| ROE Denali DL1.2 | 600 | 337.5 | 480 | 270 | 1.25 | 5.5 | 100 | 29.2 |
| ROE Diamond DM2.6 | 500 | 500 | 192 | 192 | 2.6 | 5.76 | 180 | 80 |
| ROE Diamond DM3.9 | 500 | 500 | 128 | 128 | 3.906 | 5.76 | 150 | 80 |
| ROE Graphite GP1.9 (4 in 1) | 500 | 1000 | 256 | 512 | 1.953 | 9.32 | 250 | 80 |
| ROE Graphite GP1.9 (4 in 1) Half | 500 | 500 | 256 | 256 | 1.953 | 5.51 | 125 | 80 |
| ROE Graphite GP2.6 (4 in 1) | 500 | 1000 | 192 | 384 | 2.604 | 8.6 | 250 | 80 |
| ROE Graphite GP2.6 (4 in 1) Half | 500 | 500 | 192 | 192 | 2.604 | 5.1 | 125 | 80 |
| ROE Graphite GP2.6 | 500 | 1000 | 192 | 384 | 2.604 | 9 | 320 | 80 |
| ROE Graphite GP2.6 Half | 500 | 500 | 192 | 192 | 2.604 | 5.2 | 160 | 80 |
| ROE Graphite GP3.1 | 500 | 1000 | 160 | 320 | 3.125 | 9 | 320 | 80 |
| ROE Graphite GP3.1 Half | 500 | 500 | 160 | 160 | 3.125 | 5.2 | 160 | 80 |
| ROE Graphite GP3.9 | 500 | 1000 | 128 | 256 | 3.91 | 9 | 320 | 80 |
| ROE Graphite GP3.9 Half | 500 | 500 | 128 | 128 | 3.91 | 5.2 | 160 | 80 |
| ROE Jasper JA2.6 | 500 | 1000 | 192 | 384 | 2.604 | 14.15 | 340 | 60 |
| ROE Jasper JA2.6 Half | 500 | 500 | 192 | 192 | 2.604 | 7.5 | 190 | 60 |
| ROE Jasper JA3.9 | 500 | 1000 | 128 | 256 | 3.906 | 14.15 | 340 | 60 |
| ROE Jasper JA3.9 Half | 500 | 500 | 128 | 128 | 3.906 | 7.5 | 160 | 60 |
| ROE Jet JT1.9 (GOB) | 500 | 500 | 256 | 256 | 1.95 | 6.1 | 140 | 86 |
| ROE Jet JT2.2 | 500 | 1000 | 224 | 448 | 2.23 | 10.8 | 280 | 86 |
| ROE Jet JT2.2 Half | 500 | 500 | 224 | 224 | 2.23 | 6 | 140 | 86 |
| ROE Jet JT2.6 | 500 | 1000 | 192 | 384 | 2.604 | 10.3 | 280 | 86 |
| ROE Jet JT2.6 Half | 500 | 500 | 192 | 192 | 2.604 | 5.8 | 140 | 86 |
| ROE Jet JT3.1 | 500 | 1000 | 160 | 320 | 3.125 | 10.3 | 280 | 86 |
| ROE Jet JT3.1 Half | 500 | 500 | 160 | 160 | 3.125 | 5.8 | 140 | 86 |
| ROE Jet JT3.9 | 500 | 1000 | 128 | 256 | 3.91 | 10.3 | 290 | 86 |
| ROE Jet JT3.9 Half | 500 | 500 | 128 | 128 | 3.91 | 5.8 | 145 | 86 |
| ROE Meru MR1.9 | 500 | 1000 | 256 | 512 | 1.9 | 14.8 | 300 | 48 |
| ROE Meru MR1.9 Half | 500 | 500 | 256 | 256 | 1.9 | 7.4 | 150 | 48 |
| ROE Meru MR2.6 | 500 | 1000 | 192 | 384 | 2.6 | 14.8 | 230 | 48 |
| ROE Meru MR2.6 Half | 500 | 500 | 192 | 192 | 2.6 | 7.4 | 115 | 48 |
| ROE Obsidian OB2.6 | 500 | 500 | 192 | 192 | 2.6 | 5.4 | 220 | 74.6 |
| ROE Ruby RB2.3 | 500 | 500 | 216 | 216 | 2.31 | 8.16 | 180 | 73 |
| ROE Ruby RB1.2 | 500 | 500 | 400 | 400 | 1.25 | 8.24 | 210 | 73 |
| ROE Ruby RB1.2F | 500 | 500 | 400 | 400 | 1.25 | 8.54 | 140 | 73 |
| ROE Ruby RB1.5F | 500 | 500 | 320 | 320 | 1.56 | 8.16 | 140 | 73 |
| ROE Ruby RB-C1.5F | 500 | 500 | 320 | 320 | 1.56 | 8.58 | 140 | 108 |
| ROE Ruby RB1.9BV2 | 500 | 500 | 256 | 256 | 1.95 | 8.46 | 160 | 73 |
| ROE Ruby RB-C1.9BV2 | 500 | 500 | 256 | 256 | 1.95 | 8.4 | 160 | 108 |
| ROE Ruby RB1.9F | 500 | 500 | 256 | 256 | 1.95 | 8.3 | 140 | 73 |
| ROE Ruby RB-C1.9F | 500 | 500 | 256 | 256 | 1.95 | 8.5 | 140 | 108 |
| ROE Ruby RB2.2 | 500 | 500 | 224 | 224 | 2.23 | 8.24 | 160 | 73 |
| ROE Ruby RB-C2.2F | 500 | 500 | 224 | 224 | 2.23 | 8.4 | 190 | 108 |
| ROE Ruby RB2.2F (Deepsky) | 500 | 500 | 224 | 224 | 2.23 | 8.92 | 210 | 73 |
| ROE Ruby RB-B2.2F | 500 | 500 | 224 | 224 | 2.23 | 8.9 | 190 | 72.19 |
| ROE Ruby RB2.6 | 500 | 500 | 192 | 192 | 2.604 | 8.5 | 160 | 73 |
| ROE Ruby RB2.6F | 500 | 500 | 192 | 192 | 2.604 | 8.02 | 215 | 73 |
| ROE Ruby RB-C2.6 | 500 | 500 | 192 | 192 | 2.604 | 8.3 | 160 | 108 |
| ROE Ruby RB-C2.6F | 500 | 500 | 192 | 192 | 2.604 | 8.3 | 210 | 108 |
| ROE Ruby RB-B2.6 | 500 | 500 | 192 | 192 | 2.604 | 9.08 | 160 | 72.19 |
| ROE Ruby RB-B2.6F | 500 | 500 | 192 | 192 | 2.604 | 8.7 | 215 | 72.19 |
| ROE Sierra SR1.2 | 600 | 337.5 | 480 | 270 | 1.25 | 5.7 | 100 | 29.9 |
| ROE Sierra SR1.5 | 600 | 337.5 | 384 | 216 | 1.56 | 5.7 | 80 | 29.9 |
| ROE Sierra SR1.5F | 600 | 337.5 | 384 | 216 | 1.56 | 5.7 | 70 | 29.9 |
| ROE Topaz TP1.5 | 500 | 500 | 320 | 320 | 1.56 | 8.16 | 160 | 73 |
| ROE Topaz TP-C1.5 | 500 | 500 | 320 | 320 | 1.56 | 8.5 | 160 | 108 |
| ROE Topaz TP1.9 | 500 | 500 | 256 | 256 | 1.95 | 8.3 | 140 | 73 |
| ROE Topaz TP-C1.9 | 500 | 500 | 256 | 256 | 1.95 | 8.5 | 140 | 108 |
| ROE Topaz TP-B1.9 | 500 | 500 | 256 | 256 | 1.95 | 8.9 | 140 | 72.19 |
| ROE Topaz TP2.2 | 500 | 500 | 224 | 224 | 2.23 | 8 | 160 | 73 |
| ROE Topaz TP-C2.2 | 500 | 500 | 224 | 224 | 2.23 | 8.4 | 160 | 108 |
| ROE Topaz TP-B2.2 | 500 | 500 | 224 | 224 | 2.23 | 9.08 | 160 | 72.19 |
| ROE Topaz TP2.6 | 500 | 500 | 192 | 192 | 2.604 | 8 | 140 | 73 |
| ROE Topaz TP-C2.6 | 500 | 500 | 192 | 192 | 2.604 | 8.3 | 140 | 108 |
| ROE Topaz TP-B2.6 | 500 | 500 | 192 | 192 | 2.604 | 9.08 | 140 | 72.19 |
| ROE Vanish V5S MkII | 1000 | 1000 | 176 | 176 | 5.6 | 10.9 | 420 | 67 |
| ROE Vanish V8S MkII (White LED) | 1000 | 1000 | 112 | 112 | 8.9 | 9.6 | 460 | 67 |
| ROE Vanish V8T | 1000 | 1000 | 112 | 112 | 8.9 | 18.2 | 480 | 95 |
| ROE Vanish V8T-H | 1000 | 500 | 112 | 56 | 8.9 | 11.22 | 260 | 95 |
| ROE Vanish V8T-V | 500 | 1000 | 56 | 112 | 8.9 | 14.56 | 260 | 95 |
| ROE Vanish ST V3ST | 1000 | 1000 | 256 | 256 | 3.9 | 27.5 | 700 | 116 |
| ROE Vanish ST V3ST-H | 1000 | 500 | 256 | 128 | 3.9 | 16.5 | 350 | 116 |
| ROE Vanish ST V3ST-V | 500 | 1000 | 128 | 256 | 3.9 | 19 | 350 | 103 |
| ROE Vanish ST V3ST-Q | 500 | 500 | 128 | 128 | 3.9 | 14.5 | 180 | 108 |
| ROE Vanish ST V3ST-X | 500 | 1000 | 128 | 256 | 3.9 | 22 | 350 | 107 |
| ROE Vanish ST V3ST-Q-X | 500 | 500 | 128 | 128 | 3.9 | 13.5 | 180 | 107 |
| ROE Vanish ST V4ST | 1000 | 1000 | 216 | 216 | 4.6 | 34.5 | 700 | 116 |
| ROE Vanish ST V4ST-H | 1000 | 500 | 216 | 108 | 4.6 | 21.5 | 350 | 116 |
| ROE Vanish ST V4ST-V | 500 | 1000 | 108 | 216 | 4.6 | 22.5 | 350 | 103 |
| ROE Vanish ST V4ST-Q | 500 | 500 | 108 | 108 | 4.6 | 14.5 | 180 | 108 |
| ROE Vanish ST V6ST | 1000 | 1000 | 144 | 144 | 6.94 | 34.3 | 700 | 116 |
| ROE Vanish ST V6ST-H | 1000 | 500 | 144 | 72 | 6.94 | 21.2 | 350 | 116 |
| ROE Vanish ST V6ST-V | 500 | 1000 | 72 | 144 | 6.94 | 22.2 | 350 | 103 |
| ROE Vanish ST V6ST-Q | 500 | 500 | 72 | 72 | 6.94 | 14.3 | 180 | 108 |
| ROE Vanish Air VAI (indoor) | 1000 | 1000 | 144 | 144 | 6.94 | 8.6 | 650 | 79 |
| ROE Vanish Air VAO (outdoor) | 1000 | 1000 | 144 | 144 | 6.94 | 11.8 | 650 | 79 |
| ROE Vanish Acoustics VC2.6 | 500 | 1000 | 192 | 384 | 2.604 | 9.26 | 210 | 85.6 |
| Absen Polaris PL2.5 Pro | 500 | 500 | 200 | 200 | 2.5 | 9.6 | 128 | 87 |
| Unilumin UpadIV 2.6 | 500 | 500 | 192 | 192 | 2.6 | 6.3 | 120 | 70 |
| INFiLED Deep Black DB2.6 | 500 | 500 | 192 | 192 | 2.6 | 8 | 150 | 75 |
| YES TECH MG10 1.9 | 500 | 500 | 256 | 256 | 1.95 | 6.6 | 113 | 71 |
| YES TECH MG10 1.9 (1000-1200 nit) | 500 | 500 | 256 | 256 | 1.95 | 6.6 | 140 | 71 |
| YES TECH MG10 2.6 | 500 | 500 | 192 | 192 | 2.6 | 6.6 | 113 | 71 |
| YES TECH MG10 2.6 (1000-1200 nit) | 500 | 500 | 192 | 192 | 2.6 | 6.6 | 140 | 71 |
| YES TECH MG9 2.9 | 500 | 500 | 168 | 168 | 2.98 | 6.3 | 175 | 71 |
| YES TECH MG9 3.9 | 500 | 500 | 128 | 128 | 3.91 | 6 | 175 | 71 |
| YES TECH MU 1.9 | 500 | 500 | 256 | 256 | 1.95 | 7.6 | 163 | 73 |
| YES TECH MU 2.6 | 500 | 500 | 192 | 192 | 2.6 | 7.6 | 113 | 73 |
| YES TECH MU 2.6 500×1000 | 500 | 1000 | 192 | 384 | 2.6 | 12.6 | 225 | 73 |
| YES TECH MU 3.9 | 500 | 500 | 128 | 128 | 3.91 | 7.6 | 105 | 73 |
| YES TECH MU 3.9 500×1000 | 500 | 1000 | 128 | 256 | 3.91 | 12.6 | 210 | 73 |
| YES TECH MU 4.8 | 500 | 500 | 104 | 104 | 4.81 | 7.6 | 105 | 73 |
| YES TECH MU 4.8 500×1000 | 500 | 1000 | 104 | 208 | 4.81 | 12.6 | 210 | 73 |
| YES TECH MU 2.9 outdoor | 500 | 500 | 168 | 168 | 2.98 | 7.6 | 175 | 73 |
| YES TECH MU 2.9 outdoor 500×1000 | 500 | 1000 | 168 | 336 | 2.98 | 12.6 | 350 | 73 |
| YES TECH MU 3.9 outdoor | 500 | 500 | 128 | 128 | 3.91 | 7.6 | 175 | 73 |
| YES TECH MU 3.9 outdoor 500×1000 | 500 | 1000 | 128 | 256 | 3.91 | 12.6 | 350 | 73 |
| YES TECH Xtra 1.9 | 500 | 500 | 256 | 256 | 1.953 | 7.5 | 145 | 73 |
| YES TECH Xtra 2.6 | 500 | 500 | 192 | 192 | 2.6 | 7.5 | 163 | 73 |
| YES TECH Xtra 2.9 outdoor | 500 | 500 | 168 | 168 | 2.98 | 7.5 | 175 | 73 |
| YES TECH Xtra 3.9 outdoor | 500 | 500 | 128 | 128 | 3.91 | 7.5 | 175 | 73 |
| YES TECH MG6S Plus 1.9 | 500 | 750 | 256 | 384 | 1.95 | 8.3 | 150 | 73 |
| YES TECH MG6S Plus 2.6 | 500 | 750 | 192 | 288 | 2.6 | 8.3 | 169 | 73 |
| YES TECH MG6S Plus 2.8 | 500 | 750 | 176 | 264 | 2.84 | 8.2 | 158 | 73 |
| YES TECH MG6S Plus 3.9 | 500 | 750 | 128 | 192 | 3.91 | 7.6 | 158 | 73 |
| YES TECH MG6S Plus 5.2 | 500 | 750 | 96 | 144 | 5.21 | 7.5 | 158 | 73 |
| YES TECH MG6S 2.6 | 500 | 500 | 192 | 192 | 2.6 | 6.7 | 150 | 73 |
| YES TECH MG6S 2.84 | 500 | 500 | 176 | 176 | 2.84 | 6.2 | 105 | 73 |
| YES TECH MG6S 3.9 | 500 | 500 | 128 | 128 | 3.91 | 5.8 | 130 | 73 |
| YES TECH Mega 3.9 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 400 | 86 |
| YES TECH Mega 4.6 outdoor | 500 | 1000 | 108 | 216 | 4.63 | 12.5 | 400 | 86 |
| YES TECH Mega 5.7 outdoor | 500 | 1000 | 88 | 176 | 5.68 | 12.5 | 400 | 86 |
| YES TECH MAir 5.9 mesh outdoor | 1000 | 1000 | 168 | 168 | 5.95 | 19 | 500 | 102 |
| YES TECH MAir 7.8 mesh outdoor | 1000 | 1000 | 128 | 128 | 7.81 | 19 | 500 | 102 |
| YES TECH MAir 5.9 solid outdoor | 1000 | 1000 | 168 | 168 | 5.95 | 23.5 | 500 | 102 |
| YES TECH MT II 3.9-7.8 1000×500 | 1000 | 500 | 256 | 64 | 3.91 | 8.7 | 225 | 83 |
| YES TECH MT II 3.9-7.8 500×500 | 500 | 500 | 128 | 64 | 3.91 | 5.8 | 113 | 83 |
| Absen Polaris PL2.5 XR V2 | 500 | 500 | 200 | 200 | 2.5 | 7.8 | 185 | 78 |
| Absen Polaris PL3.9 Pro V3 | 500 | 500 | 128 | 128 | 3.906 | 11.5 | 180 | 88 |
| Absen A27 1.9 (A2719) | 610 | 343 | 320 | 180 | 1.906 | 8.5 | 105 | 61 |
| Absen A27 1.4 (A2714) | 610 | 343 | 416 | 234 | 1.46 | 8.5 | 97 | 61 |
| Absen A27 1.2 (A2712) | 610 | 343 | 480 | 270 | 1.27 | 8.5 | 97 | 61 |
| Absen KL3 | 640 | 480 | 208 | 156 | 3.07 | 7.8 | 166 | 60 |
| Absen Saturn SA2.6 | 500 | 500 | 192 | 192 | 2.6 | 5.5 | 128 | 70 |
| Absen Saturn SA2.6 1000×500 | 1000 | 500 | 384 | 192 | 2.6 | 9.5 | 255 | 70 |
| Absen Saturn SA3.9 | 500 | 500 | 128 | 128 | 3.906 | 5.5 | 160 | 70 |
| Absen Saturn SA3.9 1000×500 | 1000 | 500 | 256 | 128 | 3.906 | 9.5 | 320 | 70 |
| Absen PR1.9 | 500 | 500 | 256 | 256 | 1.953 | 9.5 | 143 | 93 |
| Absen PR2.5 | 500 | 500 | 200 | 200 | 2.5 | 9.5 | 150 | 93 |
| Absen PR2.5 500×1000 | 500 | 1000 | 200 | 400 | 2.5 | 13.5 | 300 | 93 |
| Absen PR3.9 | 500 | 500 | 128 | 128 | 3.906 | 9.5 | 150 | 93 |
| Absen PR3.9 500×1000 | 500 | 1000 | 128 | 256 | 3.906 | 13.5 | 300 | 93 |
| Absen PR5.2 | 500 | 500 | 96 | 96 | 5.208 | 9.5 | 145 | 93 |
| Absen PR5.2 500×1000 | 500 | 1000 | 96 | 192 | 5.208 | 13.5 | 290 | 93 |
| Absen Polaris PL1.9 Pro V10 | 500 | 500 | 256 | 256 | 1.953 | 9 | 180 | 88 |
| Absen Polaris PL2.9 Lite | 500 | 500 | 168 | 168 | 2.97 | 7.6 | 135 | 87 |
| Absen Polaris PL3.9 V10 | 500 | 500 | 128 | 128 | 3.906 | 7.7 | 135 | 88 |
| Absen KL1.5 II | 640 | 360 | 416 | 234 | 1.53 | 6 | 129 | 65 |
| Absen A27 1.5 (A2715 V3) | 610 | 343 | 384 | 216 | 1.58 | 5 | 113 | 44.5 |
| Absen NX2.5 | 960 | 540 | 384 | 216 | 2.5 | 10.4 | 233 | 43.5 |
| Unilumin UpadIV 1.9 | 500 | 500 | 256 | 256 | 1.953 | 6.3 | 150 | 70.1 |
| Unilumin UpadIV 1.9 MIP | 500 | 500 | 256 | 256 | 1.953 | 6.3 | 80 | 70.1 |
| Unilumin UpadIV 2.6 (8 scan) | 500 | 500 | 192 | 192 | 2.604 | 6.3 | 165 | 70.1 |
| INFiLED Deep Black DB1.9 M2 MK2 | 500 | 500 | 256 | 256 | 1.95 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB2.3 Pro | 500 | 500 | 216 | 216 | 2.31 | 8.8 | 150 | 75.5 |
| INFiLED Deep Black DB1.56 M4 | 500 | 500 | 320 | 320 | 1.5625 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB1.9 Lite | 500 | 500 | 256 | 256 | 1.953 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB1.9 Pro | 500 | 500 | 256 | 256 | 1.953 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB2.3 Lite | 500 | 500 | 216 | 216 | 2.315 | 8.8 | 150 | 75.5 |
| INFiLED Deep Black DB2.6 Lite | 500 | 500 | 192 | 192 | 2.604 | 8 | 150 | 75.5 |
| INFiLED Deep Black DB2.6 Pro | 500 | 500 | 192 | 192 | 2.604 | 8 | 150 | 75.5 |
| INFiLED Deep Black DB2.8 Lite | 500 | 500 | 176 | 176 | 2.84 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB3.4 Lite | 500 | 500 | 144 | 144 | 3.47 | 7.8 | 140 | 75.5 |
| INFiLED Deep Black DB3.4 Pro | 500 | 500 | 144 | 144 | 3.47 | 7.8 | 140 | 75.5 |
| INFiLED HR1.5 M4 | 600 | 337.5 | 384 | 216 | 1.5625 | 7.8 | 150 | 73 |
| INFiLED WP1.5 MT4 MK2 | 600 | 337.5 | 384 | 216 | 1.5625 | 5.2 | 52 | 29.7 |
| INFiLED AR3.4 Mini | 500 | 500 | 144 | 144 | 3.47 | 8 | 150 | 66 |
| INFiLED AR4.8 | 500 | 1000 | 104 | 208 | 4.81 | 12.5 | 270 | 66 |
| INFiLED AR4.6 Mini outdoor | 500 | 500 | 108 | 108 | 4.63 | 13 | 150 | 131 |
| YES TECH MG6S Pro 2.6 | 500 | 500 | 192 | 192 | 2.604 | 6 | 113 | 73 |
| YES TECH MG6S 4.8 | 500 | 500 | 104 | 104 | 4.807 | 5.6 | 105 | 73 |
| YES TECH MG6S 5.2 | 500 | 500 | 96 | 96 | 5.208 | 5.5 | 105 | 73 |
| Owl Vision Black Owl 3.9 500×1000 | 500 | 1000 | 128 | 256 | 3.906 | 14 | 360 | 74 |
| Owl Vision Black Owl 3.9 | 500 | 500 | 128 | 128 | 3.906 | 8.7 | 180 | 74 |
| Owl Vision Pilot 2.6 | 500 | 500 | 192 | 192 | 2.604 | 7.4 | 50 | 71 |
| INFiLED GX1.9 mk2 mini | 500 | 500 | 256 | 256 | 1.95 | 8.09 | 130 | 75.2 |
| INFiLED GX1.9 mk2 | 500 | 1000 | 256 | 512 | 1.95 | 13.98 | 260 | 75.2 |
| INFiLED GX2.5 mk2 | 500 | 1000 | 200 | 400 | 2.5 | 14.2 | 300 | 75.2 |
| INFiLED GX2.5 mk2 mini | 500 | 500 | 200 | 200 | 2.5 | 8.2 | 150 | 75.2 |
| INFiLED GX2.9 mk2 | 500 | 1000 | 168 | 336 | 2.97 | 14.06 | 300 | 75.2 |
| INFiLED GX2.9 mk2 mini | 500 | 500 | 168 | 168 | 2.97 | 8.12 | 150 | 75.2 |
| INFiLED GX3.9 mk2 | 500 | 1000 | 128 | 256 | 3.91 | 13.97 | 300 | 75.2 |
| INFiLED GX3.9 mk2 mini | 500 | 500 | 128 | 128 | 3.91 | 8.08 | 150 | 75.2 |
| INFiLED GX3.9 mk2 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 13.12 | 340 | 75.2 |
| INFiLED GX3.9 mk2 mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 7.66 | 170 | 75.2 |
| INFiLED GX4.8 mk2 mini | 500 | 500 | 104 | 104 | 4.81 | 8.08 | 150 | 75.2 |
| INFiLED GX4.6 mk2 mini outdoor | 500 | 500 | 108 | 108 | 4.63 | 7.92 | 170 | 75.2 |
| INFiLED GX4.6 mk2 outdoor | 500 | 1000 | 108 | 216 | 4.63 | 13.75 | 340 | 75.2 |
| INFiLED GX4.8 mk2 | 500 | 1000 | 104 | 208 | 4.81 | 13.97 | 300 | 75.2 |
| INFiLED GX5.9 mk2 outdoor | 500 | 1000 | 84 | 168 | 5.95 | 13.23 | 340 | 75.2 |
| INFiLED GX5.9 mk2 mini outdoor | 500 | 500 | 84 | 84 | 5.95 | 7.72 | 170 | 75.2 |
| INFiLED GX6.9 mk2 outdoor | 500 | 1000 | 72 | 144 | 6.94 | 13.2 | 340 | 75.2 |
| INFiLED GX6.9 mk2 mini outdoor | 500 | 500 | 72 | 72 | 6.94 | 7.7 | 170 | 75.2 |
| INFiLED BWAMT3.9 outdoor | 1000 | 1000 | 256 | 256 | 3.91 | 29 | 660 | 110 |
| INFiLED BWAMT4.6 outdoor | 1000 | 1000 | 216 | 216 | 4.63 | 29 | 660 | 110 |
| INFiLED BWAMT7.8 outdoor | 1000 | 1000 | 128 | 128 | 7.81 | 26.3 | 660 | 110 |
| INFiLED EZ1.95mk2 Lite | 500 | 500 | 256 | 256 | 1.95 | 5.9 | 150 | 75.5 |
| INFiLED EZ1.56MT2mk2 SSG Ultra | 500 | 500 | 320 | 320 | 1.56 | 6.5 | 125 | 75.5 |
| INFiLED EZ2.6mk2 | 500 | 500 | 192 | 192 | 2.6 | 5.9 | 150 | 75.5 |
| INFiLED EZ2.6mk2 Lite | 500 | 500 | 192 | 192 | 2.6 | 5.9 | 150 | 75.5 |
| INFiLED RS2.5 Ultra | 500 | 1000 | 200 | 400 | 2.5 | 9.45 | 270 | 81 |
| INFiLED RS2.5 Ultra mini | 500 | 500 | 200 | 200 | 2.5 | 6.1 | 135 | 81 |
| INFiLED RS2.5 Lite | 500 | 1000 | 200 | 400 | 2.5 | 9.2 | 270 | 81 |
| INFiLED RS2.5 Lite mini | 500 | 500 | 200 | 200 | 2.5 | 6.1 | 135 | 81 |
| INFiLED RS2.6 Ultra | 500 | 1000 | 192 | 384 | 2.6 | 9.45 | 270 | 81 |
| INFiLED RS2.6 Ultra mini | 500 | 500 | 192 | 192 | 2.6 | 6.1 | 135 | 81 |
| INFiLED RS2.9 Lite | 500 | 1000 | 168 | 336 | 2.97 | 9.2 | 270 | 81 |
| INFiLED RS2.9 Lite mini | 500 | 500 | 168 | 168 | 2.97 | 6.1 | 135 | 81 |
| INFiLED RS3.91 Lite outdoor | 500 | 1000 | 128 | 256 | 3.91 | 8.7 | 300 | 81 |
| INFiLED RS3.91 Lite mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 5.9 | 150 | 81 |
| INFiLED RS3.91 Turbo outdoor | 500 | 1000 | 128 | 256 | 3.91 | 8.7 | 300 | 81 |
| INFiLED RS3.91 Turbo mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 5.9 | 150 | 81 |
| INFiLED RS4.81 Lite outdoor | 500 | 1000 | 104 | 208 | 4.81 | 8.7 | 300 | 81 |
| INFiLED RS4.81 Lite mini outdoor | 500 | 500 | 104 | 104 | 4.81 | 5.9 | 150 | 81 |
| INFiLED RS6.94 Lite outdoor | 500 | 1000 | 72 | 144 | 6.94 | 8.7 | 300 | 81 |
| INFiLED RS6.94 Lite mini outdoor | 500 | 500 | 72 | 72 | 6.94 | 5.9 | 150 | 81 |
| INFiLED X1.56M2mk3 Ultra | 500 | 500 | 320 | 320 | 1.56 | 7.7 | 150 | 96.5 |
| INFiLED X1.95M2mk3 | 500 | 500 | 256 | 256 | 1.95 | 7.7 | 150 | 96.5 |
| INFiLED X1.95M2mk3 Ultra | 500 | 500 | 256 | 256 | 1.95 | 7.7 | 150 | 96.5 |
| INFiLED X1.95mk3 Lite | 500 | 500 | 256 | 256 | 1.95 | 7.7 | 165 | 96.5 |
| INFiLED X2.6M2mk3 Ultra | 500 | 500 | 192 | 192 | 2.6 | 7.7 | 150 | 96.5 |
| INFiLED X2.6mk3 Pro | 500 | 500 | 192 | 192 | 2.6 | 7.7 | 150 | 96.5 |
| INFiLED X3.9mk3 Lite | 500 | 500 | 128 | 128 | 3.9 | 7.6 | 150 | 96.5 |
| INFiLED X3.9mk3 Turbo outdoor | 500 | 500 | 128 | 128 | 3.9 | 8.1 | 180 | 96.5 |
| INFiLED TITAN X8 outdoor | 1200 | 1200 | 144 | 144 | 8.33 | 33 | 660 | 116 |
| INFiLED AR2.9mk2 Lite mini outdoor | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Pro outdoor | 500 | 1000 | 168 | 336 | 2.97 | 13.5 | 360 | 82 |
| INFiLED AR2.9mk2 Plus mini outdoor | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Plus outdoor | 500 | 1000 | 168 | 336 | 2.97 | 13.5 | 360 | 82 |
| INFiLED AR2.9mk2 Pro mini outdoor | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Turbo outdoor | 500 | 1000 | 168 | 336 | 2.97 | 13.5 | 360 | 82 |
| INFiLED AR2.9mk2 Turbo mini outdoor | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Lite outdoor | 500 | 1000 | 168 | 336 | 2.97 | 13.5 | 360 | 82 |
| INFiLED AR2.9mk2 Pro mini | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Pro | 500 | 1000 | 168 | 336 | 2.97 | 12.5 | 360 | 82 |
| INFiLED AR2.9mk2 Lite mini | 500 | 500 | 168 | 168 | 2.97 | 8 | 180 | 82 |
| INFiLED AR2.9mk2 Lite | 500 | 1000 | 168 | 336 | 2.97 | 12.5 | 360 | 82 |
| INFiLED AR3.9mk2 Ultra outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.91mk2 Plus outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.91mk2 Plus mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.91mk2 Pro outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.91mk2 Pro mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Lite outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.9mk2 Lite mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Pro mini | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Pro | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.9mk2 Lite mini | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Lite | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR3.9mk2 Ultra mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Turbo mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 8 | 180 | 82 |
| INFiLED AR3.9mk2 Turbo outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.5 | 360 | 82 |
| INFiLED AR4.8mk2 Pro mini | 500 | 500 | 104 | 104 | 4.81 | 8 | 180 | 82 |
| INFiLED AR4.8mk2 Pro | 500 | 1000 | 104 | 208 | 4.81 | 12.5 | 360 | 82 |
| INFiLED AR4.8mk2 Lite mini | 500 | 500 | 104 | 104 | 4.81 | 8 | 180 | 82 |
| INFiLED AR4.8mk2 Lite | 500 | 1000 | 104 | 208 | 4.81 | 12.5 | 360 | 82 |
| INFiLED ART3.9 mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 13 | 180 | 131 |
| INFiLED ART3.9 CC outdoor | 500 | 1000 | 128 | 256 | 3.91 | 21 | 300 | 131 |
| INFiLED ART3.9 CC mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 13 | 150 | 131 |
| INFiLED ART3.9 Plus outdoor | 500 | 1000 | 128 | 256 | 3.91 | 21 | 360 | 131 |
| INFiLED ART3.9 Plus mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 13 | 180 | 131 |
| INFiLED ART3.9 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 21 | 360 | 131 |
| INFiLED ART3.9 Turbo mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 13 | 180 | 131 |
| INFiLED ART3.9 Turbo outdoor | 500 | 1000 | 128 | 256 | 3.91 | 21 | 360 | 131 |
| INFiLED ART4.6 Turbo mini outdoor | 500 | 500 | 108 | 108 | 4.63 | 13 | 180 | 131 |
| INFiLED ART4.6 Turbo outdoor | 500 | 1000 | 108 | 216 | 4.63 | 21 | 360 | 131 |
| INFiLED ART4.6 Plus mini outdoor | 500 | 500 | 108 | 108 | 4.63 | 13 | 180 | 131 |
| INFiLED ART4.6 Plus outdoor | 500 | 1000 | 108 | 216 | 4.63 | 21 | 360 | 131 |
| INFiLED ART4.6 mini outdoor | 500 | 500 | 108 | 108 | 4.63 | 13 | 180 | 131 |
| INFiLED ART4.6 outdoor | 500 | 1000 | 108 | 216 | 4.63 | 21 | 360 | 131 |
| INFiLED ART5.9 outdoor | 500 | 1000 | 84 | 168 | 5.95 | 21 | 360 | 131 |
| INFiLED ART5.9 mini outdoor | 500 | 500 | 84 | 84 | 5.95 | 13 | 180 | 131 |
| INFiLED ART7.8 outdoor | 500 | 1000 | 64 | 128 | 7.81 | 21 | 360 | 131 |
| INFiLED ART7.8 mini outdoor | 500 | 500 | 64 | 64 | 7.81 | 13 | 180 | 131 |
| INFiLED ART10.4 outdoor | 500 | 1000 | 48 | 96 | 10.41 | 22 | 360 | 131 |
| INFiLED ART10.4 mini outdoor | 500 | 500 | 48 | 48 | 10.41 | 13 | 180 | 131 |
| INFiLED AP2.5 | 500 | 1000 | 200 | 400 | 2.5 | 9.1 | 270 | 82 |
| INFiLED AP2.5 mini | 500 | 500 | 200 | 200 | 2.5 | 5.9 | 135 | 82 |
| INFiLED AP3.9 | 500 | 1000 | 128 | 256 | 3.91 | 8.9 | 270 | 82 |
| INFiLED AP3.9 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 8.7 | 300 | 82 |
| INFiLED AP3.9 mini | 500 | 500 | 128 | 128 | 3.91 | 5.9 | 135 | 82 |
| INFiLED AP3.9 mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 5.7 | 150 | 82 |
| INFiLED AP4.8 outdoor | 500 | 1000 | 104 | 208 | 4.81 | 8.7 | 300 | 82 |
| INFiLED AP4.8 mini outdoor | 500 | 500 | 104 | 104 | 4.81 | 5.7 | 150 | 82 |
| INFiLED AP6.9 outdoor | 500 | 1000 | 72 | 144 | 6.94 | 8.7 | 300 | 82 |
| INFiLED AP6.9 mini outdoor | 500 | 500 | 72 | 72 | 6.94 | 5.7 | 150 | 82 |
| INFiLED AP8.9 outdoor | 500 | 1000 | 56 | 112 | 8.92 | 8.7 | 300 | 82 |
| INFiLED AP8.9 mini outdoor | 500 | 500 | 56 | 56 | 8.92 | 5.7 | 150 | 82 |
| INFiLED AMT5.95 outdoor | 1000 | 1000 | 168 | 168 | 5.95 | 20.4 | 720 | 108 |
| INFiLED AMT8.33 Mesh Turbo outdoor | 1000 | 1000 | 120 | 120 | 8.33 | 15.5 | 500 | 108 |
| INFiLED AMT8.33 Mesh outdoor | 1000 | 1000 | 120 | 120 | 8.33 | 15.5 | 500 | 108 |
| INFiLED DB1.95 VSS M2 | 500 | 500 | 256 | 256 | 1.95 | 9.4 | 150 | 75.5 |
| INFiLED X1.9mk2 M2 CBSF | 500 | 500 | 256 | 256 | 1.95 | 8.3 | 150 | 75.5 |
| INFiLED DB1.95mk2 M2 CBSF | 500 | 500 | 256 | 256 | 1.95 | 8.4 | 120 | 75.5 |
| INFiLED DB1.56mk2 MT2 CBSF | 500 | 500 | 320 | 320 | 1.56 | 8.4 | 160 | 75.5 |
| INFiLED DB1.9 VSS | 500 | 500 | 256 | 256 | 1.95 | 8.8 | 180 | 75.5 |
| INFiLED X1.9mk2 VSS | 500 | 500 | 256 | 256 | 1.95 | 8.3 | 160 | 75.5 |
| INFiLED DB2.6 AD | 500 | 500 | 192 | 192 | 2.6 | 8.8 | 180 | 75.5 |
| INFiLED DB2.6mk2 MT2 CBSF | 500 | 500 | 192 | 192 | 2.6 | 7.8 | 170 | 75.5 |
| INFiLED DF2.6mk2 VSS outdoor | 500 | 500 | 192 | 192 | 2.6 | 11.5 | 180 | 83.3 |
| INFiLED X2.6mk2 VSS | 500 | 500 | 192 | 192 | 2.6 | 8.3 | 180 | 75.5 |
| INFiLED DB2.8 VSS | 500 | 500 | 176 | 176 | 2.84 | 8.8 | 180 | 75.5 |
| INFiLED DB2.6 VSS | 500 | 500 | 192 | 192 | 2.6 | 8.8 | 180 | 75.5 |
| INFiLED X2.6mk2 MT2 CBSF | 500 | 500 | 192 | 192 | 2.56 | 8.3 | 150 | 75.5 |
| INFiLED X2.6mk2 LS | 500 | 500 | 192 | 192 | 2.6 | 8.3 | 180 | 75.5 |
| INFiLED AR3.9 LS | 500 | 1000 | 128 | 256 | 3.91 | 11.3 | 360 | 77 |
| INFiLED DF3.9mk2 VSS outdoor | 500 | 500 | 128 | 128 | 3.91 | 11.5 | 210 | 83.3 |
| INFiLED DF3.9mk2 AD outdoor | 500 | 500 | 128 | 128 | 3.91 | 11.5 | 210 | 83.3 |
| INFiLED DF3.9mk2 LS outdoor | 500 | 500 | 128 | 128 | 3.91 | 11.5 | 210 | 83.3 |
| INFiLED AR3.9 VSS | 500 | 1000 | 128 | 256 | 3.91 | 11.3 | 360 | 77 |
| INFiLED AR3.9 AD | 500 | 1000 | 128 | 256 | 3.91 | 11.3 | 360 | 77 |
| INFiLED AR3.91 VSS | 500 | 1000 | 128 | 256 | 3.91 | 11.3 | 300 | 77 |
| INFiLED AR5.9RGBW | 500 | 1000 | 84 | 168 | 5.95 | 12.5 | 360 | 77 |
| INFiLED AR5.9 VSS | 500 | 1000 | 84 | 168 | 5.95 | 10.9 | 360 | 77 |
| INFiLED AR5.9 LS | 500 | 1000 | 84 | 168 | 5.95 | 10.9 | 360 | 77 |
| INFiLED AR5.9 AD | 500 | 1000 | 84 | 168 | 5.95 | 10.9 | 360 | 77 |
| INFiLED DB1.5mk2 Ultra MT2 | 500 | 500 | 320 | 320 | 1.56 | 8.4 | 120 | 75.5 |
| INFiLED DB1.9mk2 Ultra M2 | 500 | 500 | 256 | 256 | 1.95 | 7.8 | 130 | 75.5 |
| INFiLED DB1.95mk2 VSS | 500 | 500 | 256 | 256 | 1.95 | 8.4 | 180 | 75.5 |
| INFiLED DB2.6mk2 Ultra MT2 | 500 | 500 | 192 | 192 | 2.6 | 7.8 | 140 | 75.5 |
| INFiLED DBmk2 2.6 Lite | 500 | 500 | 192 | 192 | 2.6 | 8 | 150 | 75.5 |
| INFiLED DBmk2 2.6 Pro | 500 | 500 | 192 | 192 | 2.6 | 8 | 150 | 75.5 |
| INFiLED DB2.6mk2 | 500 | 500 | 192 | 192 | 2.6 | 8.4 | 180 | 75.5 |
| INFiLED MC2DB1.95M2 Ultra | 500 | 500 | 256 | 256 | 1.95 | 8.3 | 140 | 75.5 |
| INFiLED MC2DB1.56MT2 Ultra | 500 | 500 | 320 | 320 | 1.56 | 8.4 | 140 | 75.5 |
| INFiLED MC2DB1.56MT2mk2 CBSF | 500 | 500 | 320 | 320 | 1.56 | 8.4 | 140 | 75.5 |
| INFiLED MC2DB1.95M2mk2 CBSF | 500 | 500 | 256 | 256 | 1.95 | 7.8 | 140 | 75.5 |
| INFiLED MC2DB2.6MT2 Ultra | 500 | 500 | 192 | 192 | 2.6 | 7.8 | 150 | 75.5 |
| INFiLED MC2DB2.6MT2mk2 CBSF | 500 | 500 | 192 | 192 | 2.6 | 8.3 | 150 | 75.5 |
| INFiLED NX1.95 mini | 500 | 500 | 256 | 256 | 1.95 | 6.8 | 150 | 73 |
| INFiLED NX1.95 | 500 | 1000 | 256 | 512 | 1.95 | 11 | 300 | 73 |
| INFiLED NX2.5 mini | 500 | 500 | 200 | 200 | 2.5 | 6.8 | 150 | 73 |
| INFiLED NX2.5 | 500 | 1000 | 200 | 400 | 2.5 | 11 | 300 | 73 |
| INFiLED NX3.91 mini outdoor | 500 | 500 | 128 | 128 | 3.91 | 6.8 | 150 | 73 |
| INFiLED NX3.91 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 10.9 | 300 | 73 |
| INFiLED EZ2.6 Lite outdoor | 500 | 500 | 192 | 192 | 2.6 | 7.6 | 180 | 82 |
| INFiLED EZ2.6 Plus outdoor | 500 | 500 | 192 | 192 | 2.6 | 7.6 | 210 | 82 |
| INFiLED EZ2.6 Pro outdoor | 500 | 500 | 192 | 192 | 2.6 | 7.6 | 180 | 82 |
| INFiLED EZ2.6 Turbo outdoor | 500 | 500 | 192 | 192 | 2.6 | 7.6 | 180 | 82 |
| INFiLED AM8.3mk2 outdoor | 1200 | 1200 | 144 | 144 | 8.33 | 15.5 | 660 | 55.4 |
| INFiLED AM8.3mk2 Pro outdoor | 1200 | 1200 | 144 | 144 | 8.33 | 15.5 | 660 | 55.4 |
| INFiLED AM8.3mk2 mini outdoor | 1200 | 600 | 144 | 72 | 8.33 | 8.5 | 330 | 55.4 |
| INFiLED AM8.3mk2 Pro mini outdoor | 1200 | 600 | 144 | 72 | 8.33 | 8.5 | 330 | 55.4 |
| AOTO RM1.5 | 500 | 500 | 320 | 320 | 1.56 | 8.2 | 190 | 67.5 |
| AOTO RM1.5E | 500 | 500 | 320 | 320 | 1.56 | 8.2 | 150 | 67.5 |
| AOTO RM1.9 | 500 | 500 | 256 | 256 | 1.95 | 8.2 | 150 | 67.5 |
| AOTO RM2.3 | 500 | 500 | 216 | 216 | 2.31 | 8.2 | 167 | 67.5 |
| AOTO RM2.3E | 500 | 500 | 216 | 216 | 2.31 | 8.2 | 153 | 67.5 |
| AOTO RM1.5B | 500 | 500 | 320 | 320 | 1.56 | 9.3 | 185 | 67.5 |
| AOTO RM2.3B | 500 | 500 | 216 | 216 | 2.31 | 9.3 | 155 | 67.5 |
| AOTO DL1.9 | 500 | 500 | 256 | 256 | 1.95 | 7.2 | 125 | 76 |
| AOTO DL2.3 | 500 | 500 | 216 | 216 | 2.31 | 7.2 | 150 | 76 |
| AOTO DL2.6 | 500 | 500 | 192 | 192 | 2.604 | 7.2 | 160 | 76 |
| AOTO SV3.9 | 500 | 1000 | 128 | 256 | 3.91 | 14.8 | 380 | 104 |
| AOTO C1.8 | 480 | 480 | 256 | 256 | 1.875 | 3.88 | 110 | 82 |
| AOTO C2.5 | 480 | 480 | 192 | 192 | 2.5 | 3.88 | 100 | 82 |
| AOTO C3 | 480 | 480 | 160 | 160 | 3 | 3.88 | 116 | 82 |
| Absen Polaris PL2.5 Pro V10 | 500 | 500 | 200 | 200 | 2.5 | 8.6 | 170 | 88 |
| Absen Polaris PL2.9 V10 | 500 | 500 | 168 | 168 | 2.97 | 8 | 135 | 88 |
| Absen Polaris PL2.9 XL V10 | 500 | 1000 | 168 | 336 | 2.97 | 12.6 | 270 | 88 |
| Absen Polaris PL3.9 XL V10 | 500 | 1000 | 128 | 256 | 3.906 | 12.6 | 270 | 88 |
| Absen Polaris PL3.9 Pro V10 | 500 | 500 | 128 | 128 | 3.906 | 8.4 | 170 | 88 |
| Absen Polaris PL3.9 Pro XL V10 | 500 | 1000 | 128 | 256 | 3.906 | 13.7 | 340 | 88 |
| Absen Polaris PL4.8 Pro V10 | 500 | 500 | 104 | 104 | 4.81 | 8.1 | 180 | 88 |
| Absen Polaris PL4.8 Pro XL V10 | 500 | 1000 | 104 | 208 | 4.81 | 13.7 | 360 | 88 |
| Absen A27 1.2 (A2712 V3) | 610 | 343 | 480 | 270 | 1.27 | 5 | 118 | 44.5 |
| Absen A27 1.9 (A2719 V3) | 610 | 343 | 320 | 180 | 1.906 | 5 | 99 | 44.5 |
| Absen A27 2.5 (A2725 V3) | 610 | 343 | 240 | 135 | 2.54 | 5 | 63 | 44.5 |
| Gloshine DN1.9 | 500 | 500 | 256 | 256 | 1.95 | 7 | 145 | 76 |
| Gloshine DN2.6 | 500 | 500 | 192 | 192 | 2.6 | 7 | 145 | 76 |
| Gloshine DN2.6 500×1000 | 500 | 1000 | 192 | 384 | 2.6 | 11.8 | 290 | 76 |
| Gloshine DN2.9 | 500 | 500 | 168 | 168 | 2.97 | 7 | 145 | 76 |
| Gloshine DN2.9 500×1000 | 500 | 1000 | 168 | 336 | 2.97 | 11.8 | 290 | 76 |
| Gloshine DN3.9 | 500 | 500 | 128 | 128 | 3.91 | 7 | 145 | 76 |
| Gloshine DN3.9 500×1000 | 500 | 1000 | 128 | 256 | 3.91 | 11.8 | 290 | 76 |
| Gloshine DN3.9 outdoor | 500 | 500 | 128 | 128 | 3.91 | 7.2 | 145 | 76 |
| Gloshine DN3.9 500×1000 outdoor | 500 | 1000 | 128 | 256 | 3.91 | 12.2 | 290 | 76 |
| Gloshine DN4.8 outdoor | 500 | 500 | 104 | 104 | 4.81 | 7.2 | 180 | 76 |
| Gloshine DN4.8 500×1000 outdoor | 500 | 1000 | 104 | 208 | 4.81 | 12.2 | 360 | 76 |
| Gloshine CF Pro1.9 | 500 | 500 | 256 | 256 | 1.95 | 8.5 | 135 | 107 |
| Gloshine CF Pro2.3 | 500 | 500 | 208 | 208 | 2.38 | 8.5 | 135 | 107 |
| Gloshine CF Pro2.6 (1/16 scan) | 500 | 500 | 192 | 192 | 2.6 | 8.5 | 135 | 107 |
| Gloshine CF Pro2.6 (1/24 scan) | 500 | 500 | 192 | 192 | 2.6 | 8.5 | 135 | 107 |
| Gloshine CF Pro2.9 | 500 | 500 | 168 | 168 | 2.97 | 8.5 | 135 | 107 |
| Gloshine CF Pro3.9 | 500 | 500 | 128 | 128 | 3.91 | 8.5 | 135 | 107 |
| Aluvision Hi-LED 55 1.9 | 496 | 496 | 256 | 256 | 1.9 | 9.5 | 120 | 55 |
| Aluvision Hi-LED 55 2.5 | 496 | 496 | 192 | 192 | 2.58 | 9.5 | 150 | 55 |
| Aluvision Hi-LED 55 2.8 | 496 | 496 | 176 | 176 | 2.82 | 9 | 145 | 55 |
| Aluvision Hi-LED 55 OU 3.9 outdoor | 496 | 496 | 128 | 128 | 3.88 | 9.1 | 130 | 62 |
| Aluvision Hi-LED 55 R437 concave 2.5 | 689 | 496 | 266 | 192 | 2.58 | 14 | 209 | 55 |
| Aluvision Hi-LED 55 R437 concave 2.8 | 689 | 496 | 244 | 176 | 2.82 | 14 | 181 | 55 |
| Aluvision Hi-LED 55 R437 convex 2.5 | 772 | 496 | 300 | 192 | 2.58 | 14 | 243 | 55 |
| Aluvision Hi-LED 55 R437 convex 2.8 | 772 | 496 | 274 | 176 | 2.82 | 14 | 203 | 55 |
| Aluvision Hi-LED 55 R1421 convex 2.5 | 772 | 496 | 300 | 192 | 2.58 | 14 | 243 | 55 |
| Aluvision Hi-LED 55 R1421 convex 2.8 | 772 | 496 | 274 | 176 | 2.82 | 14 | 203 | 55 |
| Aluvision Hi-LED 55 R1476 concave 2.5 | 772 | 496 | 300 | 192 | 2.58 | 14 | 243 | 55 |
| Aluvision Hi-LED 55 R1476 concave 2.8 | 772 | 496 | 274 | 176 | 2.82 | 14 | 203 | 55 |

## 6. Wall shapes: removed tiles and half tiles

Every wall is a list of **pieces** computed from its settings (cached until the wall changes). Each piece has a key, a
pixel rectangle inside the wall (x, y, w, h), its anchor cell (col, row = the cell holding its top-left corner), a kind
(full, half, full on its side), its own spec (kg, W, m^2, mm) and a build order.

### 6.1 Plain grid with removed tiles (any model)

One full piece per cell except cells listed in `gone`. Remove tiles mode (Size of LED Wall submenu): press on a tile to
take it out, or on a removed spot to put it back; dragging applies the same choice to every cell crossed. "Restore all
tiles" clears the list. Tile IDs keep their grid numbers (T = row x cols + col + 1).

### 6.2 Half-tile layout (models with a half version)

| Full model | Half model | Split |
|---|---|---|
| Absen PR2.5 500×1000 | Absen PR2.5 | h = top/bottom (half height) |
| Absen PR3.9 500×1000 | Absen PR3.9 | h = top/bottom (half height) |
| Absen PR5.2 500×1000 | Absen PR5.2 | h = top/bottom (half height) |
| Owl Vision Black Owl 3.9 500×1000 | Owl Vision Black Owl 3.9 | h = top/bottom (half height) |
| ROE Carbon CB3 | ROE Carbon CB3 Half | h = top/bottom (half height) |
| ROE Carbon CB5 | ROE Carbon CB5 Half | h = top/bottom (half height) |
| ROE Carbon CB8 | ROE Carbon CB8 Half | h = top/bottom (half height) |
| ROE Black Quartz BQ3.9 | ROE Black Quartz BQ3.9 Half | h = top/bottom (half height) |
| ROE Black Quartz BQ4.6 | ROE Black Quartz BQ4.6 Half | h = top/bottom (half height) |
| ROE Black Quartz BQ6.2 | ROE Black Quartz BQ6.2 Half | h = top/bottom (half height) |
| ROE Carbon MkII CB3 | ROE Carbon MkII CB3 Half | h = top/bottom (half height) |
| ROE Carbon MkII CB5 | ROE Carbon MkII CB5 Half | h = top/bottom (half height) |
| ROE Carbon MkII CB8 | ROE Carbon MkII CB8 Half | h = top/bottom (half height) |
| ROE Graphite GP1.9 (4 in 1) | ROE Graphite GP1.9 (4 in 1) Half | h = top/bottom (half height) |
| ROE Graphite GP2.6 (4 in 1) | ROE Graphite GP2.6 (4 in 1) Half | h = top/bottom (half height) |
| ROE Graphite GP2.6 | ROE Graphite GP2.6 Half | h = top/bottom (half height) |
| ROE Graphite GP3.1 | ROE Graphite GP3.1 Half | h = top/bottom (half height) |
| ROE Graphite GP3.9 | ROE Graphite GP3.9 Half | h = top/bottom (half height) |
| ROE Jasper JA2.6 | ROE Jasper JA2.6 Half | h = top/bottom (half height) |
| ROE Jasper JA3.9 | ROE Jasper JA3.9 Half | h = top/bottom (half height) |
| ROE Jet JT2.2 | ROE Jet JT2.2 Half | h = top/bottom (half height) |
| ROE Jet JT2.6 | ROE Jet JT2.6 Half | h = top/bottom (half height) |
| ROE Jet JT3.1 | ROE Jet JT3.1 Half | h = top/bottom (half height) |
| ROE Jet JT3.9 | ROE Jet JT3.9 Half | h = top/bottom (half height) |
| ROE Meru MR1.9 | ROE Meru MR1.9 Half | h = top/bottom (half height) |
| ROE Meru MR2.6 | ROE Meru MR2.6 Half | h = top/bottom (half height) |
| ROE Carbon CB8-Transparent | ROE Carbon CB8-Transparent Half | h = top/bottom (half height) |
| YES TECH MU 2.6 500×1000 | YES TECH MU 2.6 | h = top/bottom (half height) |
| YES TECH MU 3.9 500×1000 | YES TECH MU 3.9 | h = top/bottom (half height) |
| YES TECH MU 4.8 500×1000 | YES TECH MU 4.8 | h = top/bottom (half height) |
| YES TECH MU 2.9 outdoor 500×1000 | YES TECH MU 2.9 outdoor | h = top/bottom (half height) |
| YES TECH MU 3.9 outdoor 500×1000 | YES TECH MU 3.9 outdoor | h = top/bottom (half height) |
| YES TECH MT II 3.9-7.8 1000×500 | YES TECH MT II 3.9-7.8 500×500 | w = left/right (half width) |
| INFiLED GX1.9 mk2 | INFiLED GX1.9 mk2 mini | h = top/bottom (half height) |
| INFiLED GX2.5 mk2 | INFiLED GX2.5 mk2 mini | h = top/bottom (half height) |
| INFiLED GX2.9 mk2 | INFiLED GX2.9 mk2 mini | h = top/bottom (half height) |
| INFiLED GX3.9 mk2 | INFiLED GX3.9 mk2 mini | h = top/bottom (half height) |
| INFiLED GX3.9 mk2 outdoor | INFiLED GX3.9 mk2 mini outdoor | h = top/bottom (half height) |
| INFiLED GX4.8 mk2 | INFiLED GX4.8 mk2 mini | h = top/bottom (half height) |
| INFiLED GX4.6 mk2 outdoor | INFiLED GX4.6 mk2 mini outdoor | h = top/bottom (half height) |
| INFiLED GX5.9 mk2 outdoor | INFiLED GX5.9 mk2 mini outdoor | h = top/bottom (half height) |
| INFiLED GX6.9 mk2 outdoor | INFiLED GX6.9 mk2 mini outdoor | h = top/bottom (half height) |
| INFiLED RS2.5 Ultra | INFiLED RS2.5 Ultra mini | h = top/bottom (half height) |
| INFiLED RS2.5 Lite | INFiLED RS2.5 Lite mini | h = top/bottom (half height) |
| INFiLED RS2.6 Ultra | INFiLED RS2.6 Ultra mini | h = top/bottom (half height) |
| INFiLED RS2.9 Lite | INFiLED RS2.9 Lite mini | h = top/bottom (half height) |
| INFiLED RS3.91 Lite outdoor | INFiLED RS3.91 Lite mini outdoor | h = top/bottom (half height) |
| INFiLED RS3.91 Turbo outdoor | INFiLED RS3.91 Turbo mini outdoor | h = top/bottom (half height) |
| INFiLED RS4.81 Lite outdoor | INFiLED RS4.81 Lite mini outdoor | h = top/bottom (half height) |
| INFiLED RS6.94 Lite outdoor | INFiLED RS6.94 Lite mini outdoor | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Lite outdoor | INFiLED AR2.9mk2 Lite mini outdoor | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Plus outdoor | INFiLED AR2.9mk2 Plus mini outdoor | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Pro outdoor | INFiLED AR2.9mk2 Pro mini outdoor | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Turbo outdoor | INFiLED AR2.9mk2 Turbo mini outdoor | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Pro | INFiLED AR2.9mk2 Pro mini | h = top/bottom (half height) |
| INFiLED AR2.9mk2 Lite | INFiLED AR2.9mk2 Lite mini | h = top/bottom (half height) |
| INFiLED AR3.91mk2 Plus outdoor | INFiLED AR3.91mk2 Plus mini outdoor | h = top/bottom (half height) |
| INFiLED AR3.91mk2 Pro outdoor | INFiLED AR3.91mk2 Pro mini outdoor | h = top/bottom (half height) |
| INFiLED AR3.9mk2 Lite outdoor | INFiLED AR3.9mk2 Lite mini outdoor | h = top/bottom (half height) |
| INFiLED AR3.9mk2 Pro | INFiLED AR3.9mk2 Pro mini | h = top/bottom (half height) |
| INFiLED AR3.9mk2 Lite | INFiLED AR3.9mk2 Lite mini | h = top/bottom (half height) |
| INFiLED AR3.9mk2 Ultra outdoor | INFiLED AR3.9mk2 Ultra mini outdoor | h = top/bottom (half height) |
| INFiLED AR3.9mk2 Turbo outdoor | INFiLED AR3.9mk2 Turbo mini outdoor | h = top/bottom (half height) |
| INFiLED AR4.8mk2 Pro | INFiLED AR4.8mk2 Pro mini | h = top/bottom (half height) |
| INFiLED AR4.8mk2 Lite | INFiLED AR4.8mk2 Lite mini | h = top/bottom (half height) |
| INFiLED ART3.9 outdoor | INFiLED ART3.9 mini outdoor | h = top/bottom (half height) |
| INFiLED ART3.9 CC outdoor | INFiLED ART3.9 CC mini outdoor | h = top/bottom (half height) |
| INFiLED ART3.9 Plus outdoor | INFiLED ART3.9 Plus mini outdoor | h = top/bottom (half height) |
| INFiLED ART3.9 Turbo outdoor | INFiLED ART3.9 Turbo mini outdoor | h = top/bottom (half height) |
| INFiLED ART4.6 Turbo outdoor | INFiLED ART4.6 Turbo mini outdoor | h = top/bottom (half height) |
| INFiLED ART4.6 Plus outdoor | INFiLED ART4.6 Plus mini outdoor | h = top/bottom (half height) |
| INFiLED ART4.6 outdoor | INFiLED ART4.6 mini outdoor | h = top/bottom (half height) |
| INFiLED ART5.9 outdoor | INFiLED ART5.9 mini outdoor | h = top/bottom (half height) |
| INFiLED ART7.8 outdoor | INFiLED ART7.8 mini outdoor | h = top/bottom (half height) |
| INFiLED ART10.4 outdoor | INFiLED ART10.4 mini outdoor | h = top/bottom (half height) |
| INFiLED AP2.5 | INFiLED AP2.5 mini | h = top/bottom (half height) |
| INFiLED AP3.9 | INFiLED AP3.9 mini | h = top/bottom (half height) |
| INFiLED AP3.9 outdoor | INFiLED AP3.9 mini outdoor | h = top/bottom (half height) |
| INFiLED AP4.8 outdoor | INFiLED AP4.8 mini outdoor | h = top/bottom (half height) |
| INFiLED AP6.9 outdoor | INFiLED AP6.9 mini outdoor | h = top/bottom (half height) |
| INFiLED AP8.9 outdoor | INFiLED AP8.9 mini outdoor | h = top/bottom (half height) |
| INFiLED NX1.95 | INFiLED NX1.95 mini | h = top/bottom (half height) |
| INFiLED NX2.5 | INFiLED NX2.5 mini | h = top/bottom (half height) |
| INFiLED NX3.91 outdoor | INFiLED NX3.91 mini outdoor | h = top/bottom (half height) |
| INFiLED AM8.3mk2 outdoor | INFiLED AM8.3mk2 mini outdoor | h = top/bottom (half height) |
| INFiLED AM8.3mk2 Pro outdoor | INFiLED AM8.3mk2 Pro mini outdoor | h = top/bottom (half height) |
| Absen Polaris PL2.9 XL V10 | Absen Polaris PL2.9 V10 | h = top/bottom (half height) |
| Absen Polaris PL3.9 XL V10 | Absen Polaris PL3.9 V10 | h = top/bottom (half height) |
| Absen Polaris PL3.9 Pro XL V10 | Absen Polaris PL3.9 Pro V10 | h = top/bottom (half height) |
| Absen Polaris PL4.8 Pro XL V10 | Absen Polaris PL4.8 Pro V10 | h = top/bottom (half height) |
| Gloshine DN2.6 500×1000 | Gloshine DN2.6 | h = top/bottom (half height) |
| Gloshine DN2.9 500×1000 | Gloshine DN2.9 | h = top/bottom (half height) |
| Gloshine DN3.9 500×1000 | Gloshine DN3.9 | h = top/bottom (half height) |
| Gloshine DN3.9 500×1000 outdoor | Gloshine DN3.9 outdoor | h = top/bottom (half height) |
| Gloshine DN4.8 500×1000 outdoor | Gloshine DN4.8 outdoor | h = top/bottom (half height) |

The wall is a grid of half-tile **units**: for split h, units are tw x th/2 and the unit grid is cols x 2*rows; for
split w, units are tw/2 x th and the grid is 2*cols x rows. A piece is [u, v, a, b] = top-left unit and size in units:
1x1 = half tile; the model's upright full tile = 1x2 (h) or 2x1 (w); ROE models may also use the turned full tile
(2x1 for h). Pieces never overlap; any unit not covered is empty (black). The default layout is one upright full piece
per non-removed cell. Half tile controls sit in the Size of LED Wall submenu (only for models in HALF): Convert bottom row to
half tiles / Convert top row to half tiles (toggle: the label becomes Restore ... row to full tiles). Half-height models only ('h'):
bottom row = remove the last unit row (full tiles shrink to their top half, lone bottom halves are dropped), top row = remove
unit row 0 (full tiles keep their bottom half); restoring grows every lone half in the kept row back to a full tile when the
removed unit above/below is free. Wall size (wW, wH) on a half-tile layout is the bounding box of the real pieces; piece x,y
are relative to that box; wall position ox,oy is the box's top-left corner and gx,gy (wall keys, grid offset in px) record where
that corner sits inside the full tile grid, so tiles keep their canvas position when the layout changes (wNorm). Patterns get the
box size; the tile-shade checkerboard is drawn on the full grid shifted by (gx,gy). In marking mode the whole tile grid of the
selected wall (dotted outline) is clickable and a red STOP MARKING HALF TILES button is shown over the top of the viewport (Esc also
stops). Mark half tiles mode; a press at a point decides one action:

1. If the point is within 22% of a unit edge, and the unit and the neighbour across that edge each hold a half piece,
   and the pair forms an allowed full tile (stacked = upright for h; side by side = turned, ROE only), **join** them
   into one full piece. This also joins across a row line, giving a full tile offset by half a cell. If they cannot
   join, do nothing.
2. Else, on a full piece: **split** it, keeping a half piece on the clicked unit (the other unit becomes empty).
3. Else, on an empty unit: **fill** it with a half piece.
4. Else (on a half piece): **clear** it (take it out).

Dragging repeats the press's action (split/fill/clear, not join) on every unit crossed. "Clear half tiles" returns to a
plain grid (`lay = {}`). In Remove tiles mode on a layout: press on a piece removes the whole piece; press on an
empty unit puts back a full upright piece if its whole cell is empty, else a half piece. "Restore all tiles" fills
every empty cell with a full piece and leftover empty units with halves. If the grid grows, cells beyond the layout's
saved unit size get full pieces; pieces outside the grid are dropped; turned pieces on a non-ROE model show as two
halves. The layout is ignored (kept) while the wall uses a model without that split. On a layout, tile IDs are
numbered in reading order of the pieces (top, then left) and half tiles end in " ½".

Half piece spec: from the half preset (kg, W, mm); turned full: same as full with mm swapped. Pixels are the piece's
rectangle.

## 7. Rendering the canvas

Redraw the whole canvas (opaque, #050608 background) each frame something moves, at most 60 fps (or at the output
timer's rate while NDI, Spout or Syphon runs); when nothing moves, redraw 4 times a second as a safety net. For each wall:

1. **Lit set**: during a build, the first `inst` pieces of the wall's build order; otherwise all.
2. **Unlit outlines**: dashed #2a3340 rectangle for each piece not lit yet.
3. **Pattern**: clip to the lit pieces' rectangles (or the whole wall when all lit and the grid is plain), translate to
   the wall origin and draw the pattern for the full wall size (w = cols x tw, h = rows x th), then the DVD logo.
   Scrolling patterns are pre-rendered to an offscreen canvas and blitted with wrap-around at the scroll offset.
4. **Per lit piece overlays**: border stroke (colour bc, thickness bt) inset by bt/2, a 1 px rgba(255,255,255,.25)
   inner line, square corner marks (max(4, 2bt) px) in bc; labels centred in the piece, stacked from y = h/2 - 1.1 fs
   (fs = max(8, min(w/9, h/7))) in Barlow bold on rgba(0,0,0,.65) boxes: tile ID "W2 T05 [C5:R1] ½" (W# prefix only
   with several walls), pixel address "X: x0-x1, Y: y0-y1" (#ffe066), size "500×500mm" (#9fe).
5. **Tile position arrows** (option, any pattern): a pill (rgba(0,0,0,.65), font max(8, 0.11 x min(w,h))) at the
   piece's left (x + max(4, 6% w)): an up arrow + the row counted from the bottom (rows - row), a right arrow + the
   column counted from the left (col + 1). Vertical place: same height on every tile, just above the footer band
   (tile height - footer band - 3% - pill height); on any tile where it would overlap the label stack, the tileshade
   name/size boxes, the position label or (bottom row) the footer, move to the nearest clear height in that tile.
6. **tileshade footer and position label** drawn again above the borders (section 8).
7. **Data paths**, then **power runs** (section 10/11), then the technician for walls still building, then lock sparkles.

### 7.1 Image patterns and fit

Image fit modes: Stretch to wall, Fit inside wall, Fill wall (crops edges), Original size on canvas, Original size on wall. Stretch fills the wall; Fit inside keeps the aspect with black bars; Fill
crops edges; Original size on canvas draws the image 1:1 at the canvas origin (each wall shows the part under it);
Original size on wall draws it 1:1 at the wall's origin. Large walls render at a scale so the cached image stays under
25 MP. Scroll: directions ['diagonal ↘', 'diagonal ↗', 'horizontal →', 'vertical ↓']; speed = pspd x 0.2 x shorter side px/s; the image wraps around.

## 8. Test patterns

| Pattern | How to draw it |
|---|---|
| `tileshade` | Classic pixel map. Tiles alternate (checkerboard by grid cell) between Tile-shade colour and that colour mixed 50% with white. White 1.5 px+ lines corner to corner across the wall, a centre circle of radius h/4. Wall name (light box, dark text) and "W {w} X H {h}" (dark box, white text) in the middle, font f = max(12, min(h/22, w/30)). Position label "X {x},Y {y}" (canvas position of the first tile's top-left corner; first tile = top row, then leftmost) drawn as an overlay at that corner: white text on rgba(0,0,0,.62). Footer centred at the bottom: "{name} / Position: X {ox}, Y {oy} / {cols}.0 Columns X {rows}.0 Rows - {N} Cabinets Total ({n} half) / Resolution: {w} x {h} ( {w*h} ) / Aspect Ratio: {w/h}" in a light box, font max(10, min(h/50, tileH/10)) shrunk to fit 98% of the wall width; drawn again above the tile borders. |
| `tileshade-clean` | tileshade without the name, size and position boxes (footer kept). |
| `tileshade-cycle` | tileshade layout (lines with a dark casing so they show on white), but every tile cycles red #ff0000, green #00ff00, blue #0000ff. Tile (col,row) shows TCYC[(col + 2*row + k) mod 3] where k = floor(t / 2.5 s); neighbours (left/right/up/down) never match. In the last 1.5 s of each 2.5 s step the next colour slides in from the left with smoothstep easing and pushes the current one out (both move). Redraws every frame only while sliding. |
| `SMPTEbars` | Drawn SMPTE bars at 1920x1080, then fitted like an image: 7 bars #bfbfbf #bfbf00 #00bfbf #00bf00 #bf00bf #bf0000 #0000bf over the top 75%; a #0000bf strip 75-85%; bottom 15% in 7 blocks #00214c #fff #32006a #111 #000 #1d1d1d #111. |
| `ramp` | 16 vertical grey steps from 0 to 255, left to right. |
| `sweep` | Animated rainbow: horizontal gradient of 7 hues offset by 60° x t, with a white (top) to clear to dark (bottom) vertical overlay. Redraws every frame. |
| `white` | Full field #fff. |
| `red` | Full field #f00. |
| `green` | Full field #0f0. |
| `blue` | Full field #00f. |
| `black` | Full field #000. |
| `gray50` | Full field #808080. |
| `disguise test pattern 16:9` | Built-in 1920x1080 image (grid, circles, grey steps, colour references), embedded as base64 PNG. |
| `disguise test pattern 4:3` | Built-in 1024x768 version of the same image. |
| `branded test pattern 16:9` | Built-in 1920x1080 colour bars with a black centre box at (549,249) size 823x115 (image px). Centre box can hold text (BOXFONT, colour boxCol, never stretched) or an uploaded logo (aspect kept). |
| `branded test pattern 4:3` | Built-in 1024x768 version, centre box at (293,173) size 438x88. |
| `custom` | Uploaded image (PNG/SVG/JPG, kept up to 8192 px). Shows "Upload a test pattern image" until one is uploaded. |
| `pixel1` | Single-pixel checkerboard (every other pixel white). |
| `circles` | Dark #1c1c1c field, white 3 px lines: large centre circle (0.45 x shorter side), four small corner circles, centre cross and both diagonals. |
| `gradH` | Smooth black to white, left to right. |
| `gradV` | Smooth black to white, top to bottom. |
| `rgbramp` | Four horizontal bands, each black to red / green / blue / white, left to right. |
| `zone` | Zone plate: white concentric circles on black at radii sqrt(k) x max(6, R/45). |
| `cycle` | Full-field colour stepping every 1.5 s through #f00 #0f0 #00f #fff #000 #ff0 #0ff #f0f. Redraws only when the colour changes. |
| `cabinet IDs` | cidPat: #07090c background; each tile filled with its port colour (CIDCOL, 12 colours by port) and an edge of 2.5% of the tile; the ID in bold Barlow at 28% of the tile height (shrunk to 84% of its width) at 44% down, "C# R#" under it at 45% size; unwired tiles grey with a dash. With the data paths overlay off, a dashed line per port through (94% w, 84% h) of each tile and a P# dot on its first tile. The Tile IDs / address / mm labels and tile position arrows are skipped on this pattern. Not scrolled or cached. |

"Next pattern" (top bar) moves the selected wall to the next pattern in this list order, wrapping to the first, skipping
`custom` until an image is uploaded, and shows a toast "Test pattern: name (on wall)".

## 9. Engineering panel (formulas)

Per wall (s = sums over pieces): Tiles N (with "x full + y half", "z removed", cols x rows), Wall pixels (cols*tw x
rows*th and LED pixels in MP), Position, Wall size m and ft (cols*wmm x rows*hmm), Area (sum of piece m^2, m^2 and sq
ft = x10.7639), Weight (kg and lbs = x2.20462), Peak power (sum of piece max W, kW), Typical (40%), Current peak at the
circuit voltage (when power is on: kW*1000/V). With power: Tiles per circuit, Min. circuits if every circuit is full =
ceil(sum W / wmax / t), Power wiring summary, Circuits first ... last (count), Tiles without power, Over capacity. With
a processor: Tiles per port, Min. ports = ceil(LED px / (tw*th) / t), Data wiring summary, Data paths P1 to R1 ...,
Ports used (+ returns), Unwired tiles, Over capacity. Then Test pattern and Build start.

Entire canvas: Canvas, Aspect (reduced ratio and decimal), Canvas pixels, LED walls, Tiles, LED pixels, Area, Weight,
Peak power, Typical, Current peak; processor rows (Processor, Pixels per port with Hz/bit/ULL, Data ports used (primary
+ return = physical), Ports per processor or card, Processors or Sending cards needed = max(ceil(physical ports / ports
per unit), ceil(LED px / processor max px)), Over capacity); power rows (section 11).
"Export PDF" writes one PDF itself (a minimal PDF 1.4 writer: Helvetica/Helvetica-Bold with WinAnsi text, the master canvas as a DCT/JPEG image, vector rectangles and text for the labels). Page 1 (landscape, Letter in US/CA/MX and similar locales, otherwise A4): title, canvas size and date, then the master canvas (JPEG 92%) scaled to fit. Then portrait pages with the same tables as the engineering panel (Entire canvas, then each wall; 8.5 pt, label column 190 pt). Then, when data or power cables are wired, one page per label sheet at the label sheet size in mm, drawn exactly like the Print labels layout (flags, wall marks, fold line, rotated second panel). Saved as TileSmith-WxH-YYYYMMDD.pdf through dl(). There is no Export CSV button and no separate Spec sheet button.

## 10. LED processors and data wiring

| Processor | Brand | Ports | px/port | at Hz | bit | Max px | Scaling | Note |
|---|---|---|---|---|---|---|---|---|
| Brompton Tessera S4 | Brompton | 4 | 525000 | 60 | 8 |  | brompton | 4 × 1G outputs. |
| Brompton Tessera S8 | Brompton | 8 | 525000 | 60 | 8 | 4500000 | brompton | 8 × 1G outputs, 4.5 MP max. |
| Brompton Tessera SX40 + 4 XD | Brompton | 40 | 525000 | 60 | 8 | 8847360 | brompton | 4 × 10G to Tessera XD units, 10 ports each. 4096 × 2160 max. |
| NovaStar VX400 Pro | NovaStar | 4 | 650000 | 60 | 8 | 2600000 | novastar | 4 × 1G outputs, 2.6 MP max. |
| NovaStar VX1000 Pro | NovaStar | 10 | 650000 | 60 | 8 | 6500000 | novastar | 10 × 1G outputs, 6.5 MP max. |
| NovaStar VX2000 Pro | NovaStar | 20 | 650000 | 60 | 8 | 13000000 | novastar | 20 × 1G outputs, 13 MP max. |
| NovaStar MX40 Pro | NovaStar | 20 | 650000 | 60 | 8 | 9000000 | novastar | 20 × 1G outputs (40-port mode via 10G optical), 9 MP max. |
| NovaStar MCTRL300 | NovaStar | 2 | 650000 | 60 | 8 | 2304000 | novastar | 2 × 1G outputs, 650,000 px per port. One unit takes inputs up to 1920 × 1200 at 60 Hz. |
| NovaStar MCTRL600 | NovaStar | 4 | 650000 | 60 | 8 | 2304000 | novastar | 4 × 1G outputs, 650,000 px per port. One unit takes inputs up to 1920 × 1200 at 60 Hz. |
| NovaStar MCTRL660 | NovaStar | 4 | 650000 | 60 | 8 | 2304000 | novastar | 4 × 1G outputs, 650,000 px per port. One unit takes inputs up to 1920 × 1200 at 60 Hz. |
| NovaStar MCTRL660 PRO | NovaStar | 6 | 650000 | 60 | 8 | 2304000 | novastar | 6 × 1G outputs, 650,000 px per port, 1920 × 1200 at 60 Hz per unit. The 2 × 10G optical outputs each carry the same load as the 6 Ethernet ports, so they add no capacity. |
| NovaStar MCTRL700 | NovaStar | 6 | 650000 | 60 | 8 | 2304000 | novastar | 6 × 1G outputs, 650,000 px per port. One unit takes inputs up to 1920 × 1200 at 60 Hz. |
| NovaStar MCTRL R5 | NovaStar | 8 | 650000 | 60 | 8 | 4147200 | novastar, 10-bit 325000 | 8 × 1G outputs, up to 3840 × 1080 at 60 Hz, with image rotation. 325,000 px per port at 10-bit. The 2 × 10G optical outputs copy the Ethernet ports, so they add no capacity. |
| NovaStar MCTRL4K | NovaStar | 16 | 650000 | 60 | 8 | 8800000 | novastar, 10-bit 320000 | 16 × 1G outputs, 8.8 MP max from DP / HDMI (8.3 MP from DVI), max 7,680 px wide or high. 320,000 px per port at 10/12-bit; HDR, 3D or a 144 Hz input also halves it. OPT1 carries ports 1–8 and OPT2 ports 9–16 (OPT3/4 are copies), so the fibers add no capacity. |
| NovaStar MX20 | NovaStar | 6 | 659722 | 60 | 8 | 3900000 | novastar, 10-bit 329861 | COEX. 6 × 1G outputs, 3.9 MP max. 329,861 px per port at 10-bit (494,791 with A10s Pro cards). OPT1 carries ports 1–6 and OPT2 copies it. |
| NovaStar MX30 | NovaStar | 10 | 659722 | 60 | 8 | 6500000 | novastar, 10-bit 329861 | COEX. 10 × 1G outputs, 6.5 MP max, max 16,384 px wide or high. 329,861 px per port at 10-bit (494,791 with A10s / A8s Pro cards). OPT1 carries ports 1–10 and OPT2 copies it. |
| NovaStar NovaPro UHD Jr | NovaStar | 16 | 650000 | 60 | 8 | 10400000 | novastar, 10-bit 320000 | 16 × 1G outputs, 10.4 MP max, max 16,384 px wide or 8,192 high. 320,000 px per port at 10/12-bit. OPT1 carries ports 1–8 and OPT2 ports 9–16 (OPT3/4 are copies). |
| NovaStar VX16s | NovaStar | 16 | 650000 | 60 | 8 | 10400000 | novastar | 16 × 1G outputs, 10.4 MP max, max 16,384 px wide or 8,192 high. |
| NovaStar VX600 | NovaStar | 6 | 650000 | 60 | 8 | 3900000 | novastar | 6 × 1G outputs, 3.9 MP max, max 10,240 px wide or 8,192 high (the sheet gives no per-port figure; 3.9 MP over 6 ports is 650,000). The fiber outputs copy the Ethernet ports. |
| NovaStar VX600 Pro | NovaStar | 6 | 650000 | 60 | 8 | 3900000 | novastar | 6 × 1G outputs, 3.9 MP max, max 10,240 px wide or 8,192 high. The 2 × 10G optical outputs copy the Ethernet ports. |
| NovaStar H series: H_20xRJ45 card | NovaStar | 20 | 650000 | 60 | 8 | 13000000 | novastar, 10-bit 320000, per card | H series sending card (H2/H5/H9/H15/H20), 2 slots: 20 × 1G outputs, 13 MP per card, max 10,752 px wide or high, up to 144 Hz. 320,000 px per port at 10-bit. The engineering panel shows how many cards the canvas needs. |
| NovaStar H series: H_16xRJ45+2xFiber card | NovaStar | 16 | 650000 | 60 | 8 | 10400000 | novastar, 10-bit 320000, per card | H series sending card, 2 slots: 16 × 1G outputs, 10.4 MP per card, max 10,240 px wide or high, up to 144 Hz. 320,000 px per port at 10-bit. Fiber 1 copies Ethernet ports 1–8 and fiber 2 copies 9–16, so the fibers add no capacity. |
| NovaStar H series: H_4xFiber card | NovaStar | 32 | 650000 | 60 | 8 | 20800000 | novastar, 10-bit 320000, per card | H series sending card: 4 × 10G fiber outputs, each equal to 8 Ethernet ports through a fiber converter (32 ports), 20.8 MP per card, max 16,384 px wide or high, up to 144 Hz. Figures are for independent mode; copy and backup modes give less. 320,000 px per port at 10-bit. |
| HELIOS Jr | Megapixel HELIOS | 8 | 401000 | 60 | 12 |  | table | 8 × 1G outputs. 401,000 px per port at 12-bit 60 Hz (HELIOS User Guide, output port capacity table). |
| HELIOS 8K | Megapixel HELIOS | 72 | 401000 | 60 | 12 | 34000000 | table | 8 × 10G to distributors, 72 ports, 34 MP max. 401,000 px per 1G port at 12-bit 60 Hz. |
| ROE Evision eV4 | Evision | 40 | 655360 | 60 | 8 | 8300000 | linear | 4 × 10G to EVX10 distributors, 40 ports, 8.3 MP max. |
| Custom | Custom | 16 | 650000 | 60 | 8 |  | linear | Enter your processor's pixels per port and port count. |

Pixels per port for the chosen frame rate (fps) and bit depth (bpc): v = px x hz / fps, then: brompton: x 8/bpc, and
/2 with ULL; novastar: above 8-bit use px10 x hz / fps if given, else v/2; fixed (HELIOS): x bpc_spec/bpc only when bpc
> spec; linear: x bpc_spec/bpc. Floor the result. "Reset to spec" restores it; editing makes the note say it was edited.
Tiles per port t = floor(pixels per port / (tw x th)).

**Patterns**: None, Snake (turns back at the end of each line), Linear (each line starts from the same side), Manual.
8 start choices (corner/direction): Top-left/Horizontal, Top-right/Horizontal, Bottom-left/Horizontal, Bottom-right/Horizontal, Top-left/Vertical, Top-right/Vertical, Bottom-left/Vertical, Bottom-right/Vertical. The picker shows 8 small icons (green start, red end).

| Data wiring preference / (power) Wiring preference | Rule |
|---|---|
| Fewest ports / Fewest circuits | Each port gets a rectangle of tiles, sized to use as few ports as possible, and the pattern repeats inside every rectangle. |
| Whole rows or columns / Whole rows or columns | Each port takes complete rows (complete columns when vertical). If a port cannot drive a whole line, the line is split evenly between ports. |
| One continuous path / One continuous path | One path runs through the whole wall and is cut wherever a port is full, so a port can start partway along a line. |
| Horizontal / Horizontal | Each port takes a horizontal band: complete rows across the whole wall, as many as it can drive, whichever way the pattern runs. If a port cannot drive a whole row, each row is split evenly between ports. |
| Vertical / Vertical | Each port takes a vertical band: complete columns down the whole wall, as many as it can drive, whichever way the pattern runs. If a port cannot drive a whole column, each column is split evenly between ports. |

Fewest ports algorithm: lines run along the direction (L = cols for horizontal, rows for vertical; NL = number of lines).
Choose nx blocks along the lines and ny across: for each nx with ceil(L/nx) <= t, ny = ceil(NL / min(NL, floor(t /
ceil(L/nx)))); keep the smallest nx*ny, then (snake) prefer blocks of at least 2 lines, then the smallest nx. Split L
and NL into near-equal runs; each block is one port and the pattern repeats inside each block (block order: across
lines outer, along lines inner; mapped from the start corner). Whole rows: nx is forced to ceil(L / min(L, t)). One
continuous path: one path through the whole wall cut every t tiles. Horizontal / Vertical (bands of whole rows /
whole columns, whatever the direction): when the bands run along the lines (Horizontal with a horizontal pattern,
Vertical with a vertical one) it is exactly Whole rows or columns; when they cross the lines, ny = ceil(NL / min(NL, t))
(more than 1 only when a port cannot cover a whole line across), ba = ceil(NL / ny), nx = ceil(L / min(L, floor(t /
ba))); split L and NL into near-equal runs and order the blocks band by band (along the lines outer, across inner), with
the pattern repeating inside each block. Example: 10x5 wall, t = 20, vertical snake from the top-left, Horizontal: ports
of rows 1-2, rows 3-4 and row 5, each snaking down and up the columns of its band. The UI labels are "Data wiring
preference" (data) and "Wiring preference" (power), with a one-line explanation of the chosen rule underneath; the
engineering panel shows e.g. "Snake, top-left start, vertical, horizontal bands".

With removed tiles: chains drop removed cells, then neighbouring chains are joined while they still fit t (One
continuous path is re-cut every t). On a half-tile layout: one path over the unit grid in the chosen pattern; pieces
in the order the path first reaches them; a new port starts whenever adding the next piece would exceed the pixels per
port (counting each piece's own pixels). Ports are numbered P1, P2, ... across walls in wall order. A port is over
capacity when it has more than t tiles (plain) or more pixels than allowed (half tiles); it is then drawn dashed red.

**Manual wiring**: "Wire tiles" toggles the mode; click a tile to add it to the current port; or press and drag across
tiles (the pointer path is sampled every quarter tile so fast drags fill every tile crossed); dragging back onto the
previous tile removes the last one; pressing on the last tile continues the chain; a tile already in any chain is
skipped (a click shows "That tile is already wired."); a full port refuses tiles ("This port is full (t tiles). Click
New port to start the next one."). Buttons: New port, Undo (remove last tile), Clear. Status under the controls:
"Each port drives up to t tiles of this model." and "P1→R1: 15/17" (or "640k/650k px" on half-tile walls), unwired
count, "Adding to P3."

**Drawing data paths** (when Show data paths is on): for each port a line through tile centres (colour from
['#ff4d4d', '#4dff88', '#4da6ff', '#ffd24d', '#d24dff', '#4dfff0', '#ff944d', '#b0ff4d'] by port, red #ff3b3b dashed when over capacity), width max(2, min(tw,th)/30), with a filled arrow head at
each segment midpoint; a filled circle badge "P#" at the first tile and a dark rounded square "R#" at the last.

## 11. Power

Engineering > Power has four parts (2026-11-19 rethink): **Supply** (distro and house power cards), **Load** (Design load, Power
factor, Load circuits to 80%), **This wall** (Fed from, Cable, then the wiring settings) and **Show** (Show power runs, Colour by
phase, Rebalance after every change). Power is on while S.dists holds a supply (pdOn); "+ Add distro" / "+ Add house power"
add one. Each supply sets the circuit voltage cv (a multi-phase distro offers its line-to-neutral and line-to-line voltage) and
the breaker cb, capped at the connector rating; each wall picks its supply (pfeed) and its cable (pdt, only types that supply
has). pwC(w) returns the wall's {d supply, kind, D cable type, V, A, cw usable W}. Usable watts per circuit cw = V x A x
(0.8 if "Load circuits to 80%") x pf. Tiles per circuit t = floor(usable / wmax), capped by the power link limit if set.
Note text: "One 120 V 20 A circuit loaded to 80% supplies 1,920 W, enough for 12 tiles of ... at 150 W max each."
A tile that does not take a supply's voltage moves the supply to its other voltage (toast).

Circuits are numbered per wall segment (SEG): a wall starts new cables of its own type unless it shares the previous wall's
cable (pown off, same supply, type and voltage). With n circuits per cable (Socapex 6, L14-30 2, L21-30 3) circuit k is on
cable ceil(k/n) of its type as leg (k-1) mod n (legs 1-6 for Socapex, X,Y for L14-30, X,Y,Z for L21-30); labels
cable-circuit with no type letter: 1-1 ... 1-6, 2-1 ... or 1-X, 1-Y, 2-X ...
**House power** (type house, single phase, default 120 V 15 A, 12 Edison outlets): walls on it use powerCON to Edison (n = 1),
every circuit is its own plug. Outlets per house circuit (outl) and House breaker (hb): plug j is on house circuit
ceil(j / outl), its amps (W / (V x pf)) are summed per house circuit and compared with hb x (0.8 if derated); a house
breaker above 20 A is a warning. Engineering rows per house supply: Supply, House circuits, Load per house circuit, Outlets
used, Plugs, Over capacity. Labels: one pair per circuit, tags "1/2 EDISON PLUG END" (lines "Edison plug k[, wall circuit g]", "to <wall> <tile> (col, row)", tiles/watts/volts/breaker) and
"2/2 POWERCON END" ("<wall> <tile> POWER IN", "from Edison plug k", tiles/watts); the Power labels select is hidden. Power wiring works
like data wiring with the same patterns, corners and areas (Fewest circuits / Whole rows or columns / One continuous
path), capacity t, plus the power link limit; on half-tile layouts by each piece's own watts (circuit full when watts >
usable or tiles > link limit). Manual: Wire tiles, New circuit, Undo, Clear; "This circuit is full (12 tiles)."

Canvas rows: one "Circuit: <supply>, <cable>" row per supply and cable type ("120 V · 20 A · loaded to 80% = 1,920 W usable"),
Circuits used, Min. circuits if every circuit is full, <cable name> cables "2 (3 spare circuits)", Peak amps per phase, each cable "cable 1: A 32.0 · B 32.0 · C 32.0 A" (circuit amps = watts / V; circuits land A, B, C
repeating within a cable, so Socapex 1 and 4 on A, 2 and 5 on B, 3 and 6 on C; L14-30 X, Y on the two legs A, B; a 208 V circuit,
or 240 V on L14-30, is line to line and counts its full current on two phases: circuit i on PHN[i%3] and PHN[(i+1)%3]),
Peak amps per phase, all cables (with "busiest n% above average"), on 3-phase cables Balanced 3-phase current @V_LL (total watts /
(V_LL x sqrt 3); V_LL = 208 for 120 V, 400 for 230 V, the circuit voltage itself for 208 V), Over capacity, and one "Check power
settings" warning row for each problem from powWarn(): breaker above the connector's rating per circuit (Socapex 20 A, L14-30 and
L21-30 30 A, powerCON/Edison 20 A), a voltage the connector is not made for (Socapex 100-240, L14-30 110/120/240, L21-30
110/120/208, Edison 100-120), or an Edison wall circuit breaker above 20 A. The same warnings show in red under the circuit
note in the Power distribution settings.

**Power factor and design load**: usable watts per circuit = V x A x (0.8 if derated) x pf, so tiles per circuit drop
at pf < 1 (16 -> 15 for 120 W tiles at 120 V 20 A, pf 0.95). Every amp figure is W / (V x pf). The design load (pload: Max,
Typical ptyp % of max, or Measured pmeas W per tile capped at the tile's max) scales distro and leg totals only; circuits
are always checked at max watts. Engineering adds "Design load" and "Design load power".

**Distros** (submenu Engineering > Power > Distros, shown with Power distribution on): a list of distros (S.dists), each a
card with name, System, Rating per leg (A), Socapex leg map (6 letters A/B/C, default ABCABC), and the number of Socapex,
L21-30, L14-30 and Edison outputs, then leg bars (amber line at 80% of the rating when derated), Neutral, Imbalance and the
cable count, and Balance / Remove distro buttons; then Add distro, "Rebalance after every wiring change" (autoBal) and
"Colour power runs by phase on the canvas" (phaseView). Cables (all canvases; key "canvas:cable") are patched in S.pcab;
any cable without a valid output is patched automatically to the first free output of its type (distro order), and
cables that do not fit stay unpatched (Engineering warns "Cables not patched").
Phases: a circuit at the distro's line-to-line voltage (within 6%: 208 on 120/208, 220 on 127/220, 400 on 230/400, 240 on
120/240) takes two phases (p, p+1); otherwise one. Base phase of leg i: Socapex = map[i], L21-30 X/Y/Z = A/B/C, L14-30
X/Y = A/B, Edison = A; phase = (base + r) mod n, n = 3 (3-phase), 2 (split phase) or 1 (single phase, always A). Auto
patch gives Edison output j rotation (j-1) mod n.
Leg amps (legSum): phases at 0, -120 and +120 degrees (split phase 0 and 180). A line-to-neutral current I adds I at its
phase angle to its line and to the neutral; a line-to-line current I flows at the angle of V_p - V_q, added to line p
and subtracted from line q. Leg = |line phasor|, Neutral = |neutral phasor| (shown when circuits are line to neutral),
Imbalance = (max leg - mean) / mean, over capacity when a leg > rating x (0.8 if derated). Checks: 10 A on AB, BC and CA
-> 17.3 A per line; 24 / 18 / 12 A line to neutral -> neutral 10.4 A.
Balance (per distro, or Balance in the tray for all): only each cable's rotation r changes (outputs and circuit order
stay). Heaviest cable first, each takes the r that gives the lowest (highest leg, neutral, sum of squared legs), then
up to 6 passes of single-cable changes; the result is kept only if it is strictly better than before.
Engineering section "Power distribution" (after Entire canvas; also one section at the end of the PDF spec): Design load,
Design load power, Cables not patched, then per distro a heading row and System, Voltage warning when pvolt matches
neither voltage, Leg A/B/C "40.0 A · 40% of rating", Neutral, Imbalance, Outputs used, Cables, Over capacity.

**Power tray** (#ptray, under the viewport, shown while distros exist): bar with "Power tray", a green "every cable
patched" or red "n cables not patched" flag, a hint, Balance and Hide/Show; then one card per distro with a slot per
output of the current cable type (other output types summarised in one line) and a "Not patched" box. A slot holds the
cable chip (name, walls, amps, and one chip per circuit "1-3 C 14.0" bordered in its phase colour) and an x to unpatch.
Drag a chip onto a slot (HTML5 drag and drop) or click the chip, then the slot. Dropping on a taken slot swaps the two
cables; a slot of another type refuses with a message. While dragged or picked, the cable's tiles are highlighted on the
viewport (not on the output) and each slot shows what it would add per leg ("+A 12.0 B 12.0 A").

**Shared circuits** (Power wiring > Shared circuits): pick two or three runs ("Wall · run n") and Share one circuit. The
runs keep their own chains but take the first run's circuit number; later numbers close up, so circuits used drops.
The circuit is over capacity when the runs together exceed the usable watts; adding such a share is refused unless one
of the walls uses Manual power wiring. Labels show "1-3a", "1-3b" and "2fer on 1-3".

**Phase on canvas and labels**: with phaseView and a patched cable, a run is drawn in its phase colour (A #ffffff, B
#f59e0b, C #3b82f6; over capacity stays red) and its badge reads "1-3 C" (two letters for line to line). Circuit labels
add "<distro> phase C" to the cable line and print in the phase colour (A #222222, B #f59e0b, C #2563c9) with
"PHASE C · <wall>" as the flag text. Top bar "Phase" (shown while distros exist) toggles phaseView.

**Rigging** (submenu Engineering > Rigging; S.rigOn, default off): hang method = per-wall bmode ('Ground stack' | 'Flown from
motors' | 'Flown from truss'; the LED build treats both flown modes the same). Per wall: rbw (bumper width in tiles 1-4, default
2), rbkg (9), rpts (pickups per bumper 1-2, default 2), rwll (hoist rating kg, 500), tsec (truss lengths owned, "1, 2, 3"), tkgm
(truss kg/m, 8), thn (hoists on the truss, 3), tex (extra truss each side m, 0.5), rgbw (ground base width, 2), rgkg (14). S.rparts
= {tile model: [[part, qty, per (tile | column | row | wall | hoist point), kg each]]}. rigCalc(w): bumpers = ceil(cols / rbw);
motors: hoist points = bumpers x rpts; truss: span = wall width + 2 x tex from the longest sections that fit, hoists = thn,
slings and shackles per pickup; ground: bases = ceil(cols / rgbw). Parts counted ceil(qty x count); per hoist point parts are
skipped on a ground stack. Rows: hang method, bumpers/bases, truss, hoists, load per pickup, rigging weight, total weight,
load per hoist (total / hoists) with a warning over rwll, and "Planning figures only". The pull sheet gets a Rigging
department (parts per tile get the tile spare %).

**Show binder** (submenu Engineering > Show binder; top bar "Export binder" = exportPDF(true)): S.bShow, S.bVenue, S.bDate
(text), S.spT (spare tiles %, 0-100, default 5), S.spC (spare cables per length, 0-20, default 1). The binder PDF is: cover
(show name, venue, load-in, walls and tile counts, processor, power, page count), contents (section -> first page, filled in
last), the full raster page(s), one landscape page per wall (the wall cropped from the canvas drawn with data and power runs
forced on, then wallRows + cable home runs in two columns; "More figures for this wall are in the spec sheet." when they do
not fit), the pull sheet (pullItems(): Video = tiles per model, half tiles separately, spare = ceil(n x spT%), processors
needed; Data = etherCON per length (Cable lengths on) or home-run count "length not set", jumpers spare max(spC, spT%);
Power = cables per length or count, breakouts, jumpers, each distro; Labels = label sheets; columns NEED SPARE TOTAL and tick
boxes PULLED LOADED BACK; footer "Pulled by / Checked by / Returned by"), then the spec sheet and labels exactly as Export PDF.
File name "<show name>-binder-YYYYMMDD.pdf". Export PDF itself is unchanged. When any wall is wired (cidAny), a "Cabinet IDs"
section (cidPages) goes between the wall pages and the pull sheet.

**Cabinet IDs** (submenu Engineering > Cabinet IDs): S.cidFmt (CIDFMT: "Processor : port : tile (1:P2:07)" default | "Port -
tile (P12-07, as on the cable labels)"), S.cidStk (sticker per tile, default off). cabIds(plan) -> per wall, in portPlan order:
{wi, p (global port), s = floor((p-1)/pports)+1, ps = (p-1)%pports+1, k (1-based place on the port's cable), q (piece), id,
col/row (1-based, u/v on custom layouts), model, half}; id = `${s}:P${ps}:${kk}` or `P${p}-${kk}` (kk two digits). Same
processor split as cfgRows / the NovaStar config export. #cidStat: "Pick a processor..." | "Wire the data (Data wiring)..." |
"N tiles have an ID, on M ports." Buttons: cidShow (sets the selected wall's pattern to "cabinet IDs"; toast when nothing is
wired), cidPdf -> cidPDF(): "<show name or TileSmith>-cabinet-ids-YYYYMMDD.pdf" (Letter or A4 as Export PDF) = cidPages +
cidStickers when cidStk. cidPages: per wired wall a landscape map page ("<wall>: cabinet IDs", tiles, ports, processor, style;
tiles filled with the port's paper colour, port-colour edge, ID and C# R#, dashed cable per port, P# tag on its first tile),
then portrait list pages ("<wall>: cabinet IDs in data order"; two columns of ID, Proc., Port, Tile, Col., Row with a port
colour bar). cidStickers: one per tile on lblGeom() (no skip/copies), port colour bar at the left, the ID large, "<wall> · C#
R# · <model>" under it.

**Locations** (submenu Engineering > Locations; called zones in the code): S.zones = [{id, name (30 chars), c (#rrggbb)}] (max 20, list order = pull sheet
and binder order), per wall w.zone (0 = no zone), per distro d.zone, S.zProc (processor's zone), S.zHide (zones hidden in the
viewport only). zSan() drops unknown ids on load; a wall saved without zone opens as 0. New zones get the first unused colour
of ZCOL. Engineering "Locations" section (zTotals over every canvas): per zone a head row, LED walls (names), Tiles, Weight, Peak
power, Data ports (x2 with returns), Power circuits, Gear staged here; wall rows add "Location". Viewport (zDrawVp): 3 px outline
and a name tag in the zone colour; a hidden zone's walls are drawn black with a dashed grey edge and "<name> · hidden", and
hitWall skips them; the strip #zstrip above the viewport toggles S.zHide and has Show all. pullItems(zid) keeps only walls in
the zone (zid 0 = no zone) and the gear whose zone matches; processors and label sheets go with S.zProc; with Cable lengths a
power cable belongs to the wall it is measured to, otherwise to the first wall it feeds; jumpers and breakouts are counted per
zone. Pull sheet: a coloured zone bar (name, "N LED walls") before that zone's departments, zones in list order then No location.
Binder: a "Location map" page per canvas after the canvas pages (the raster darkened, each wall tinted and outlined in its zone
colour with "<wall> · <zone>", and a key with walls and gear per zone), contents list each zone under LED walls, and each wall
page has a zone tag top right.

**Cable lengths** (submenu Engineering > Cable lengths; S.cabOn, default off): per wall cdD / cdP (distance from processor /
distro, in S.cunit, 0-3000, defaults 25 / 15) and cin (Bottom left | Bottom centre | Bottom right | Top left | Top centre |
Top right); global cunit (m | ft; switching converts every wall's distances and swaps the default cable lists), cslack (% per
run, default 10), clenD / clenP (comma-separated lengths owned; defaults m: "1, 3, 5, 10, 15, 20, 30, 50" / "1, 3, 5, 10, 15,
25"; ft: "3, 10, 15, 25, 50, 75, 100, 150" / "5, 10, 25, 50, 75, 100"). Run = (distance + |x - entry x| + |y - entry y| to the
centre of the first tile, in m) x (1 + slack); returns R# start at the last tile; a multi-circuit cable is measured to the
farthest first tile of its circuits, Edison/powerCON per circuit. Cables: the shortest owned length that reaches; longer runs
take the longest length repeatedly plus the shortest that covers the rest ("50+20 m"). Engineering and the PDF get a "Cable
pack list" section (counts per length, jumpers = tiles - 1 per run, breakouts, total, joined runs, warn when a data run is
over 100 m) and per-wall "Cables arrive at" / "Data home runs" / "Power home runs" rows. The canvas shows each run's length
in a dark pill under its P# / power start badge.

**Fibre and breakout boxes** (inside Cable lengths): per wall wfib (Auto | Fibre | Copper, default Auto); global fibLim (copper
limit in S.cunit, 1-10000, default 90 m / 295 ft), fibBox (ports per breakout box 4 | 10 | 16, default 10), fibNat (processor
has fibre outputs, default off), fibTr (opticalCON DUO = 1 box per trunk | opticalCON QUAD = 2 boxes per trunk, default QUAD),
fibLen / fibTail (lengths owned; m "50, 100, 150, 300" / "1, 3, 5, 10", ft "150, 300, 500, 1000" / "3, 10, 15, 30"; the limit
and lists convert with the units). cFib(w, runs): far = longest copper data run (P# and R#, slack included); fibre when wfib =
Fibre, or Auto and far > fibLim. A fibre wall: ports = runs x (2 with returns), boxes = ceil(ports / fibBox), trunks =
ceil(boxes / 1 or 2), trunk length = processor distance x (1 + slack) picked from fibLen (cPick, joined when longer),
converters = boxes unless fibNat; each run becomes a copper tail = climb from the arrival point to its first tile x (1 + slack)
picked from fibTail. cabRuns returns runs with fib:1 and R.fib = [{wi, ports, boxes, trunks, m, cab}]. Pack list rows: Fibre
walls, Fibre breakout boxes, Fibre converters at the processor, Fibre trunks, Copper tails (box to tile), fibre in Cable on the
truck; the Over 100 m warning skips fibre walls. Wall rows: "Data to this wall" (Fibre with the reason or "set by hand",
Copper with the longest run), Breakout boxes, Fibre trunk, Copper tails from the box. Pull sheet Data: "Fibre breakout box, N
ports", "Fibre converter at the processor, N ports", "<trunk> fibre L", "etherCON tail L". Canvas pills show the tail length.

**Redundancy** (in LED processor; replaces the old global S.ret "Return lines" switch, which now only seeds old projects:
walls saved without wred get Loop, or None when S.ret was false). Per wall wred (Full | Backup processor | Loop | Spare
processor | None, default Loop) and wpri (1-99, default 1); global rlink (link / sync cable per backup unit, default on),
gOn (limit to gear on hand, default off), gProc / gTr / gBox (0-50). redPlan(plan): primaries P = all runs, main units =
max(ceil(P / pports), ceil(px / max px)) capped by gProc; P# p sits on main unit floor((p-1)/pports), port (p-1)%pports+1.
Fibre walls (cFib, Cable lengths on) first take their own trunks and boxes. Walls in order of wpri then wall order try
their method, then each weaker one: Loop needs spare main ports after the primaries (adds a main unit if one is on hand);
Backup processor / Full need a backup unit mirroring every main unit that holds the wall's P# (shared between walls), and
on fibre walls Full needs ceil(ports / fibBox) more boxes and their trunks for its own route, while Loop / Backup share the
main box (2 x ports). Spare processor needs one unit left over at the end (one covers the canvas), else None. The first
reason a wall failed is kept ("no processor left for a backup", "no spare processor ports left", ...). Loop R# lines go on
the main units after the primaries; backup R# on the mirror port. Engineering: "Redundancy" section (Processors, Not enough
processors, Fibre short, each wall "<got> (should get <want>: <reason>)", Stepped down, Port map rows per unit) and "Signal
path" svg (main x N box, backup x N box, link line, per wall: P# solid, fibre trunk pink dashes + box, R# dashed to main or
backup, Full on fibre via a second trunk + box, labels "R# loop" / "R# backup" / "R# own route" / "spare on truck" / "no
backup", "wanted ..." when stepped down). The PDF spec gets the Redundancy rows. Pull sheet Video: main processors, "Backup
<proc>", "Spare <proc> (not patched)", "Processor link / sync cable". Labels: R# processor end "<proc> return N" for Loop,
"Backup <proc> port N" for backup. wiring.json returnPorts = [{wall, redundancy}].

**Drawing power runs**: dashed line (dash 3w gap 2w, w = max(2, min(tw,th)/36)) through tile centres, colour from
['#ff9f1c', '#ffd166', '#06d6a0', '#4cc9f0', '#ef476f', '#c77dff'] by circuit; start badge = dark rounded box with a lightning-bolt icon and the circuit number k; small
square at the last tile. When a wall shows both data and power: data runs at (centre x - 0.2 tile w, centre y), power
at (centre x + 0.2 w, centre y + 0.2 h), and power is white on a black casing (2.4x width) with white badges;
over-capacity circuits stay red. With only one shown, it runs through the centres in its own colours.

## 12. Build animation (technician)

Per wall a simulation steps through the pieces in build order (cells in order of the start corner and Horizontal/
Vertical placement; for half-tile layouts, pieces sorted by their anchor cell's order then unit position). Phases per
tile: walkin 0.8 s, move 1.1 s, place 0.8 s, lock 0.6 s, walkout 1.5 s, hoist 1.6 s, scaled by Speed and a per-wall rate from [1, 0.88, 1.1, 0.94, 1.06, 0.84, 1.14, 0.97] (wall index); wall i waits i x 0.6 s before
starting. walkin: tech walks in from the wall edge carrying the tile; move: walks beside the slot; place: turns and
lifts the tile into place (tile scales from carry size to full); lock: tile flashes into place (a ring sparkle expands
from its centre) and the tile becomes lit; walkout: turns and walks off. Loop build restarts after Pause before restart.
The LED build submenu (Animation Options) has Start (clear all walls and play), Stop (stop and show every wall finished), Reset (clear all walls and wait) and Play/Pause (freeze and resume; the label follows S.play).

The technician is a flat vector person (hard hat, hi-vis vest with reflective band and logo text or image, skin tone,
hair colour, face photo optional, name tag) sized to fit inside the wall (size = min(2.4 x tile height, 42% of canvas
height, wall height/1.05, wall width/0.85)), clipped to the wall, standing beside the slot on the side he came from,
facing it, with both hands on the carried tile. The carried tile is a dark #1b2028 rectangle with a light frame,
amber corner marks and a black handle, at the piece's own size. Crew: ['Marcus', 'Elena', 'David', 'Chen', 'Priya', 'Malik'] by default, editable (name, skin,
hair, face photo), rotating so one person is not on two walls at once.

Character style (S.tstyle): Classic is the flat vector person above. Hand-drawn draws two Microsoft Rocketbox workers
(MIT; binary FBX, motion-captured walk and textures base64-encoded in app/crew/rb-assets.js) posed from their skeleton
for each build phase with the walk blended in, rendered by three.js r147 into an offscreen WebGL canvas through an ink
outline / flat-colour shader, then drawn onto the wall like the Classic tech. The files load only when Hand-drawn is
picked; without them or without WebGL the Classic tech is drawn and #crewNote says why. Backlit is a dark Canvas 2D
figure with a rim of wall light and bright reflective tape. Hat, vest, logo and name tags apply to every style.

Build mode (wall key bmode): Ground stack builds up from the floor from any start corner, row by row or column by
column. Flown from motors and Flown from truss hang the wall top row first, a row at a time: each row goes on at floor
level, then the wall is raised one row (bar on chain motors, or bumpers on a truss); only the left or right side of the
start corner is used. The same setting is the rigging hang method (Engineering > Rigging).

Tile faults (Animation Options > Tile faults; S.glOn, glType, glPick, glN, wall key glk): GLT = Dead tile, Flicker,
Colour channel out, Stuck pixels, Data chain break, Module out, Scrambled tile, Frozen tile, Calibration mismatch, Scan
line fault, Noise and sparkle, Power circuit tripped (GLD holds the cause shown under the menu), or Random mix. Faulty
tiles are picked by clicking in the viewport (Pick tiles) or rolled at random (glN tiles). Start tile faults (top bar
or the submenu) draws each fault over its tile on every output. Fix glitch sends two technicians: one behind the wall
appears in the gap when the faulty tile pops out; a reachable tile is handed down and the new one up, a higher one is
lowered on a rope; the other swaps it and carries the broken tile off; the faults stop when every tile is fixed.

## 13. DVD screensaver

A logo bounces inside each wall (or the whole canvas). Logo sprite height 200 px: TileSmith logo (5 squares mark +
"TILESMITH"), Text (bold, BOXFONT) or an uploaded image. With "Change color on each bounce" the sprite is recoloured
(source-in) to a random hue at least 70° from the previous one. Size = dvdSize% of the shorter side (max 95% of the
area). Speed = dvdSpeed x 0.25 x shorter side px/s. Start at a random point, angle 30-60°.

Corner hit chance: after every bounce, with probability dvdCorner% x 0.45, aim for a corner: unfold the
reflections and pick a direction that reaches a corner directly or via one side bounce (scored by fewest bounces, then
keeping direction, then the closest angle; angles kept between 2° and 88°). Otherwise keep the reflection angle and, if
the next wall hit would land within max(2, min(0.3 x logo size, 0.4 x free size)) of a corner, nudge the angle by up to
60° (kept between 8° and 82°) so it misses. At 0% it never hits a corner. The stats line counts bounces and corner hits.

**Perfect loop** (dvdLoop): over T seconds the logo crosses the free width 2m times and the free height 2n times (m, n
coprime, 1-240), so vx = 2 Wr m / T and vy = 2 Hr n / T, choosing m, n to keep the speed close to the set speed and the
angle between 25° and 65°. Position(t) = (tri(U0 + vx t, Wr), tri(V0 + vy t, Hr)) with tri(u, L) = L - |((u mod 2L) +
2L) mod 2L - L|. Start U0 = ((0.37 + 0.29 i) mod 1) x 2 Wr (i = wall index); V0 = Hr (U0/Wr)(n/m) for two corner hits
per loop, plus Hr/(2m) to avoid all corners. Bounce times are the crossings of whole multiples of Wr and Hr; colours
come from a seeded list (one per bounce, wrapping), so position and colour at T equal those at 0. "Export video" with DVD logo ticked
renders exactly one loop frame by frame at 60 fps (walls shown built, moving patterns and scroll held still) into
ffmpeg, file tilesmith-dvd-loop-Ns-*.ext.

## 14. Outputs

**NDI®** (desktop): sender name ndiName; frame rates 25 (25000/1000), 30 (30000/1000), 50 (50000/1000), 60 (60000/1000), 59.94 (60000/1001), 29.97 (30000/1001); frames are the canvas read back as RGBA and sent as RGBX
(FourCC 'RGBX' = 0x58424752, progressive, aspect = w/h, timecode synthesized). NDI runs on its own timer at the chosen
rate (frames go out evenly even when the window is hidden); with Save CPU, a frame is sent only when the canvas changed
(plus the 4/s safety net). One canvas readback per redraw is shared by NDI and recording. Status line: "● NDI® name ·
60 fps · 1920×1080 · per frame: render 0.4 ms, read 10.1 ms, send 0.0 ms · built-in NDI® runtime". The app keeps full
speed when hidden or minimised and blocks system app-suspension while NDI or recording runs. Runtime loading order:
TileSmith's own copy (resources/ndi), then NDI_RUNTIME_DIR_V* folders, then standard install paths.
Project licence: TileSmith is GPL-3.0-or-later, (c) 2026 Callum Davenport-Lambton; the animated technician's artwork,
character design, name and logo are reserved (all rights reserved, not GPL). An app built from this spec must not copy
that artwork or name: draw your own technician. Info dialog shows a Licence line stating this.

Licensing: show "NDI® is a registered trademark of Vizrt NDI AB" with links to https://ndi.video/ and
https://ndi.video/tools/, mark NDI with ® everywhere, ship the runtime's license notices (Info dialog "View NDI® license
notices"), do not bundle NDI® Tools, and follow the NDI® SDK License Agreement (https://ndi.link/ndisdk_license).

**Spout** (Windows desktop) and **Syphon** (Mac desktop) share the canvas with other programs on the same computer
through the GPU (no network, no compression). Submenu "Spout options" / "Syphon options" (web: "Spout / Syphon
options") under Output options, after NDI® options: sender/server name shName (default TileSmith), "Frame rate when
NDI® is off" shFps (60/50/30/25), "Save CPU while the picture is still" shIdle (default on), the explanation text, a
Start/Stop button (hidden when not built in), a status line and the credit line ("Spout by Lynn Jarvis ·
spout.zeal.co" / "Syphon by Tom Butterworth & Anton Marini · syphon.github.io"). One output timer paces everything
while NDI, Spout or Syphon runs: at the NDI rate while NDI runs, otherwise at shFps; each tick advances the animation
(unless recording), then sends to NDI and to Spout/Syphon from the same canvas read. With shIdle a frame goes out only
when the canvas changed (the 4/s safety-net redraw still refreshes it). Status line: "● Spout sender "TileSmith" · 60
fps · 1920×1080 · per frame: send 0.4 ms" (Syphon: "server", plus "no app receiving yet" until a client connects).
Spout: SpoutDX.dll (Spout SDK 2.007.017, MT build, no VC++ runtime) loaded with koffi; its C++ methods are called by
their exported decorated names with a 1 MB zeroed object from HeapAlloc: constructor, SetSenderFormat(28 =
DXGI_FORMAT_R8G8B8A8_UNORM, the canvas byte order), SetSenderName(name) (Spout appends _1, _2 when taken; GetName gives
the real one), SendImage(rgba, w, h, 0) each frame (size changes are handled by Spout), ReleaseSender on stop. Three
failed sends at the start (or 120 in a row later) stop it with "Spout could not send frames on <card>".
Graphics card (shGpu, Windows only): a Spout texture can only be opened by programs on the same graphics card, and on
laptops with two graphics chips the DirectX default is often the built-in chip while the receiver (e.g. Resolume) runs
on the fast one, which shows black. The list comes from GetNumAdapters/GetAdapterName ("Automatic" first). Before the
DirectX 11 device opens: a named card → SetAdapter(index); Automatic → SetPreferredAdapter(2 = high performance), or
when Windows has no preference the first card whose name is not Intel or Microsoft. Then OpenDirectX11(null) and
GetDX11Device must be non-null (else "Spout could not start DirectX 11 on the graphics card"). Changing the card while
running stops, closes the device (CloseDirectX11) and starts again. The status line ends with the card in use
(GetAdapter → GetAdapterName). Spout's own log goes to %APPDATA%/TileSmith/spout-log.txt (EnableSpoutLogFile) and
error messages name it. A saved card the PC does not have falls back to Automatic.
Syphon: node-syphon 1.5.5's syphon.node (N-API, universal) with Syphon.framework 5; new MetalServer(name), then
publishImageData(Uint8ClampedArray rgba, {x:0,y:0,width:w,height:h}, {width:w,height:h}, flipped=false) per frame,
only while server.hasClients (the first frame always goes out), dispose() on stop. Packaging: Windows
resources/spout/SpoutDX.dll + Spout-licence.txt; Mac Contents/Resources/syphon.node (rpath @loader_path/../Frameworks)
and Contents/Frameworks/Syphon.framework, licences in Resources/syphon. Info dialog: "Spout and Syphon" credits with
licences (Simplified BSD, BSD, MIT) and "View Spout / Syphon licences". On Android there is no Spout or Syphon; leave
this submenu out (or offer NDI only).

**Video export** (desktop, needs ffmpeg with the encoder): records at 60 fps: Blank intro seconds of empty canvas, the
live build, then Final hold; stream raw RGBA frames to ffmpeg `-f rawvideo -pix_fmt rgba -s WxH -framerate 60 -i
pipe:0 [format args] -an out`. Saved to Videos/TileSmith (Windows) or Movies/TileSmith (Mac) as
tilesmith-build-YYYYMMDD-HHMMSS.ext. Click again to cancel. Estimated length is shown.

| Format | Ext | ffmpeg encoder | ffmpeg output args | Note |
|---|---|---|---|---|
| HAP (.mov) | mov | hap | `-vf pad=ceil(iw/4)*4:ceil(ih/4)*4:0:0:black -c:v hap -format hap -compressor snappy -chunks 4` | For media servers (Resolume, disguise, Millumin). Large files, very light to play back. |
| H.264 (.mp4) | mp4 | libx264 | `-vf pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p -c:v libx264 -preset medium -crf 16 -profile:v high -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart` | Plays almost anywhere and makes small files. Colour detail is shared between pairs of pixels (4:2:0), so single-pixel colour lines soften. |
| H.265 / HEVC (.mp4) | mp4 | libx265 | `-vf pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p -c:v libx265 -preset medium -crf 18 -tag:v hvc1 -x265-params log-level=error -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart` | Smaller than H.264 at the same quality; needs a newer player. 4:2:0 colour like H.264. |
| ProRes 422 HQ (.mov) | mov | prores_ks | `-vf pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black,scale=out_color_matrix=bt709:out_range=tv,format=yuv422p10le -c:v prores_ks -profile:v 3 -vendor apl0 -colorspace bt709 -color_primaries bt709 -color_trc bt709` | Editing master for Premiere, Final Cut, Resolve. Large files, 10-bit 4:2:2. |
| ProRes 4444 (.mov) | mov | prores_ks | `-vf pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black,scale=out_color_matrix=bt709:out_range=tv,format=yuva444p10le -c:v prores_ks -profile:v 4444 -vendor apl0 -colorspace bt709 -color_primaries bt709 -color_trc bt709` | Highest-quality editing master with full colour on every pixel (4:4:4). Largest files. |

**Cable labels** (section "Label printing options", placed after Output options; the whole section is hidden unless
data wiring (a processor is chosen and at least one port exists) or power wiring (Power distribution on and at least one
circuit exists) is defined). Button "Print labels" (mobile: "Save label sheet"). One entry per cable with two labels
(end 1/2 and 2/2): data cable P<n> (processor port -> first tile, DATA IN), return cable R<n> when Return is on (last
tile DATA OUT -> processor return), power cable <n> (one pair per distribution cable: distro end and fan-out/wall end, circuits used, walls, watts) and power circuit <n-m> (distribution end -> first tile POWER IN; shows cable x of y, circuit or leg, voltage, breaker amps, tile count and watts), selected by lblPow; optional tile-to-tile jumper labels (P<n>-<i>, <circuit>-<i>). Each
label shows a small DATA/POWER + end caption, the cable name in large bold type, then three text lines (from/to with
wall name, tile id Tnn and col/row; tile count and pixels or watts). Settings lblWhat, lblPow, lblSize, lblW, lblH, lblCopies,
lblSkip, lblColor, lblJump, lblKeep (see the settings table). Sheet presets (mm): Avery 5160 66.675x25.4, 3x10, margins
4.76/12.7, gap 3.175; Avery 5163 101.6x50.8, 2x5, 3.97/12.7, gap 4.76; Avery L7160 63.5x38.1 on A4, 3x7, 7.21/15.15, gap
2.54; roll 62x29 and custom: one label per page. Output is an HTML page with one absolutely positioned div per label
(@page size = the sheet, margin 0). Desktop opens it in a new window and calls print(); mobile saves
tilesmith-cable-labels.html through the share sheet; if window.open is blocked an in-page iframe preview with Print/Close
is shown. Labels are wrap-around strips (stick to themselves around the cable): the text is printed on both halves (lblLayout
0 identical halves with flags at the outer ends, 1 second half rotated 180 degrees, 2 text in the centre with colour-only
end tails). Flags: primary green #22c55e (P), return red #e11d48 (R), power by phase (A #222, B #f59e0b, C #2563c9). Wall mark:
the wall's shadeC colour with the wall name (or W1, W2 in corner squares), shown when more than one wall exists (or always,
or as a background tint). Flag styles: full-height end blocks (flag 20% + wall 14% of a half), top/bottom bars (17% of the
height each), corner squares (36% of height). Black or white text is chosen by colour luminance. Extra preset: wrap-around
strip roll 100x30 mm; the default sheet is Avery 5163. With "keep together" the two ends never straddle a row on a sheet.
**PNG**: the full canvas as tilesmith-canvas.png. **PDF**: see the Export PDF paragraph in the top bar section.
**Layered SVG / PSD** (Export layers ▾): a dialog with SVG / PSD buttons and a checklist of layers, bottom to top Background, Test pattern,
Tile grid, Tile labels, Data paths, Power paths. Data and Power paths are disabled unless the canvas shows them (Data / Power on and a
processor / distribution set); unticked layers are remembered (lyrOff). One file per canvas, tilesmith-layers[-canvas].svg|psd. Each layer is
drawn by the normal canvas renderer with a layer filter (and an optional single-wall filter) on a clear canvas, so layers stack to exactly the
PNG. Test pattern = pattern, DVD sprite, tile faults, rigging; Tile grid = tile edges, inner line, corner squares, unbuilt outlines; Tile labels =
Tile IDs / addresses / mm sizes, tile position markers, the position label and footer of the shaded patterns. The technician is never drawn.
SVG: each layer is a top-level <g> with inkscape:groupmode="layer", inkscape:label and data-name (the translated layer name). Vector
layers come from a stand-in 2D context that turns fillRect/strokeRect/paths/arcs/roundRect/fillText into <rect>/<path>/<text> (rgba split
into colour + opacity, textBaseline converted to a y offset, text-anchor from textAlign); the test pattern is an <image> with a PNG data URL.
PSD: hand-written, version 1, RGB 8-bit, no colour mode data or image resources; one layer per leaf with channels -1 (alpha), 0, 1, 2 in
PackBits RLE, cropped to the pixels it draws, Pascal name (ASCII) plus a luni Unicode name; folders use lsct section dividers; then the
merged RGB image in RLE. Grouping (lyrGrp): A one layer per kind holding every wall (the default), B a folder per wall, C a folder per kind
with one layer per wall.
Port = "P1" or "P1 / R1" for the last tile; Tile = full | half top/bottom/left/right | full on its side; coordinates
are canvas px; MaxW/TypW per piece. **Resolume XML**: an Arena Advanced Output preset (XmlState > ScreenSetup >
screens > Screen > layers > Slice) whose composition size is the canvas, one virtual output screen the size of the
canvas, and one slice per wall or per tile (input rect = output rect = the tile/wall rectangle, 4x4 warper mesh),
saved as tilesmith-WxH.xml into Documents/Resolume Arena/Presets/Advanced Output when that folder exists.

## 15. Building it for Android (notes for the clone)

Note: the project already has a mobile build of this exact page (folder mobile/, Capacitor 8 for Android and iOS; see
BUILD-ANDROID.txt and BUILD-IOS.txt). In it, MOBILE = window.Capacitor.isNativePlatform(): files (PNG, PDF, XML, the label
sheet as HTML) go through a share sheet, Export video records H.264 MP4 in real time with MediaRecorder on the master
canvas (captureStream 60 fps, about 0.12 bits per pixel per frame, 4-40 Mbps) streamed to a file in 3 MB pieces, the
screen is kept awake while recording, NDI®/Spout/Syphon and the loop-video export are hidden, and two-finger pinch zooms
and pans the viewport. The folder android-aistudio/ holds the same app for Google AI Studio's Android builder: a Kotlin +
Jetpack Compose activity that shows this page in a WebView (WebViewAssetLoader, https://appassets.androidplatform.net)
and a JavaScript interface TileSmithAndroid (writeChunk, deleteFile, shareFile, openUrl, keepAwake) that
webview-bridge.js turns into the same window.TSM. A native Android clone, as described below, is the alternative.

- Use Kotlin + Jetpack Compose (or Views) with a single full-screen landscape layout: viewport in the centre,
  settings in a left drawer or side sheet (same sections and submenus), engineering in a right sheet or tab, top bar as
  a horizontally scrolling row of buttons. On phones, put Settings and Engineering behind toolbar buttons.
- Render the canvas into an offscreen `Bitmap` of cw x ch with `android.graphics.Canvas` (same drawing rules as the
  Canvas 2D code), and draw it scaled in the viewport. Use a render loop tied to `Choreographer`, redrawing only when
  something moves (section 7).
- Gestures: tap = click; one-finger drag on a wall = move it (or edit, in editing modes); one-finger drag on empty
  space or two-finger drag = pan; pinch = zoom (same limits as the wheel); long-press could open a tile's details.
- NDI® on Android: the NDI® SDK includes Android libraries (check the current SDK and its license). Send RGBX/RGBA
  frames from the canvas bitmap on a background thread at the chosen rate; hold a Wi-Fi multicast lock for discovery,
  run output in a foreground service with a notification, and keep the screen on while sending.
- Video export on Android: H.264 / H.265 MP4 with `MediaCodec` + `MediaMuxer` (feed frames via an input `Surface` or
  YUV conversion), 60 fps, BT.709 tags. HAP and ProRes need an FFmpeg build; treat them as optional.
- Save PNG/PDF/XML/MP4 with the Storage Access Framework or MediaStore (Pictures, Movies, Documents). Persist state as
  the same JSON (section 4) in app storage, so files can move between desktop and Android.
- Keep all formulas, labels, colours, defaults and limits from this document so plans match the desktop app.
- Keep the credits and NDI® notices from the Info dialog: "Concept & development: Callum Davenport-Lambton", the contact
  and Ko-fi links, and the NDI® trademark and license text. Spout and Syphon are Windows/Mac only; leave them out on
  Android (the shName/shFps/shIdle keys can stay in the saved JSON so files move between platforms).

## 16. Checks a clone should pass

- tileshade-cycle: for every wall up to 40x40 and every step, no tile shares a colour with the tile left, right, above
  or below it.
- Auto data and power wiring (all 16 signal-flow choices = 8 start corner/direction x Snake/Linear, picked from a 2 x 8 icon grid styled like Brompton's mapping picker; x 3 areas, any size, with removed tiles or half tiles):
  every tile appears in exactly one chain, no chain is over capacity, and One continuous path uses ceil(tiles / t)
  chains.
- Engineering for a 6x4 Unilumin UpadIV 2.6 wall: 24 tiles, 1152 x 768 px (884,736 LED px), 6.00 m^2, 151.2 kg,
  2.88 kW peak, 1.15 kW typical; at 120 V 20 A loaded to 80%: 1,920 W usable, 16 tiles per circuit.
- NovaStar VX1000 Pro at 60 Hz 8-bit: 650,000 px per port; at 10-bit 325,000; Brompton S8 at 50 Hz 10-bit: 504,000.
- Perfect-loop DVD: position and colour at time T equal those at time 0, and there are exactly 2 (or 0) corner hits
  per loop.
