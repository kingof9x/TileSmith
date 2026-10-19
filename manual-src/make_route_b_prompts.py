"""Route B (native Kotlin + Compose rewrite) prompts for Google AI Studio, fully assembled: each file holds one prompt
with its instructions, the spec sections and the original JavaScript it needs already pasted in, plus the list of
screenshots to attach. Written into <kit>/route-b-prompts by make_aistudio_kit.py (it needs the built kit: the filled
docs and source/readable/app.js).

  python3 make_route_b_prompts.py <kit folder>
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).parent
TOOLS = HERE / 'tools'

RULES = """HOW TO WORK (applies to every step)
- You are rebuilding TileSmith, an existing and finished app, natively for Android in Kotlin + Jetpack Compose: one
  activity, a ViewModel and data classes, single module. This is step {n} of 12. Keep everything built in earlier steps
  working and change only what this step needs.
- Match the attached screenshots, not default Material styling: a compact UI with about 13 sp body text, small
  controls and the TileSmith colours (1 CSS px = 1 dp).
- Port the JavaScript under REFERENCE CODE faithfully. Keep the same field names, defaults, limits, formulas, colours,
  texts and drawing order. Do not simplify, skip or invent behaviour. When the code and a screenshot disagree, the code
  wins. DOM code (document.querySelector, innerHTML templates, event listeners) describes the UI: rebuild it in
  Compose with the same labels, order and behaviour.
- Everything the output shows is drawn into the master Bitmap (canvas width × height px) by MasterRenderer with
  android.graphics.Canvas, at 1:1 canvas pixels. The viewport only shows that bitmap scaled.
- Canvas 2D to android.graphics:
  - fillRect → drawRect with a FILL paint; strokeRect/lineWidth → a STROKE paint with strokeWidth.
  - setLineDash([a,b]) → DashPathEffect.
  - createLinearGradient + addColorStop → LinearGradient.
  - arc/ellipse → drawCircle/drawOval/drawArc; roundRect → drawRoundRect.
  - clip() → clipPath; save/restore/translate/scale/rotate → the same.
  - globalCompositeOperation 'source-in' → PorterDuffXfermode(SRC_IN) in a layer.
  - fillText/measureText → drawText/Paint.measureText; textBaseline 'middle' → y − (ascent + descent)/2.
  - font '700 Npx …' → a bold Typeface with textSize N.
  - drawImage → drawBitmap with src/dst rects; createPattern(…,'repeat') → BitmapShader REPEAT.
  - shadowBlur → setShadowLayer.
- Colour strings like '#22d3ee', 'rgba(r,g,b,a)' and 'hsl(h,s%,l%)' must give exactly the same colours.
- When you are done, say what you built, what you changed, and anything you could not do."""

# what each prompt asks for; attachments are paths under screenshots/ (a name ending in * means every match)
P = [
 dict(n=1, slug='shell-layout-settings', title='App shell, theme, layout and settings model',
  attach=['tablet/t01-first-launch.png', 'phone/p01-phone-portrait.png', 'phone/p21-phone-all-open.png', 'panels/ui-header.png', 'panels/ui-canvas.png',
          'panels/ui-led-walls.png', 'panels/ui-tile-model.png', 'panels/ui-size.png', 'panels/ui-position.png', 'panels/ui-test-pattern.png', 'panels/ui-borders.png',
          'panels/ui-engineering-section.png', 'panels/ui-animation-section.png', 'panels/ui-top-bar.png', 'tablet/t21-light-theme.png'],
  ask="""Build "TileSmith" ({V}), a pixel-mapping and test-pattern app for LED video wall technicians. This first step
is the app shell, the whole settings panel and the settings model. The canvas drawing comes in later steps, so the
viewport and the engineering panel are placeholders for now.

1. Theme. It follows the system light/dark setting.
   - Dark: background #0D1217, panel #151C23, lines #27323C, text #E6EDF3, muted #8A9AA8, accent #22D3EE, amber #FFB300.
   - Light: background #F1F3F5, panel #FFFFFF, lines #CFD5DB, text #16202A, muted #5D6B78, accent #0B8AA6, amber #C47A00.
   - The exact spacing, borders and sizes are in the CSS under REFERENCE CODE.
2. Layout.
   - At 900 dp wide or more: a 350 dp settings panel on the left; a 310 dp engineering panel on the right; between
     them, a top bar of buttons (one row that scrolls sideways) above the viewport.
   - Narrower than 900 dp: one scrolling column with the settings, then the top bar and a viewport 70% of the screen
     tall, then the engineering panel.
