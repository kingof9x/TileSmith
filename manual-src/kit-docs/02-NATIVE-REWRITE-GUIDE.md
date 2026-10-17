# Route B: rebuilding TileSmith natively in Kotlin + Compose (AI Studio)

Use this route if you want TileSmith as native Compose code instead of the original page in a WebView (route A). It is a
big job. The original is {{JS_LINES}} lines of JavaScript (`source/readable/app.js`), with about 170 functions, 50
tile presets, 12 processors and 25 test patterns. AI Studio will not rebuild that in one prompt. Work through the 12
prompts below in order, in one AI Studio project, and check each step against the screenshots before going on.

**The prompts are ready to paste in `route-b-prompts/` (B01 to B12).** Each one already contains the spec sections and
the original code it needs, and lists the screenshots to attach; see `route-b-prompts/B00-HOW-TO-USE.md`. This guide
explains the plan behind them and has a shorter version of each prompt, for reference.

Everything the rewrite needs is in this kit:

- `TileSmith-App-Spec.md`: every setting with its default and limits, the presets, the processors, the formulas and
  algorithms, the colours, the export formats, and checks with expected numbers (section 16).
- `04-ANIMATIONS.md`: the build animation, technician, DVD screensaver and moving patterns, with timings and formulas.
- `03-SCREENS.md` and `screenshots/`: every screen, panel, pattern, wiring preference and animation frame.
- `source/readable/app.js` with `FUNCTIONS.md`: the original code. When a prompt names a function, paste that
  function (line numbers below) so AI Studio ports it instead of guessing.
- `TileSmith-Mobile-Manual.pdf`: how the finished app behaves, from the user's side.

If AI Studio accepts a text file attached to a prompt, attach `source/readable/app.js` and `TileSmith-App-Spec.md` to
prompt 1 and say "use these as the reference for every later step".

## Architecture to ask for

| TileSmith (JavaScript) | Native Android (Kotlin) |
|---|---|
| Global settings object `S` and the `walls` array (spec section 4) | `data class Settings` and `data class Wall` with the same field names and defaults; a `TileSmithViewModel` holds `StateFlow<AppState>` |
| Saved as JSON in localStorage (`tilesmith-state-v1`) | The same JSON (`{sv:23,S:{...},walls:[...],cur,crew,logo,dvd}`) in `filesDir/state.json`, written 400 ms after a change, so files can move between desktop and Android |
| Master canvas `M` (cw × ch px) drawn by `render()` with Canvas 2D | An `android.graphics.Bitmap` of cw × ch drawn with `android.graphics.Canvas` by a `MasterRenderer` that ports `render()` and its helpers one to one |
| Viewport `vp` drawn by `vpDraw()` (zoom `V.z`, pan `V.x/V.y`) | A Compose `Canvas` that draws the bitmap with the zoom and pan, plus outlines and editing marks |
| `requestAnimationFrame(loop)` → `tick(now)` at up to 60 fps, redraw only when something moves, else 4 times a second | `LaunchedEffect` + `withFrameNanos` calling `tick(nowMs)`, with the same redraw rules (spec section 7) |
| Left panel (`<details>` sections) | `LazyColumn` of collapsible sections and submenus; labels exactly as in the screenshots |
| Top bar | A horizontally scrolling `Row` of buttons |
| Right panel (engineering) | `LazyColumn` of two-column tables |
| Mobile bridge (`window.TSM`) | Direct Kotlin: FileProvider + `ACTION_SEND` share sheet, `MediaCodec` + `MediaMuxer` for MP4, `FLAG_KEEP_SCREEN_ON` |
| Phone (narrower than 900 px): panels stack | Same: one scrolling column (settings, top bar + viewport, engineering) |

**Canvas 2D to android.graphics.** `fillRect` → `drawRect` with a FILL paint · `strokeRect`/`lineWidth` → STROKE
paint with `strokeWidth` · `setLineDash([a,b])` → `DashPathEffect(floatArrayOf(a,b),0f)` · `createLinearGradient` +
`addColorStop` → `LinearGradient` shader · `arc`/`ellipse` → `drawCircle`/`drawOval`/`drawArc` · `roundRect` →
`drawRoundRect` or `Path.addRoundRect` · `clip()` → `clipPath` · `save`/`restore`/`translate`/`scale`/`rotate` →
the same · `globalCompositeOperation='source-in'` → `PorterDuffXfermode(SRC_IN)` on a layer · `fillText` → `drawText`
(`textBaseline='middle'` means y + (−ascent − descent)/2) · `measureText` → `Paint.measureText` · `font='700 Npx
Barlow'` → bold `Typeface`, `textSize = N` · `drawImage(img,x,y,w,h)` → `drawBitmap(bmp, null, RectF(...), paint)`
with filtering · `createPattern(PXC,'repeat')` → `BitmapShader(REPEAT)` · `shadowBlur`/`shadowColor` →
`setShadowLayer` · `lineJoin='round'` → `Paint.Join.ROUND`. All sizes are in canvas pixels, so draw at 1:1 on the
bitmap.

## Key functions to port (line numbers in `source/readable/app.js`)

| Area | Functions |
|---|---|
| Frame loop and timing | `loop` {{L:loop}}, `tick` {{L:tick}}, `animNow` {{L:animNow}}, `busyNow` {{L:busyNow}} |
| Canvas | `render` {{L:render}}, `pat` {{L:pat}}, `vpDraw` {{L:vpDraw}}, `fit` {{L:fit}}, `fitZ` {{L:fitZ}} |
| Wall shapes | `pieces` {{L:pieces}}, `unitG` {{L:unitG}}, `layDefault` {{L:layDefault}}, `layPieces` {{L:layPieces}}, `halfAct` {{L:halfAct}}, `halfDo` {{L:halfDo}}, `goneDrag` {{L:goneDrag}}, `restoreAll` {{L:restoreAll}} |
| Wiring | `autoChains` {{L:autoChains}}, `blockGrid` {{L:blockGrid}}, `blockPath` {{L:blockPath}}, `splitN` {{L:splitN}}, `keepTiles` {{L:keepTiles}}, `layChains` {{L:layChains}}, `portPlan` {{L:portPlan}}, `powChains` {{L:powChains}}, `powerPlan` {{L:powerPlan}}, `manChains` {{L:manChains}} |
| Build animation | `mkSim` {{L:mkSim}}, `reset` {{L:reset}}, `showAll` {{L:showAll}}, `stepSim` {{L:stepSim}}, `step` {{L:step}}, `pickCrew` {{L:pickCrew}}, `techBox` {{L:techBox}}, `drawWallTech` {{L:drawWallTech}}, `worker` {{L:worker}}, `cab` {{L:cab}} |
| DVD screensaver | `dvdStep` {{L:dvdStep}}, `dvdRun` {{L:dvdRun}}, `dvdNewState` {{L:dvdNewState}}, `dvdDecide` {{L:dvdDecide}}, `dvdAim` {{L:dvdAim}}, `dvdAvoid` {{L:dvdAvoid}}, `dvdBounce` {{L:dvdBounce}}, `dvdLoopPlan` {{L:dvdLoopPlan}}, `dvdLoopAt` {{L:dvdLoopAt}}, `dvdSpr` {{L:dvdSpr}}, `dvdDraw` {{L:dvdDraw}} |
| Engineering | `wst` {{L:wst}}, `specPx` {{L:specPx}}, `applySpec` {{L:applySpec}}, `tpp` {{L:tpp}}, `powRowsCanvas` {{L:powRowsCanvas}}, `info` {{L:info}} |
| Exports | `csv` {{L:csv}}, `spec` {{L:spec}}, `resolumeXML` {{L:resolumeXML}}, `recStartMR` {{L:recStartMR}} |
| Settings | `saveNow` {{L:saveNow}}, `loadState` {{L:loadState}}, `storeWall` {{L:storeWall}}, `loadWall` {{L:loadWall}}, `addWall` {{L:addWall}}, `fitCanvas` {{L:fitCanvas}} |


## The prompts

Paste one prompt at a time. Under each prompt, **Attach** lists the screenshots to attach and **Paste** lists the
spec sections or code to paste under the prompt text. After each step, compare the emulator with the attached
screenshots and ask AI Studio to fix any difference before going on.