3. Settings panel.
   - At the top: "TileSmith" with "v{V}" in amber, and the subtitle "LED Wall Pixel Map & Test Pattern Generator".
   - Then the collapsible sections and submenus, built from build() and its helpers F (labelled field), B (button),
     SW and SUB (collapsible submenu). Use exactly their labels, order, control types, options and initial open
     state.
   - Apply the visibility rules in uiVis() and sync(): submenus that appear only with a processor, with power on, or
     for tileshade patterns, and so on.
   - Skip everything marked desk-only (NDI®, Spout/Syphon, video format, loop video): the mobile app hides it. Do show
     the mob-only video note.
4. Settings model.
   - Use data classes Settings (the object S) and Wall (the per-wall keys WK), with exactly these field names, defaults
     and limits (LIM).
   - Selecting a wall copies its keys into S, and editing writes them back (storeWall/loadWall).
   - Canvas presets come from R.
5. Saving. Save as the same JSON as saveNow() ({sv:23,S,walls,cur,crew,logo,dvd}) in filesDir/state.json, 400 ms
   after any change. Load and validate it at start-up as loadState() does.
6. Top bar buttons: ⓘ Info, New Project, Save, Open, Undo menu, Center canvas, Show entire canvas, Next pattern, Export PNG, Export CSV,
   Spec sheet, Resolume XML ▾ (menu: One slice per LED wall / One slice per tile). Save writes the whole project (the saveNow() JSON incl. images, crew, logo) to a .tilesmith file; Open reads one after a confirmation and replaces the current project. After them, a red
   recording status, the zoom % and the fps label. They can do nothing yet.
7. LED walls list (wallsUI) with Add wall / Duplicate / Remove working on the list (positions come in step 4).""",
  spec=['1', '2', '3', '4'], code=[('R', 'R'), ('S', 'loadWall'), ('LIM', 'HEAVY'), ('wallsUI', 'wallsUI'), ('F', 'build'), ('sync', 'uiVis'), ('stFile', 'resetSaved')], css=True),

 dict(n=2, slug='canvas-tiles-tileshade-viewport', title='Master canvas, tiles, borders, overlays, tileshade, viewport',
  attach=['patterns/cv-pattern-01-tileshade.png', 'patterns/cv-overlays-all.png', 'tablet/t09-overlays.png', 'tablet/t01-first-launch.png', 'panels/ui-borders.png'],
  ask="""Add the master canvas and the viewport.

1. MasterRenderer. Draw into an android.graphics.Bitmap of S.cw × S.ch (default 1920 × 1080) by porting render()
   one to one:
   - background #050608;
   - for each wall: dashed #2a3340 outlines on tiles not lit yet, then the pattern clipped to the lit tiles;
   - for each lit tile: the border (S.bc, S.bt), the 1 px inner line, square corner marks, and the label stack: tile
     ID, pixel address (#ffe066) and size in mm (#9fe);
   - the tile position arrows (tposSize/tposTop/tposDraw);
   - the tileshade footer and position label drawn again above the borders.
   For now, every wall is fully lit and pieces(w) is the plain grid (one piece per cell, keys "c,r"). The full
   pieces() comes in step 8. Skip the data, power, technician and DVD parts of render() for now (later steps).
2. Patterns. Implement pat()/patRaw() with the tileshade pattern exactly: checkerboard of Tile-shade color and its
   50% white mix, diagonals, centre circle, wall name and size boxes, footer, and position label. Pick a different
   pattern and the wall turns black for now (step 3).
3. Viewport. Port vpDraw():
   - draw the bitmap scaled by zoom V.z and offset V.x/V.y, with a drop shadow;
   - a cyan #22d3ee outline around the canvas;
   - an amber outline around each wall: solid for the selected wall when there are several, dashed otherwise.
   Port fit()/fitZ()/zMin()/viewBounds(): Show entire canvas fits the canvas with a margin of min(60, 10% of the view). Show the
   zoom % in the top bar.
4. Gestures. Pinch zooms around the fingers (zMin to 500%), two fingers pan, and one finger on empty space pans.
5. Frame loop. Port tick()/loop()/animNow()/busyNow() with withFrameNanos: redraw only when something moves, else
   4 times a second. The fps label shows "· still" when nothing moves.
6. Every setting in "Tile borders & overlays" and the Tile-shade color now changes the picture at once.""",
  spec=['3.3', '7'], anim=['1'], code=[('wN', 'wH'), ('pieces', 'pieceOf'), ('seqRC', 'seqRC'), ('vp', 'fit'), ('posLabel', 'mixW'), ('pat', 'patRaw'), ('bolt', 'tposDraw'),
       ('render', 'render'), ('vpDraw', 'vpDraw'), ('lastStep', 'lastStep'), ('MOVE_PAT', 'loop')]),

 dict(n=3, slug='all-test-patterns', title='All 25 test patterns, image fit, scroll, centre box, uploads',
  attach=['patterns/cv-patterns-all.png', 'patterns/cv-pattern-*', 'panels/ui-test-pattern.png', 'tablet/t18-next-pattern-toast.png'],
  extra_files=['source/readable/images/disguise-test-pattern-16-9.png', 'source/readable/images/disguise-test-pattern-4-3.png',
               'source/readable/images/branded-test-pattern-16-9.png', 'source/readable/images/branded-test-pattern-4-3.png'],
  ask="""Implement every test pattern in PAT_LIST so each one looks exactly like its attached picture. All of them are
drawn by patRaw() and the image helpers below.

1. Built-in images. The four built-in pictures are attached. Add them as res/drawable-nodpi/disguise_16_9.png,
   disguise_4_3.png, branded_16_9.png and branded_4_3.png, and use them where PATIMG_SRC names them. SMPTEbars is
   drawn once at 1920 × 1080 by drawBars() (GEN_PAT) and then treated like an image.
2. Image fit (PFIT, five modes) for every image pattern, exactly as drawImgPat() does, including the 25 MP cache limit.
3. Scroll. Port scrollOff() and blitWrap(): four directions, speed = Scroll speed × 0.2 × the wall's shorter side in
   px per second, wrapping around. Choosing smptescroll switches Scroll to diagonal ↘ when it was none.
4. Centre box of the branded patterns (PATIMG_BOX, drawPatBox): text in BOXFONT with boxCol and never stretched, or
   an uploaded logo with its aspect kept.
5. Uploads. "Upload test pattern", "Upload logo" (centre box) and "Upload logo" (DVD) open the Android photo picker.
   Keep pictures up to 8192 px (loadImgFile), store them as data URLs in the saved JSON, and show
   "Upload a test pattern image" on the custom pattern until one is chosen.
6. Next pattern. Port nextPattern(): move the selected wall to the next pattern in PAT_LIST order, skipping custom
   until an image is uploaded, and show the toast "Test pattern: <name> (<wall>)" at the bottom centre.""",
  spec=['7.1', '8'], code=[('SMPTE', 'tcycTile'), ('pat', 'patRaw'), ('nextPattern', 'nextPattern'), ('loadImgFile', 'loadImgFile')]),

 dict(n=4, slug='presets-walls-dragging', title='Tile models, canvas presets, several walls, dragging and snapping',
  attach=['tablet/t02-two-walls-data.png', 'tablet/t03-led-walls.png', 'tablet/t04-wall-position.png', 'shapes/cv-three-walls.png', 'panels/ui-tile-model.png',
          'panels/ui-size.png', 'panels/ui-position.png', 'panels/ui-led-walls.png'],
  ask="""Make walls and the settings that change them work.

1. Tile model presets (P, grouped by manufacturer, as presetSel() builds the list). Picking one fills tw, th, wmm,
   hmm, pitch, kg, wmax and dmm. Editing any of those switches the preset to "Custom". Density is
   1e6 / pitch² px/m², and Typical is 40% of max watts.
2. Canvas presets (R), and Fit canvas to walls (fitCanvas). Wall size quick buttons. Wall position fields and buttons.
3. Several walls: selWall, addWall (new 4 × 3 wall, next unused pattern from PATS, next tile-shade colour from SHADES,
   placed to the right or below), Duplicate and Remove (delWall). The wall list highlights the selected wall in
   amber, and sections marked with the wall's name edit the selected wall.
4. Viewport gestures, ported from the pointer handlers below:
   - tap a wall to select it;
   - one finger on a wall drags it; it snaps to canvas edges and other walls within 10 screen px (snapPos), with
     magenta #ff2bd6 dashed guides while dragging;
   - after dropping, keepGap pushes overlapping walls apart so a 2 px gap (GAP) remains;
   - editing modes (manual wiring, Remove tiles, Mark half tiles) take over one-finger drags in later steps.
5. Port applyKey and the input/change/click handlers below, so every control and button in the panel does exactly
   what it does there (actions not built yet can stay empty).""",
  spec=['4.2', '5'], code=[('P', 'HALF'), ('presetSel', 'presetSel'), ('selWall', 'fitCanvas'), ('setAll', 'applyPreset'), ('applyKey', '-fit_if'), ('drag', 'keepGap'), ('PTR', '-SMPTE')]),

 dict(n=5, slug='engineering-panel', title='Engineering panel and its formulas',
  attach=['panels/ui-engineering-panel.png', 'tablet/t02-two-walls-data.png', 'tablet/t07-power-and-data.png'],
  ask="""Fill the engineering panel (right side on tablets, bottom on phones) by porting wst(), canvasRows(), wallRows(),
procRowsCanvas(), powRowsCanvas() and info():
- an "Entire canvas" section, then one section per wall (titled with the wall name);
- each is a collapsible two-column table (label left, value right) with the same rows, number formats and units;
- rows for the processor and power appear only when those features are on (steps 6 and 7 fill them in).

Check: a 6 × 4 Unilumin UpadIV 2.6 wall must show 24 tiles, 1152 × 768 px (884,736 LED px, 0.88 MP), 3.00 × 2.00 m,
6.00 m², 151.2 kg / 333 lbs, 2.88 kW peak and 1.15 kW typical.""",
  spec=['9', '16'], code=[('wst', 'info')]),

 dict(n=6, slug='processors-data-wiring', title='LED processors and data wiring',
  attach=['wiring/cv-data-wiring-all.png', 'wiring/cv-data-wiring-*', 'wiring/cv-data-snake-8-starts.png', 'wiring/cv-data-linear-8-starts.png',
          'panels/ui-led-processor.png', 'panels/ui-data-wiring.png', 'tablet/t05-data-wiring.png', 'tablet/t06-manual-data-wiring.png'],
  ask="""Add LED processors and data wiring.

1. Processor list (PROC). Settings:
   - frame rate, bit depth, ULL (Brompton);
   - Pixels per port from specPx() for the chosen frame rate and bit depth, with Reset to spec;
   - ports per processor, return ports (R#), Show data paths.
   Tiles per port is tpp(). Data wiring is shown only when a processor is chosen.
2. Automatic data wiring:
   - patterns None / Snake / Linear / Manual;
   - the 8 start icons (wpatSvg: green start, red end);
   - the five Data wiring preferences (WFILL) with their one-line explanations (WFILLN).
   Port blockPath, splitN, blockGrid, autoChains, keepTiles, wallChains and portPlan exactly. Every tile is in exactly
   one chain; no chain is over capacity unless it must be; ports are numbered P1, P2 … across walls.
3. Drawing (the data part of render()), for each port:
   - a line through the tile centres in PC[port mod 8], width max(2, min(tw, th)/30);
   - filled arrow heads at the segment midpoints;
   - a "P#" circle badge on the first tile and a dark "R#" square on the last;
   - red #ff3b3b dashed when over capacity.
   Each image in wiring/cv-data-wiring-* must match: a 10 × 5 UpadIV wall, NovaStar VX1000 Pro (17 tiles per port),
   Snake from the top-left, horizontal.
4. Manual wiring:
   - Wire tiles (the button reads Stop wiring while on), New port, Undo, Clear;
   - tap tiles, or drag across them (sampled every quarter tile); drag back to remove;
   - press the last tile to continue the chain;
   - the exact messages from manAdd()/wireMsg(), and the status lines ("P1→R1: 15/17", unwired count, "Adding to P3.").
5. Fill the processor rows of the engineering panel.""",
  spec=['10'], code=[('D', '-PFILL'), ('manWiring', 'wireDrag'), ('render', 'render')]),

 dict(n=7, slug='power-and-power-wiring', title='Power and power wiring',
  attach=['wiring/cv-power-wiring-all.png', 'wiring/cv-power-wiring-*', 'wiring/cv-data-and-power.png', 'panels/ui-power.png', 'panels/ui-power-wiring.png',
          'tablet/t07-power-and-data.png', 'tablet/t08-power-wiring.png'],
  ask="""Add power.

1. Settings. Power distribution (Socapex, 6 circuits per cable) shows the power settings when it is ticked:
   - voltage, breaker amps, load circuits to 80%;
   - power link limit (plink);
   - Show power runs.
   Usable watts per circuit is circW(), and tiles per circuit is tpcW().
2. Power wiring: the same patterns, 8 starts and five Wiring preferences (PFILL/PFILLN) as data wiring. Port
   powChains, powerPlan and powerTotals. Circuits are labelled cable-circuit, 1-1 … 1-6, 2-1 … (cLabel) for Socapex, or 1-X, 1-Y, 2-X … for NEMA L14-30 (2 circuits per cable) and L21-30 (3 per cable), or just 1, 2, 3 … for powerCON to Edison (one circuit per cable, with optional plugs-per-wall-circuit checks: pwall, pwallA), chosen with the Distribution cable setting (PDT, PD, cCab, cLeg). No phase is assigned.
3. Manual power wiring: Wire tiles, New circuit, Undo, Clear, with the messages from pmanAdd()/pwMsg().
4. Drawing (the power part of render()):
   - a dashed line (dash 3w, gap 2w, w = max(2, min(tw, th)/36)) in POWC[circuit mod 6];
   - a start badge with a lightning bolt (bolt()) and the circuit number; a small square on the last tile.
   When a wall shows both data and power:
   - data runs at the tile centre minus 0.2 tile width;
   - power runs at plus 0.2 width and plus 0.2 height, white on a black casing (2.4× width), with white badges.
   Over-capacity circuits stay red.
5. Fill the power rows of the engineering panel (powRowsCanvas: circuits used, min. circuits, Socapex cables with
   spare circuits, peak load per cable).""",
  spec=['11'], code=[('PFILL', 'powerTotals'), ('pwMsg', 'pmanAdd'), ('bolt', 'bolt'), ('powRowsCanvas', 'powRowsCanvas'), ('render', 'render')]),

 dict(n=8, slug='wall-shapes', title='Wall shapes: removed tiles and half tiles',
  attach=['shapes/cv-half-tiles.png', 'shapes/cv-removed-tiles.png', 'tablet/t10-remove-tiles.png', 'tablet/t11-half-tiles.png', 'panels/ui-tile-model-half.png', 'panels/ui-size.png'],
  ask="""Make wall shapes work exactly as described: a wall is a list of pieces (pieces()), not just a grid.

1. Remove tiles (Size of LED Wall).
   - Remove tiles / Stop removing, and Restore all tiles.
   - Tap a tile to take it out or put it back; dragging repeats the first tap's choice on every tile crossed.
   - Removed spots show a red dashed outline with an X, in the viewport only (vpDraw).
2. Half tiles (Size of LED Wall). Shown only for models in HALF. Convert bottom / top row to half tiles (toggle), Mark half tiles / Stop marking (with a red STOP MARKING HALF TILES button over the viewport), and Clear half tiles. The wall is the bounding box of its real tiles (wW/wH/pieces X0,Y0, gx/gy).
   - Port unitG, layDefault, layPieces, unitAt, halfAct, halfDo, unitDrag, halfDrag, goneDrag and restoreAll.
   - A tap within 22% of a unit edge between two halves joins them (upright, or on its side for ROE); a tap on a full
     tile keeps the half that was tapped; a tap on an empty half fills it; a tap on a half takes it out.
   - The half-tile note text and the status line as in uiVis.
3. Piece numbering. Tile IDs on half-tile walls are numbered in reading order of the pieces and half tiles end in
   " ½". Engineering totals use each piece's own spec.
4. Everything follows the pieces: wiring (layChains on half-tile layouts), power, the engineering panel and (next
   step) the build order.""",
  spec=['6'], code=[('halfOf', 'pieceOf'), ('pwiring', 'restoreAll'), ('layChains', 'layChains')]),

 dict(n=9, slug='build-animation-technician', title='The build animation and the technician',
  attach=['animations/anim-build-strip.png', 'animations/anim-tech-phases.png', 'animations/anim-tech-poses.png', 'animations/anim-tech-looks.png',
          'animations/anim-carried-tile.png', 'animations/anim-build-progress.png', 'animations/anim-multiwall-start.png', 'animations/anim-build-first-tiles.gif',
          'tablet/t13-build-in-progress.png', 'panels/ui-technician.png', 'panels/ui-build-options.png'],
  ask="""Add the build animation. This is TileSmith's signature feature, so port the code below line by line. The
attached frame strips are the exact reference: same canvas, same timing, same poses.

1. Simulation, per wall (mkSim, stepSim, step, reset, showAll, pickCrew), run from tick() with the real dt:
   - phases walkin 0.8 s, move 1.1 s, place 0.8 s, lock 0.6 s, walkout 1.5 s;
   - times Speed and the wall's rate RATES[i];
   - wall i starts i × 0.6 s later;
   - a tile becomes lit (shows the pattern) at the end of lock;
   - each walkin takes the next crew member.
   Build order is seqRC().
2. Positions and motion. Port techBox() and drawWallTech() exactly:
   - tech size, carry scale, standing spot beside the slot, walk-on and off-wall points;
   - facing angles, the tile flying from the hands to the slot and growing to full size;
   - the hands holding its top corners and shaking during lock.
   Everything is clipped to the wall rectangle.
3. The technician. Port worker() (and drawTech, sh, rr, STY) line by line: shadow, legs with knee bend, boots, arms
   with two-bone inverse kinematics to the hands, hi-vis vest with reflective bands and back logo, name tag with
   lanyard, head with skin and hair or a round face photo, hard hat with brim; mirrored by facing angle. The pose sheet
   (anim-tech-poses.png) is drawn with this exact function: match every cell.
4. The carried tile (cab) and the lock sparkle (end of render()): a ring that grows by 0.03 × Speed per frame, radius
   t × max(tw, th) × 0.9, line width 6(1 − t) + 1, colour rgba(255,255,200,1 − t).
5. Controls:
   - LED build submenu: Start (clear every wall and play), Stop (everything done), Reset (clear, paused), Play / Pause. Then Speed 0.25–5, Loop build, Pause before restart.
   - Technician: Hard hat and Vest colours, Vest logo text or uploaded image, "Crew details & name tags".
   - Crew editor (crewUI): name, 6 skin swatches, custom skin colour, hair colour, face photo; default crew Marcus,
     Elena, David, Chen, Priya, Malik.
6. Estimated build length (buildSecs) for the Video export note.""",
  spec=['12'], anim=['2', '3', '4'], code=[('HAIR', 'defCrew'), ('SK', 'buildSecs'), ('seqRC', 'seqRC'), ('STY', 'cab'), ('D', 'NX'), ('pickCrew', 'step'),
       ('techBox', 'drawWallTech'), ('render', 'render')]),

 dict(n=10, slug='dvd-and-moving-patterns', title='DVD screensaver and the moving patterns',
  attach=['animations/anim-dvd-strip.png', 'animations/anim-dvd-sprites.png', 'animations/anim-dvd.gif', 'animations/anim-dvd-corner.gif',
          'animations/anim-tileshade-cycle-strip.png', 'animations/anim-tileshade-cycle.gif', 'animations/anim-cycle-strip.png', 'animations/anim-sweep-strip.png',
          'animations/anim-sweep.gif', 'animations/anim-scroll-strip.png', 'animations/anim-scroll.gif', 'panels/ui-dvd.png', 'tablet/t12-dvd.png'],
  ask="""Add the DVD screensaver and make the time-based patterns move.

1. DVD screensaver. Port everything from DVD_ST to dvdLoopSet, plus dvdStats.
   - Sprites: the TileSmith logo, text or an uploaded image, 200 px tall, recoloured source-in to
     hsl(hue,100%,55%).
   - Bounce inside each wall or the whole canvas, at speed dvdSpeed × 0.25 × the shorter side px/s.
   - Corner hit chance (dvdDecide/dvdAim/dvdAvoid, up to 45% of bounces), a new colour at least 70° away at every
     bounce, and the Perfect loop mode (dvdLoopPlan/dvdLoopAt).
   - The logo is drawn over the pattern, under the tile borders (dvdDraw from render).
   - The stats line counts bounces and corner hits.
   - Exporting the DVD loop video is desktop only (Video export > DVD logo): leave it out.
2. Moving patterns:
   - tileshade-cycle: a 2.5 s step, with the next colour sliding in from the left with smoothstep during the last
     1.5 s; neighbours never match.
   - cycle: the full field steps through 8 colours every 1.5 s.
   - sweep: a moving rainbow, redrawn every frame.
   - Scroll on any pattern.
   They must match the attached strips frame for frame at the same T.
3. The redraw rules (animNow/busyNow/tick): redraw every frame only while something moves.""",
  spec=['13'], anim=['1', '5', '6'], code=[('T', 'PXC'), ('dvdImg', 'dvdLoopSet'), ('dvdStats', 'dvdStats'), ('TCYC', 'tcycTile'), ('scrollOff', 'blitWrap'), ('MOVE_PAT', 'tick')]),

 dict(n=11, slug='exports-sharing-video', title='Exports, sharing and video recording',
  attach=['tablet/t14-recording.png', 'tablet/t15-recording-saved.png', 'tablet/t17-resolume-menu.png', 'tablet/t19-saved-toast.png', 'tablet/t20-spec-sheet.png',
          'panels/ui-video-export.png'],
  ask="""Add every export. Write each file to cacheDir/exports and open the Android share sheet (ACTION_SEND through a
FileProvider, authority <applicationId>.fileprovider, file_paths cache-path "exports/"). It counts as saved when the
sheet returns OK or the app went to the background while it was open. Toast "Saved <name>." when saved, else
"Not saved: <name>".

1. Export PNG: the master bitmap as tilesmith-canvas.png at full size.
2. Export CSV: patching.csv, exactly as csv() builds it (same columns, order and number formats).
3. Spec sheet: tilesmith-spec.html, the HTML from spec(), without the print script (the mobile app shares the file).
4. Resolume XML: tilesmith-WxH.xml from resolumeXML(), with One slice per LED wall or One slice per tile from the
   menu, and the toast text from exportRes().
5. Export video (Video export submenu, button Export video, with the LED build box ticked), the same behaviour as recToggle/recStartMR/recTick/endRec, in Kotlin:
   - record the master bitmap at 60 fps into an H.264 MP4 with MediaCodec (an input Surface: draw the bitmap with
     lockHardwareCanvas each frame) and MediaMuxer;
   - bitrate min(40 Mbps, max(4 Mbps, W × H × 60 × 0.12));
   - phases: Blank intro (an empty canvas), the live build, then Final hold;
   - status "● REC blank Ns", "● REC building", "● REC hold Ns", "Saving video…", "Saved <name>";
   - keep the screen on while it records;
   - share tilesmith-build-YYYYMMDD-HHMMSS.mp4 when it finishes;
   - pressing Export video again cancels ("Recording cancelled") and deletes the file.
   HAP, ProRes and the loop video are desktop only.""",
  spec=['14', '15'], code=[('csv', 'exportRes'), ('dl', 'mobSave'), ('REC', 'recUI'), ('endRec', 'recTick')]),

 dict(n=12, slug='info-dialog-and-finishing', title='Info dialog, toasts and the final comparison',
  attach=['tablet/t16-info-dialog.png', 'panels/ui-info-dialog.png', 'tablet/t01-first-launch.png', 'tablet/t02-two-walls-data.png', 'phone/p01-phone-portrait.png'],
  ask="""Finish the app.

1. The ⓘ Info dialog, exactly as the attached markup and screenshot:
   - title "TileSmith - LED Wall Builder" and "Version {V}";
   - "Concept & development: Callum Davenport-Lambton";
   - contact tilesmithapp@gmail.com, with a Copy e-mail button that shows "Copied!";
   - "Support the project" with the Ko-fi button (https://ko-fi.com/kingof9x), opened in the browser;
   - Reset saved settings: confirm "Reset all saved settings, crew and uploads to defaults?", then delete state.json
     and restart with the defaults;
   - Close.
   Leave out the NDI®, Spout and Syphon entries (desktop only).
2. Toasts. Bottom centre, for 2.5 to 9 s, as toast() does. The Resolume XML menu closes on outside taps (ddClose).
3. Loop build and every top-bar button work as in the earlier steps' code.
4. Compare. Go through every attached screenshot and every picture from earlier steps, list each difference you can
   see (labels, order, spacing, colours, what the canvas draws), and fix them. Then run the checks in spec section 16
   and report the results.""",
  spec=['16'], code=[('showAbout', 'toast')], markup=True),
]


def toplevel(js):
    out = subprocess.run(['node', str(TOOLS / 'toplevel.js'), str(js)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main(kit):
    kit = pathlib.Path(kit)
    js = kit / 'source' / 'readable' / 'app.js'
    lines = js.read_text().split('\n'); top = toplevel(js)
    def stmt(name):
        for i, x in enumerate(top):
            if name in x['names']: return i
        raise SystemExit(f'[STOP] {name} is not a top-level name in app.js')
    def region(a, b):
        i = stmt(a)
        j = stmt(b[1:]) - 1 if b.startswith('-') else stmt(b)   # "-name": up to the statement before name
        assert j >= i, (a, b)
        return '\n'.join(lines[top[i]['start'] - 1:top[j]['end']]), top[i]['start'], top[j]['end']
    spec_md = (kit / 'TileSmith-App-Spec.md').read_text()
    anim_md = (kit / '04-ANIMATIONS.md').read_text()
    version = re.search(r'TileSmith ([\d.]+)', spec_md).group(1)
    def section(md, num):
        lvl = '###' if '.' in num else '##'
        m = re.search(rf'^{lvl} {re.escape(num)}[. ].*$', md, re.M)
        assert m, f'section {num} not found'
        nxt = re.search(r'^#{2,3} ' if lvl == '###' else r'^## ', md[m.end():], re.M)
        txt = md[m.start():m.end() + (nxt.start() if nxt else len(md))].strip()
        return re.sub(r'!\[[^\]]*\]\(screenshots/[^/]+/([^)]+)\)', r'(picture: \1, attached)', txt)
    shots = kit / 'screenshots'
    def expand(a):
        if a.endswith('*'):
            got = sorted(str(p.relative_to(shots)) for p in shots.glob(a)); assert got, a; return got
        assert (shots / a).exists(), a; return [a]
    outdir = kit / 'route-b-prompts'; outdir.mkdir(exist_ok=True)
    css = (kit / 'source' / 'readable' / 'style.css').read_text()
    html = (kit / 'source' / 'readable' / 'index.html').read_text()
    about = html[html.index('<div class="ov" id="about"'):html.index('<script')].strip()
    sizes = []
    for p in P:
        att = [x for a in p['attach'] for x in expand(a)]
        ref = []
        for s in p.get('spec', []):
            ref.append(f'----- REFERENCE: TileSmith-App-Spec.md, section {s} -----\n{section(spec_md, s)}')
        for s in p.get('anim', []):
            ref.append(f'----- REFERENCE: 04-ANIMATIONS.md, section {s} -----\n{section(anim_md, s)}')
        for a, b in p.get('code', []):
            code, l0, l1 = region(a, b)
            ref.append(f'----- REFERENCE CODE: app.js lines {l0}-{l1} -----\n{code}')
        if p.get('css'):
            ref.append(f'----- REFERENCE CODE: style.css (the whole stylesheet; :root = light theme, the media query = dark) -----\n{css.strip()}')
        if p.get('markup'):
            ref.append(f'----- REFERENCE CODE: the Info dialog markup (index.html) -----\n{about}')
        body = (f"TileSmith native Android rewrite, step {p['n']} of 12: {p['title']}\n\n" + p['ask'].replace('{V}', version) + '\n\n'
                + RULES.replace('{n}', str(p['n'])) + '\n\n' + '\n\n'.join(ref) + '\n')
        extra = [f'  - {f} (in the kit, not under screenshots/)' for f in p.get('extra_files', [])]
        head = (f"ROUTE B, PROMPT {p['n']} OF 12: {p['title'].upper()}\n"
                f"{'=' * 72}\n"
                f"1. In the same AI Studio Android project as the earlier prompts, attach these {len(att) + len(extra)} files (from the kit's screenshots/ folder):\n"
                + '\n'.join(f'  - {a}' for a in att) + ('\n' + '\n'.join(extra) if extra else '') +
                "\n2. Copy everything between the two COPY lines below into the prompt box and send it.\n"
                "3. When it is done, compare the app with the attached pictures. If something differs, use the fix-up prompts in\n"
                "   B00-HOW-TO-USE.md before going on to the next prompt.\n"
                f"(This prompt is {len(body):,} characters. If AI Studio cuts it off, send it in two messages: the part above\n"
                " REFERENCE first with \"more reference follows, wait\", then the REFERENCE part.)\n\n"
                "======================== COPY FROM HERE ========================\n")
        f = outdir / f"B{p['n']:02d}-{p['slug']}.txt"
        f.write_text(head + body + "========================= COPY TO HERE =========================\n")
        sizes.append((f.name, len(body), len(att) + len(extra)))
    rows = '\n'.join(f'| `{n}` | {P[i]["title"]} | {a} | {b // 1000} KB |' for i, (n, b, a) in enumerate(sizes))
    (outdir / 'B00-HOW-TO-USE.md').write_text(f"""# Route B prompts: native Kotlin + Compose rewrite of TileSmith {version}

These are the 12 prompts from `02-NATIVE-REWRITE-GUIDE.md`, fully assembled. Each file holds:

- the instructions for that step;
- the rules that keep AI Studio faithful to the original;
- the sections of `TileSmith-App-Spec.md` and `04-ANIMATIONS.md` it needs;
- the original JavaScript to port (from `source/readable/app.js`);
- at the top, the list of screenshots to attach.

Nothing has to be looked up or pasted by hand.

| File | Step | Attachments | Size |
|---|---|---|---|
{rows}

## How to use them

1. Start a new **Android** app in Google AI Studio (Build). Use one project for all 12 prompts.
2. Open `B01-….txt`, attach the files listed at its top, and paste everything between the COPY lines.
3. Let it build. Compare the emulator with the attached pictures, and fix differences before moving on (prompts
   below).
4. Carry on with B02, B03 … in order. Each step builds on the previous ones.
5. AI Studio can publish to the Play internal testing track or install on a USB-connected phone at any point; you can
   also download the project ZIP and continue in Android Studio.

Expect several fix-up rounds per step. The build animation (B09) and the patterns (B02, B03, B10) need the most care.
Route A (`01-PROMPT-exact-app.md`) gives the exact app straight away; route B is for a native code base.

## Fix-up prompts

- **It looks different:** "Compare the app with the attached <file>. List every difference in labels, order,
  spacing, colours and what the canvas draws, then fix each one. The picture is the reference."
- **It simplified something:** "<function> in the reference code was simplified. Port it again line by line, keeping
  every constant, branch and drawing call; do not change the maths."
- **A number is wrong:** "Check <value> against TileSmith-App-Spec.md section <n> and the reference code. Show the
  formula you use and the formula in the code, then make them the same."
- **The canvas looks blurry or wrong at 100%:** "MasterRenderer must draw into a Bitmap of exactly S.cw × S.ch pixels
  at 1:1. The viewport only scales that bitmap. Check that no density scaling is applied to canvas drawing."
- **It is slow:** "Redraw the master bitmap only when animNow()/busyNow() say something moves (spec section 7), reuse
  Paint objects and Bitmaps, and do the drawing off the main thread if needed. Keep the output identical."
- **It lost earlier work:** "Step <n> broke <feature> from step <m>. Restore it without undoing step <n>."

## Checks at the end

Run the checks in `TileSmith-App-Spec.md` section 16 and compare with the kit's screenshots:

- **Patterns:** a 6 × 4 UpadIV wall on a 1152 × 768 canvas with the overlays off must match each
  `patterns/cv-pattern-NN-*.png`.
- **Wiring:** a 10 × 5 wall with a NovaStar VX1000 Pro, Snake from the top left, horizontal, must match
  `wiring/cv-data-wiring-*.png`. Power at 120 V 20 A loaded to 80% must match `wiring/cv-power-wiring-*.png`.
- **Build:** a 6 × 3 wall on a 1152 × 576 canvas at Speed 1 must match `animations/anim-build-strip.png` frame by
  frame.
""")
    print(f'[ok] {len(P)} route B prompts in {outdir}: ' + ', '.join(f'B{i + 1:02d} {b // 1000} KB' for i, (_, b, _a) in enumerate(sizes)))


if __name__ == '__main__':
    main(sys.argv[1])