### Prompt 1: app shell, theme, layout and settings model
> Build "TileSmith", an LED video wall pixel-mapping and test-pattern app for LED technicians, in Kotlin + Jetpack
> Compose (single activity, ViewModel, data classes). This first step is the shell. Dark theme by default with the
> colours bg #0D1217, panel #151C23, lines #27323C, text #E6EDF3, muted #8A9AA8, accent #22D3EE, amber #FFB300; a light
> theme with bg #F1F3F5, panel #FFFFFF, lines #CFD5DB, text #16202A, muted #5D6B78, accent #0B8AA6, amber #C47A00,
> following the system setting. Tablet layout (900 dp or wider): a 350 dp settings panel on the left, a 310 dp
> engineering panel on the right, and between them a top bar of buttons (scrolls sideways) above a viewport. Below
> 900 dp, put everything in one scrolling column: settings, then the top bar and a viewport 70% of the screen tall,
> then engineering. The left panel starts with "TileSmith" and the version "v{{VERSION}}" in amber, and the subtitle
> "LED Wall Pixel Map & Test Pattern Generator". Then the collapsible sections and submenus, in this order and with
> these labels: Canvas (LED walls, Tile model, Size of LED Wall, Wall position), Test pattern (Tile borders &
> overlays), Engineering (LED processor › Data wiring, Power › Power wiring), Animation Options (DVD screensaver, Build
> options › Technician, Video export). Create every control shown in the attached screenshots with the defaults and
> limits from the pasted settings tables, stored in data classes Settings and Wall with these exact field names.
> Save all settings as JSON in filesDir/state.json, 400 ms after any change, and load them at start. The viewport and
> engineering panel can be placeholders for now. Top bar buttons: ⓘ Info, Play / Pause, Start build, Instant skip,
> Reset fit, Next pattern, Export PNG, Export CSV, Spec sheet, Resolume XML ▾, Export video.

**Attach:** `tablet/t01-first-launch.png`, `phone/p01…p0n-phone-portrait.png`, `panels/ui-header.png`,
`panels/ui-canvas.png`, `panels/ui-led-walls.png`, `panels/ui-tile-model.png`, `panels/ui-size.png`,
`panels/ui-position.png`, `panels/ui-test-pattern.png`, `panels/ui-borders.png`,
`panels/ui-engineering-section.png`, `panels/ui-animation-section.png`, `panels/ui-top-bar.png`.
**Paste:** spec sections 3 (screen layout) and 4 (data model, both settings tables).

### Prompt 2: master canvas, tiles, borders, overlays, tileshade, viewport
> Add the master canvas: an android.graphics.Bitmap of cw × ch pixels (default 1920 × 1080), redrawn by a
> MasterRenderer that follows the pasted rendering rules exactly (background #050608, unlit tile outlines, pattern
> clipped to lit tiles, per-tile border, inner line, corner marks, labels, tile position arrows). Implement the
> tileshade pattern exactly as described, including the footer and position label. Draw the bitmap in the viewport
> with zoom and pan: a drop shadow, a cyan #22D3EE outline around the canvas, an amber outline around each wall.
> Reset fit fits the canvas with a margin of min(60 px, 10% of the viewport). Pinch zooms around the fingers (max
> 500%), two fingers pan, one finger on empty space pans. Port the attached JavaScript functions one to one.

**Attach:** `patterns/cv-pattern-01-tileshade.png`, `patterns/cv-overlays-all.png`, `tablet/t09-overlays.png`.
**Paste:** spec sections 3.3 and 7; code: `render` (first part), `pat` (the tileshade branch), `vpDraw`, `fit`, `fitZ`.

### Prompt 3: all 25 test patterns, image fit, scroll, centre box, uploads
> Implement every test pattern in the pasted table, drawn exactly as the attached images show; the four built-in
> pictures are attached as files (put them in res/drawable-nodpi). Add Image fit (5 modes), Scroll (4 directions,
> speed = Scroll speed × 0.2 × the wall's shorter side px/s, wrapping around), the centre box of the branded patterns
> (text or logo), and uploads with the Android photo picker (kept up to 8192 px). Next pattern moves the selected wall
> to the next pattern in this order and shows a toast "Test pattern: <name> (<wall>)".

**Attach:** `patterns/cv-patterns-all.png`, every `patterns/cv-pattern-NN-*.png`, the four files in
`source/readable/images/`.
**Paste:** spec sections 7.1 and 8; code: `pat`, `patImg`, `scrollOff`, `blitWrap`, `tcycTile`, `tcycFill`, `drawBars`.

### Prompt 4: tile models, canvas presets, walls, dragging and snapping
> Add the tile model presets (grouped by manufacturer; editing any tile field switches to Custom), the canvas presets
> and Fit canvas to walls, wall size quick buttons, wall position buttons, and several walls: Add wall, Duplicate,
> Remove, a wall list where the selected wall has an amber border. In the viewport a one-finger drag on a wall moves
> it; walls snap to canvas edges and other walls within 10 screen px (magenta dashed guides), then overlapping walls
> are pushed apart to keep a 2 px gap. Tap a wall to select it.

**Attach:** `tablet/t02-two-walls-data.png`, `tablet/t03-led-walls.png`, `tablet/t04-wall-position.png`,
`shapes/cv-three-walls.png`.
**Paste:** spec sections 4.2 (the paragraph after the table) and 5 (the whole presets table).

### Prompt 5: engineering panel
> Fill the engineering panel: an "Entire canvas" section, then one section per wall, as two-column tables with the
> pasted rows and formulas. Check: a 6 × 4 Unilumin UpadIV 2.6 wall must show 24 tiles, 1152 × 768 px (884,736 LED px),
> 6.00 m², 151.2 kg, 2.88 kW peak, 1.15 kW typical.

**Attach:** `panels/ui-engineering-panel.png`. **Paste:** spec sections 9 and 16; code: `wst`, `info`.

### Prompt 6: LED processors and data wiring
> Add the LED processor list with frame rate, bit depth, ULL, pixels per port (with Reset to spec), ports per
> processor, returns, and Show data paths. Add data wiring: None, Snake, Linear, Manual; 8 start icons; the five Data
> wiring preferences with their one-line explanations. Port autoChains, blockGrid, blockPath and splitN exactly; every
> tile must be in exactly one chain and no chain may be over capacity. Draw the data paths as described (colours by
> port, arrow heads, P# and R# badges, dashed red when over capacity). Manual wiring: Wire tiles / New port / Undo /
> Clear, tap or drag across tiles, with the messages given.

**Attach:** `wiring/cv-data-wiring-all.png`, `wiring/cv-data-snake-8-starts.png`, `wiring/cv-data-linear-8-starts.png`,
`panels/ui-led-processor.png`, `panels/ui-data-wiring.png`, `tablet/t05-data-wiring.png`,
`tablet/t06-manual-data-wiring.png`.
**Paste:** spec section 10; code: `specPx`, `applySpec`, `tpp`, `autoChains`, `blockGrid`, `blockPath`, `splitN`, `keepTiles`, `portPlan`,
and the data-path drawing part of `render`.

### Prompt 7: power and power wiring
> Add Power distribution (Socapex, 6 circuits per cable), voltage, breaker, load to 80%, power link limit and Show
> power runs, the power rows of the engineering panel, and power wiring with the same patterns, starts and five Wiring
> preferences as data wiring. Draw power runs as described; when a wall shows data and power, offset them and draw
> power white on a black casing with lightning-bolt badges.

**Attach:** `wiring/cv-power-wiring-all.png`, `wiring/cv-data-and-power.png`, `panels/ui-power.png`,
`panels/ui-power-wiring.png`, `tablet/t07-power-and-data.png`, `tablet/t08-power-wiring.png`.
**Paste:** spec section 11; code: `powChains`, `powerPlan`, `powRowsCanvas`, `bolt`, the power drawing part of `render`.

### Prompt 8: wall shapes (removed tiles, half tiles)
> Add Remove tiles / Restore all tiles (Size of LED Wall) and, for models with a half version, Mark half tiles /
> Clear half tiles (Tile model), working exactly as the pasted rules: walls become a list of pieces; tap or drag edits;
> empty spots show a red dashed outline with an X in the viewport only. Wiring, power, engineering and the build follow
> the pieces.

**Attach:** `shapes/cv-half-tiles.png`, `shapes/cv-removed-tiles.png`, `tablet/t10-remove-tiles.png`,
`tablet/t11-half-tiles.png`, `panels/ui-tile-model-half.png`.
**Paste:** spec section 6; code: `unitG`, `layDefault`, `layPieces`, `pieces`, `halfAct`, `halfDo`, `goneDrag`,
`restoreAll`, `layChains`.

### Prompt 9: the build animation and the technician
> Add the build animation from the pasted animation guide. A per-wall state machine steps through the tiles: walkin
> 0.8 s, move 1.1 s, place 0.8 s, lock 0.6 s, walkout 1.5 s, times Speed and the wall's pace. Port drawWallTech,
> worker (the technician drawing: hard hat, hi-vis vest with logo, name tag, arms reaching the carried tile, walk cycle,
> turning), cab (the carried tile) and the lock sparkle one to one, so the frames match the attached strips. Add the
> crew editor (name, skin tone, hair colour, face photo, rotation across walls), hard hat and vest colours, vest logo
> text or image, and Build options (Speed, Loop build, Pause before restart). Start build, Play / Pause and Instant
> skip work as described.

**Attach:** every file in `animations/` whose name starts with `anim-build`, `anim-tech` or `anim-multiwall`, plus
`anim-carried-tile.png`, `tablet/t13-build-in-progress.png` and `panels/ui-technician.png`.
**Paste:** `04-ANIMATIONS.md` sections 1 to 4; code: `mkSim`, `reset`, `showAll`, `stepSim`, `step`, `pickCrew`,
`techBox`, `drawWallTech`, `worker`, `cab` and the sparkle loop at the end of `render`.

### Prompt 10: DVD screensaver and moving patterns
> Add the DVD screensaver and the time-based patterns exactly as in the pasted guide: free bounce with the corner-hit
> chance, recolouring at every bounce, Perfect loop mode; sweep, tileshade-cycle (slide with smoothstep) and cycle.
> Redraw every frame only while something moves.

**Attach:** `animations/anim-dvd*.png|gif`, `anim-tileshade-cycle*`, `anim-cycle-strip.png`, `anim-sweep*`,
`anim-scroll*`, `panels/ui-dvd.png`, `tablet/t12-dvd.png`.
**Paste:** `04-ANIMATIONS.md` sections 5 to 7 and spec section 13; code: the `dvd…` functions.

### Prompt 11: exports and sharing
> Add Export PNG (the master bitmap as tilesmith-canvas.png), Export CSV (patching.csv, columns as pasted), Spec sheet
> (tilesmith-spec.html with the same tables as the engineering panel), Resolume XML (One slice per LED wall / One slice
> per tile, tilesmith-WxH.xml). Write the file to cacheDir/exports and open the Android share sheet through a
> FileProvider; show the toast "Saved <name>." or "Not saved: <name>". Export video: record the master canvas at
> 60 fps into an H.264 MP4 (MediaCodec input Surface + MediaMuxer, bitrate min(40 Mbps, max(4 Mbps, W × H × 60 ×
> 0.12))), phases Blank intro, live build, Final hold, status "● REC blank 3s / building / hold 5s", keep the screen
> on, then share tilesmith-build-YYYYMMDD-HHMMSS.mp4. Pressing Export video again cancels.

**Attach:** `tablet/t14-recording.png`, `tablet/t15-recording-saved.png`, `tablet/t17-resolume-menu.png`,
`tablet/t19-saved-toast.png`, `tablet/t20-spec-sheet.png`, `panels/ui-video-export.png`.
**Paste:** spec section 14 (PNG, CSV, Resolume XML parts) and the mobile notes in section 15; code: `csv`, `spec`,
`resolumeXML`.

### Prompt 12: info dialog and finishing
> Add the ⓘ Info dialog exactly as attached (credits "Concept & development: Callum Davenport-Lambton", contact
> tilesmithapp@gmail.com, Ko-fi https://ko-fi.com/kingof9x, Reset saved settings with a confirmation). Then compare
> every screen with the attached screenshots and fix the differences: labels, order, spacing, colours, and what the
> canvas draws.

**Attach:** `tablet/t16-info-dialog.png`, `panels/ui-info-dialog.png`, then any screenshots that still differ.

## Checking the rewrite

Use `TileSmith-App-Spec.md` section 16 and these pictures:

- Patterns: put a 6 × 4 UpadIV wall on a 1152 × 768 canvas with the overlays off, and compare each pattern with
  `patterns/cv-pattern-NN-*.png`.
- Wiring: use a 10 × 5 wall, NovaStar VX1000 Pro, Snake from the top left, horizontal. Each preference must match
  `wiring/cv-data-wiring-*.png`. Power at 120 V 20 A 80% must match `wiring/cv-power-wiring-*.png`.
- Build: use a 6 × 3 wall on a 1152 × 576 canvas at Speed 1. The frames at 0.2 s steps must match
  `animations/anim-build-strip.png`.
