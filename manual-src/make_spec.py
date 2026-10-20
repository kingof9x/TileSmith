# Builds TileSmith-App-Spec.md: a detailed description of the app for another AI model (or developer) to build a clone,
# e.g. an Android app. Lists (settings, presets, processors, patterns, video formats, half tiles...) are
# read from the running app/index.html, so the spec always matches the build it ships with.
# Run: python3 make_spec.py   (fails if a setting or pattern has no description here, so new features get documented)
import asyncio, json, pathlib, datetime, os
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__import__('os').environ.get('TILESMITH_ROOT', pathlib.Path(__file__).resolve().parent.parent / 'tilesmith-desktop'))
APP = 'file://' + str(ROOT / 'app' / 'index.html')
OUT = pathlib.Path(os.environ.get('SPEC_OUT', ROOT / 'TileSmith-App-Spec.md'))
VERSION = json.loads((ROOT / 'package.json').read_text())['version'].rsplit('.0', 1)[0]
TODAY = datetime.date.today().isoformat()

# every setting the app saves, with what it does. Per-wall keys are marked by the app's WK list.
KEYDESC = {
 'cw': 'Canvas width in px (16-8192) of the selected canvas. Each canvas is a raster sent over its own NDI / Spout / Syphon source and recorded to its own video. Projects store every canvas in cvs:[{name,cw,ch,cur,walls}] with ac = the selected canvas (its walls are the top-level walls, cvs[ac].walls is null).',
 'ch': 'Canvas height in px (16-8192).',
 'bc': 'Tile border colour (overlay drawn on every lit tile).', 'bt': 'Tile border thickness in px (1-8).',
 'tpos': 'Show tile position arrows on every lit tile (any pattern).',
 'ids': 'Show tile ID labels "T05 [C5:R1]".', 'addr': 'Show each tile\'s pixel address range label.', 'mm': 'Show each tile\'s size in mm label.',
 'speed': 'Build animation speed multiplier (0.25-5).',
 'dvdOn': 'DVD screensaver on/off.', 'dvdSrc': 'DVD logo source: TileSmith logo | Text | Uploaded image.', 'dvdText': 'Text used when dvdSrc = Text.',
 'dvdArea': 'Bounce inside: Each LED wall (one logo per wall) | Whole canvas (one logo).', 'dvdSize': 'Logo height as % of the area\'s shorter side (5-60).',
 'dvdSpeed': 'Bounce speed multiplier (0.25-3). Base speed = 0.25 x shorter side per second.', 'dvdCorner': 'Corner hit chance slider 0-100 (100 = about 45% of bounces hit a corner).',
 'dvdTint': 'Recolour the logo at every bounce.', 'dvdLoop': 'Perfect loop mode (motion repeats exactly).', 'dvdLoopLen': 'Perfect loop length in seconds (4-600).',
 'dvdLoopCorners': 'Perfect loop includes exactly two corner hits per loop (else none).',
 'rcard': 'Engineering > LED processor: receiving card family in the tile (any, brompton, novastar, helios, evision). Narrows the processor list; resets to any when the tile does not allow it.', 'procAll': 'Engineering > LED processor (UI label "Show incompatible processors"): show every processor instead of only those listed for the selected wall\'s tile. The currently chosen processor is always listed; if the tile does not list it, an amber warning shows. Compatibility comes from ROE brochure Processing Platform lines (CMP table: Carbon, Carbon MkII, Graphite, Black Pearl BP2V2, Ruby 2.2/2.6, Vanish V5S/V8S MkII, V8T, ST V4ST/V6ST, Black Quartz, Jet, Topaz, Meru, Sierra, Diamond); tiles not in the table are unrestricted; the list follows the selected wall; #procWarn names every wall on any canvas whose tile does not list the chosen processor. Download config file (experimental): NovaStar = zip of NovaLCT .scr per canvas (DSCI header, DVI info, Standard screens of 17-byte cabinet regions, adjust info; 16-bit byte-sum checksums) + wiring CSV/JSON; other brands = wiring CSV/JSON. Canvas output: per-canvas display picker opens a borderless full-screen window (frame name tsout:<display id>:<canvas id>) drawn 1:1 in device pixels.', 'vLed': 'Video export: tick to include the LED build video (blank intro, live build, final hold).', 'vDvd': 'Video export: tick to include the DVD logo perfect-loop video (desktop only; needs Bounce a logo and Perfect loop). With both ticked, one Export video click makes two files, LED build first.', 'vIntro': 'Video export: seconds of blank canvas before the build (0-60).', 'vHold': 'Video export: seconds holding the finished wall (0-120).',
 'vCodec': 'Video export format (see Video formats).', 'hapFmt': 'HAP flavour: hap | hap_alpha | hap_q.',
 'proc': 'LED processor model (or None). Gates all data/port features.', 'fps': 'Processor frame rate in Hz (affects pixels per port).',
 'bpc': 'Processor bit depth (8, 10, 12).', 'ull': 'Brompton Ultra Low Latency (halves port capacity).', 'ppx': 'Pixels per port in use (from spec, editable).',
 'pports': 'Ports per processor / sending card (editable).', 'ret': 'Count a return port (R#) for every primary port.', 'showData': 'Draw data paths on the canvas.',
 'pdist': 'Power distribution ticked. Gates all power features.', 'pdt': 'Distribution cable: "Socapex (6 circuits per cable)" (default), "L14-30 (2 circuits per cable)" "L21-30 (3 circuits per cable)" or "powerCON to Edison (1 circuit per cable)". Choosing Edison sets pvolt 120 and pamps 15.', 'pwall': 'Edison only: plugs per wall circuit (0-100, default 0 = no wall-circuit check).', 'pwallA': 'Edison only: wall circuit breaker in amps (1-400, default 20).', 'gx': 'Wall key: how far (px) the top-left of the wall\'s real tiles sits right of the full tile grid. Set by the app, not the user; ox/oy are the canvas position of those tiles.', 'gy': 'Wall key: like gx, downwards (a converted top row makes it half a tile).', 'lblPow': 'Power labels: "Cable and circuit labels" (default), "Circuit labels only", "Cable labels only".', 'pvolt': 'Circuit voltage: 100, 110, 120, 208, 220, 230 or 240 V.',
 'pamps': 'Breaker size in amps (1-400).', 'derate': 'Load circuits to 80% (continuous load rule).', 'showPow': 'Draw power runs on the canvas.',
 'resSl': 'Resolume XML slice mode: One slice per LED wall | One slice per tile.', 'loop': 'Restart the build animation continuously.', 'loopHold': 'Seconds to pause before restarting (0-600).',
 'ndiName': 'NDI source name (default TileSmith-LED-Out).', 'ndiFps': 'NDI frame rate (see NDI).', 'ndiIdle': 'Save CPU: when nothing moves, send about 4 frames per second instead of the full rate.',
 'shName': 'Spout sender name (Windows) or Syphon server name (Mac), default TileSmith. Applies the next time it starts.',
 'shFps': 'Spout/Syphon frame rate while NDI is off: 60, 50, 30 or 25 (while NDI runs, its rate is used).',
 'shIdle': 'Spout/Syphon Save CPU (default on): a still picture is sent about 4 times a second instead of the full rate.',
 'lblWhat': 'Label printing: which cables to label: Data and power (default), Data only, Power only.',
 'lblSize': 'Label sheet preset: Avery 5160 (30 per US Letter), Avery 5163 (10 per US Letter), Avery L7160 (21 per A4), Label roll 62 x 29 mm, or Custom label roll.',
 'lblW': 'Custom roll label width in mm (20-300).', 'lblH': 'Custom roll label height in mm (10-300).',
 'lblCopies': 'Copies printed of each cable end (1-4).', 'lblSkip': 'First label position to use on a sheet (skips used labels).',
 'lblColor': 'Colour the labels: data labels are completely green (primary) or red (return); power labels carry a flag in the wall\'s Tile-shade colour; off = plain labels, no flags or wall marks.',
 'lblLayout': 'Wrap layout: Two identical panels (default), Flag fold-over (second panel rotated 180 degrees), Text in the middle, colour on the ends.',
 'lblFlag': 'Colour flag style: Big end blocks (default), Top and bottom bars, Big corner squares.',
 'lblWall': 'Wall mark: Wall-shade block + name (several walls only, default), Always show wall mark, Wall tint + block (light tint of the wall shade as label background).',
 'lblJump': 'Also print labels for the tile-to-tile links (data and power jumpers).',
 'lblKeep': 'Sheets: keep the two ends of one cable in the same row (pad with a blank cell).',
 'shGpu': 'Spout graphics card (Windows): Automatic (the high-performance card) or a card name from the list. The receiver must be on the same card.',
 'hat': 'Technician hard hat colour.', 'vest': 'Technician vest colour.', 'logo': 'Vest logo text.', 'tstyle': 'Technician character style: Classic, Cartoon or Character pack.', 'tpack': 'Selected character pack (id in the on-device pack library).', 'cd': 'Show crew details editor and name tags.', 'play': 'Build animation playing (not saved).',
 # per wall
 'half': 'Legacy half-tile marks from v3.2 previews ([col,row,side]); converted to "lay" on load.',
 'gone': 'Removed tiles on a plain grid: list of [col,row].',
 'lay': 'Half-tile layout: {} for a plain grid, or {s: split "h"|"w", uc/ur: unit grid size when last edited, p: [[u,v,unitsWide,unitsTall],...]}.',
 'name': 'Wall name.', 'ox': 'Wall X offset on the canvas in px (-20000..20000).', 'oy': 'Wall Y offset on the canvas in px.',
 'cols': 'Columns of tiles (1-64).', 'rows': 'Rows of tiles (1-64).', 'rcfg': 'Per wall: id (SHA-256 hex) of the NovaStar receiving card file (.rcfg/.rcfgx) the wall uses, or empty. Files live in IndexedDB tilesmith-rcfg/files {id,name,ext,size,data,models[],vendor,revision,added}; saved projects carry the used ones as rc:{id:{name,ext,vendor,revision,models,added,data:base64}} (autosave does not), opening a project merges them into the library; Download config file adds them under receiving-card-files/ with a README of which walls use each.', 'preset': 'Tile model preset name ("Custom" once any tile field is edited). The UI picks Brand first, then a model of that brand; user presets live in localStorage "tilesmith-tiles-v1" ({name:[wmm,hmm,tw,th,pitch,kg,wmax,dmm]}) and are copied into the project file as "ut" for every preset a wall uses (on open a differing same-name tile is kept as "Name (from project)"); PINFO holds extra spec-sheet facts per model (receiving card, brightness, refresh, IP, curving, hanging height with an over-limit warning); models in PEST have estimated figures flagged as MISSING DATA in Engineering and the PDF.',
 'tw': 'Tile width in px.', 'th': 'Tile height in px.', 'wmm': 'Tile width in mm.', 'hmm': 'Tile height in mm.', 'dmm': 'Tile depth in mm.', 'kg': 'Tile weight in kg.',
 'wmax': 'Tile max power in W.', 'pitch': 'Pixel pitch in mm.', 'pat': 'Test pattern (see Patterns).', 'pfit': 'Image fit for image patterns (see Image fit).',
 'pdir': 'Scroll direction: none | diagonal ↘ | diagonal ↗ | horizontal → | vertical ↓.', 'pspd': 'Scroll speed (0-3).', 'shadeC': 'Tile-shade colour (tileshade, tileshade-clean).',
 'patImg': 'Uploaded custom pattern image (kept up to 8192 px).', 'boxMode': 'Branded pattern centre box: Nothing | Text | Logo.', 'boxText': 'Centre box text.', 'boxCol': 'Centre box text colour.',
 'boxImg': 'Centre box logo image.', 'corner': 'Build start corner (Tech starts at): Top-left | Top-right | Bottom-left | Bottom-right.', 'dir': 'Tile placement order: Horizontal (row at a time) | Vertical.',
 'wmode': 'Data wiring pattern: None | Snake | Linear | Manual.', 'wcorner': 'Data wiring start corner.', 'wdir': 'Data wiring direction: Horizontal | Vertical.', 'wfill': 'Data wiring preference, how tiles are shared between ports: Fewest ports | Whole rows or columns | One continuous path | Horizontal | Vertical (see Wiring).',
 'wman': 'Manual data chains: list of ports, each a list of tiles ([col,row] on a plain grid, "u,v" keys on a half-tile layout).',
 'pmode': 'Power wiring pattern: None | Snake | Linear | Manual.', 'pcorner': 'Power wiring start corner.', 'pwdir': 'Power wiring direction.', 'pfill': 'Power wiring preference (UI label "Wiring preference"): Fewest circuits | Whole rows or columns | One continuous path | Horizontal | Vertical (see Power).',
 'plink': 'Power link limit: max tiles per circuit (0 = none).', 'pman': 'Manual power chains (same format as wman).',
}
PATSPEC = {
 'tileshade': 'Classic pixel map. Tiles alternate (checkerboard by grid cell) between Tile-shade colour and that colour mixed 50% with white. White 1.5 px+ lines corner to corner across the wall, a centre circle of radius h/4. Wall name (light box, dark text) and "W {w} X H {h}" (dark box, white text) in the middle, font f = max(12, min(h/22, w/30)). Position label "X {x},Y {y}" (canvas position of the first tile\'s top-left corner; first tile = top row, then leftmost) drawn as an overlay at that corner: white text on rgba(0,0,0,.62). Footer centred at the bottom: "{name} / Position: X {ox}, Y {oy} / {cols}.0 Columns X {rows}.0 Rows - {N} Cabinets Total ({n} half) / Resolution: {w} x {h} ( {w*h} ) / Aspect Ratio: {w/h}" in a light box, font max(10, min(h/50, tileH/10)) shrunk to fit 98% of the wall width; drawn again above the tile borders.',
 'tileshade-clean': 'tileshade without the name, size and position boxes (footer kept).',
 'tileshade-cycle': 'tileshade layout (lines with a dark casing so they show on white), but every tile cycles red #ff0000, green #00ff00, blue #0000ff. Tile (col,row) shows TCYC[(col + 2*row + k) mod 3] where k = floor(t / 2.5 s); neighbours (left/right/up/down) never match. In the last 1.5 s of each 2.5 s step the next colour slides in from the left with smoothstep easing and pushes the current one out (both move). Redraws every frame only while sliding.',
 'SMPTEbars': 'Drawn SMPTE bars at 1920x1080, then fitted like an image: 7 bars #bfbfbf #bfbf00 #00bfbf #00bf00 #bf00bf #bf0000 #0000bf over the top 75%; a #0000bf strip 75-85%; bottom 15% in 7 blocks #00214c #fff #32006a #111 #000 #1d1d1d #111.',
 'ramp': '16 vertical grey steps from 0 to 255, left to right.',
 'sweep': 'Animated rainbow: horizontal gradient of 7 hues offset by 60° x t, with a white (top) to clear to dark (bottom) vertical overlay. Redraws every frame.',
 'white': 'Full field #fff.', 'red': 'Full field #f00.', 'green': 'Full field #0f0.', 'blue': 'Full field #00f.', 'black': 'Full field #000.', 'gray50': 'Full field #808080.',
 'disguise test pattern 16:9': 'Built-in 1920x1080 image (grid, circles, grey steps, colour references), embedded as base64 PNG.',
 'disguise test pattern 4:3': 'Built-in 1024x768 version of the same image.',
 'branded test pattern 16:9': 'Built-in 1920x1080 colour bars with a black centre box at (549,249) size 823x115 (image px). Centre box can hold text (BOXFONT, colour boxCol, never stretched) or an uploaded logo (aspect kept).',
 'branded test pattern 4:3': 'Built-in 1024x768 version, centre box at (293,173) size 438x88.',
 'custom': 'Uploaded image (PNG/SVG/JPG, kept up to 8192 px). Shows "Upload a test pattern image" until one is uploaded.',
 'pixel1': 'Single-pixel checkerboard (every other pixel white).',
 'circles': 'Dark #1c1c1c field, white 3 px lines: large centre circle (0.45 x shorter side), four small corner circles, centre cross and both diagonals.',
 'gradH': 'Smooth black to white, left to right.', 'gradV': 'Smooth black to white, top to bottom.',
 'rgbramp': 'Four horizontal bands, each black to red / green / blue / white, left to right.',
 'zone': 'Zone plate: white concentric circles on black at radii sqrt(k) x max(6, R/45).',
 'cycle': 'Full-field colour stepping every 1.5 s through #f00 #0f0 #00f #fff #000 #ff0 #0ff #f0f. Redraws only when the colour changes.',
}

async def collect():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(900)
        d = await pg.evaluate("""()=>{const o={};for(const k in S){const v=S[k];o[k]=v&&typeof v=='object'&&!Array.isArray(v)&&v.constructor!==Object?null:v}
          return {S:o,WK,P:Object.entries(P).filter(([k,v])=>v),HALF:Object.entries(HALF),PROC:Object.entries(PROC).filter(([k,v])=>v),PATS:PAT_LIST,PFIT,SCRV:Object.keys(SCRV),
           WFILL,WFILLN,PFILL,PFILLN,WPAT,R:Object.entries(R),NFR:Object.entries(NFR),codecs:Object.entries(VCODEC).map(([k,v])=>({name:k,ext:v.ext,enc:v.enc,note:v.note,args:v.args().join(' ')})),
           crew:defCrew().map(c=>c[0]),D,RATES,STAG,GAP,DVD_MAX,TCYC,TC_STEP,TC_SLIDE,STEP_S,PC,POWC,SHADES,NEWPATS:PATS,PATIMG_BOX:Object.entries(PATIMG_BOX),
           top:[...document.querySelectorAll('#bar > button, #bar .dd > button')].map(x=>x.textContent),
           panel:[...document.querySelectorAll('#left > details')].map(dd=>[dd.querySelector(':scope>summary').textContent.trim(),[...dd.querySelectorAll('details.subd')].map(x=>{let n=0,e=x.parentElement;while(e&&e!==dd){if(e.matches('details.subd'))n++;e=e.parentElement}return [n,x.querySelector(':scope>summary').textContent.trim()]})])}}""")
        await b.close()
        assert not errs, errs
        return d

def md_table(head, rows):
    esc = lambda x: str(x).replace('|', '\\|').replace('\n', ' ')
    return '| ' + ' | '.join(head) + ' |\n|' + '---|' * len(head) + '\n' + ''.join('| ' + ' | '.join(esc(c) for c in r) + ' |\n' for r in rows)

def build(d):
    missing = [k for k in d['S'] if k not in KEYDESC] + [p for p in d['PATS'] if p not in PATSPEC]
    assert not missing, f'spec is missing descriptions for: {missing}'
    WK = set(d['WK'])
    fmt = lambda v: json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    glob = md_table(['Key', 'Default', 'Meaning'], [[f'`{k}`', fmt(d['S'][k]), KEYDESC[k]] for k in d['S'] if k not in WK])
    wall = md_table(['Key', 'Default', 'Meaning'], [[f'`{k}`', fmt(d['S'][k]), KEYDESC[k]] for k in d['WK']])
    presets = md_table(['Preset', 'W mm', 'H mm', 'px W', 'px H', 'Pitch mm', 'kg', 'Max W', 'Depth mm'], [[k] + v for k, v in d['P']])
    half = md_table(['Full model', 'Half model', 'Split'], [[k, v[0], 'h = top/bottom (half height)' if v[1] == 'h' else 'w = left/right (half width)'] for k, v in d['HALF']])
    procs = md_table(['Processor', 'Brand', 'Ports', 'px/port', 'at Hz', 'bit', 'Max px', 'Scaling', 'Note'],
                     [[k, m['brand'], m['ports'], m['px'], m['hz'], m['bpc'], m.get('max', ''), m['sc'] + (f", 10-bit {m['px10']}" if m.get('px10') else '') + (', per card' if m.get('unit') == 'card' else ''), m['note']] for k, m in d['PROC']])
    pats = md_table(['Pattern', 'How to draw it'], [[f'`{p}`', PATSPEC[p]] for p in d['PATS']])
    codecs = md_table(['Format', 'Ext', 'ffmpeg encoder', 'ffmpeg output args', 'Note'], [[c['name'], c['ext'], c['enc'], f"`{c['args']}`", c['note']] for c in d['codecs']])
    res = ', '.join(f'{k} ({v[0]}x{v[1]})' for k, v in d['R'])
    wpat = ', '.join(f'{c}/{dd}' for c, dd in d['WPAT'])
    fills = md_table(['Data wiring preference / (power) Wiring preference', 'Rule'], [[a + ' / ' + b, n] for a, b, n in zip(d['WFILL'], d['PFILL'], d['WFILLN'])])
    nfr = ', '.join(f'{k} ({v[0]}/{v[1]})' for k, v in d['NFR'])
    panel = '\n'.join(f'- **{t}**' + ''.join(f"\n{'  ' * (n + 1)}- {s}" for n, s in subs) for t, subs in d['panel'])
    top = ', '.join(f'**{t}**' for t in d['top'])
    sim = ', '.join(f'{k} {v} s' for k, v in d['D'].items())

    return f"""# TileSmith {VERSION} - app specification for building a clone

Generated {TODAY} from TileSmith v{VERSION} (`app/index.html`). This file describes what the app does, how it looks,
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
  **Spout** (Windows) or **Syphon** (Mac), and can be recorded to video, exported as PNG, a PDF (full raster, spec sheet and cable labels) or
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
amber for the version). Header: "TileSmith v{VERSION}" and subtitle "LED Wall Pixel Map & Test Pattern Generator".

### 3.1 Left panel sections and submenus (in order)

Sections are collapsible `<details>`; submenus are nested collapsible blocks. Sections marked with the wall name edit
the selected wall.

{panel}

Visibility rules:
- Data wiring (inside LED processor) and all processor fields appear only when a processor other than None is picked;
  otherwise a hint "Pick a processor to see tiles per port and plan data wiring."
- Everything under Power except the "Power distribution" checkbox (including the Power wiring submenu) appears only
  when that box is ticked.
- Half-tile controls appear only when the wall's tile model has a half version (section 6).
- Tile-shade color appears directly under the Test pattern list, only for tileshade and tileshade-clean.
- Image fit appears only for image patterns; HAP type only for the HAP format; DVD controls only when DVD is on.

### 3.2 Top bar

Buttons: {top}. Then a red recording status, the zoom level (e.g. "41%") and an fps readout ("still" when nothing
moves). Resolume XML is a drop-down (One slice per LED wall / One slice per tile). "Start NDI®" toggles NDI; while
live it is green with a dot and reads "Stop NDI®". Right after it, "Start Spout" (Windows) or "Start Syphon" (Mac)
toggles that output the same way ("Stop Spout" / "Stop Syphon", green); the button is hidden in the web version and in a
desktop build made without the Spout/Syphon files. Short messages (NDI started/stopped/errors, Resolume saved, Next
pattern name) appear as a toast at the bottom centre for 2.5-9 s. In a cramped viewport (narrower than 640 px or a
window under 520 px tall) the top bar stays on one row and scrolls sideways.

### 3.3 Viewport (centre)

Shows the canvas scaled (zoom V.z, pan V.x/V.y) on a dark background with a drop shadow, a cyan outline around the
canvas, and an amber outline around each wall (solid for the selected wall when there are several, dashed otherwise).
No text labels around the canvas. The viewport is only a preview of the canvas; nothing drawn on the viewport overlay
goes to the output.

- Scroll wheel zooms around the pointer, 0.9x / 1.1x per notch, max 500%. Minimum = min(25%, 80% of the zoom that fits
  the canvas plus every wall in the viewport). At the minimum zoom everything is centred.
- Drag empty space to pan. Drag a wall to move it (unless an editing mode is on).
- Walls snap to canvas edges and other walls' edges within 10 screen px (magenta dashed guides while dragging); after
  dropping, overlapping walls are pushed apart to keep a {d['GAP']} px gap. Hold Alt to place freely.
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

### 3.4 Engineering panel (right)

Collapsible "Entire canvas" section then one section per wall, as two-column tables (label, value). Rows in section 9.

## 4. Data model and saved settings

Global settings live in one object `S`. Per-wall settings (keys marked "per wall") are copied between `S` and the
selected wall object whenever the selection changes, so the UI always edits `S`. State is saved (debounced 400 ms) as
JSON `{{sv:23, S:{{...}}, walls:[...], cur, crew, logo, dvd}}`: in localStorage key `tilesmith-state-v1` (web) or
`state.json` in the user data folder (desktop: `%APPDATA%/TileSmith`, `~/Library/Application Support/TileSmith`).
Images are stored as data URLs. On load, values are type-checked and clamped to their limits; walls that use a named
preset get the preset's current figures; legacy half marks are converted to a layout. "Reset saved settings" (Info
dialog) deletes the state and reloads.

### 4.1 Global settings

{glob}
### 4.2 Per-wall settings

{wall}
New wall ("Add wall"): copy of the selected wall's settings but 4x3, build from top-left horizontal, pattern = first of
{d['NEWPATS']} not used yet, tile-shade colour from {d['SHADES']} by index, name "Wall N". It is placed to the right of the
rightmost wall (2 px gap) if it fits on the canvas, else below the lowest wall, else offset 40 px. "Duplicate" copies
the wall (including manual wiring) and names it "... copy". "Remove" deletes the selected wall (at least one remains).
Canvas presets: {res}. "Fit canvas to walls" moves walls so none is left/above 0 and sets the canvas to their bounding
box (clamped 16-8192). Wall position buttons: Top-Left (0,0), Center Both, Top-Center, Bottom-Left, Bottom-Center.
Quick sizes: 4x3, 6x4, 8x5, 10x6, 16x9.

## 5. Tile models (presets)

Picking a preset fills tw, th, wmm, hmm, pitch, kg, wmax, dmm. Editing any of those switches the preset to "Custom".
Density = 1e6 / (pitch^2) px/m^2; Typical power = 40% of max. The list is grouped by manufacturer (Absen, Unilumin,
INFiLED, YES TECH; Custom last); ROE is split into one group per series (ROE Amber, ROE Black Marble, ... ROE Vanish Acoustics) in the order of the ROES array. YES TECH max watts = the higher W/m^2 figure on the spec sheet x cabinet area, rounded
up. ROE figures come from the cabinet pages on roevisual.com (per panel, as printed). 23 ROE models have a half panel (HALF table, 'h' = two halves stacked make the full tile).

{presets}
## 6. Wall shapes: removed tiles and half tiles

Every wall is a list of **pieces** computed from its settings (cached until the wall changes). Each piece has a key, a
pixel rectangle inside the wall (x, y, w, h), its anchor cell (col, row = the cell holding its top-left corner), a kind
(full, half, full on its side), its own spec (kg, W, m^2, mm) and a build order.

### 6.1 Plain grid with removed tiles (any model)

One full piece per cell except cells listed in `gone`. Remove tiles mode (Size of LED Wall submenu): press on a tile to
take it out, or on a removed spot to put it back; dragging applies the same choice to every cell crossed. "Restore all
tiles" clears the list. Tile IDs keep their grid numbers (T = row x cols + col + 1).

### 6.2 Half-tile layout (models with a half version)

{half}
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
plain grid (`lay = {{}}`). In Remove tiles mode on a layout: press on a piece removes the whole piece; press on an
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

Image fit modes: {', '.join(d['PFIT'])}. Stretch fills the wall; Fit inside keeps the aspect with black bars; Fill
crops edges; Original size on canvas draws the image 1:1 at the canvas origin (each wall shows the part under it);
Original size on wall draws it 1:1 at the wall's origin. Large walls render at a scale so the cached image stays under
25 MP. Scroll: directions {d['SCRV']}; speed = pspd x 0.2 x shorter side px/s; the image wraps around.

## 8. Test patterns

{pats}
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

{procs}
Pixels per port for the chosen frame rate (fps) and bit depth (bpc): v = px x hz / fps, then: brompton: x 8/bpc, and
/2 with ULL; novastar: above 8-bit use px10 x hz / fps if given, else v/2; fixed (HELIOS): x bpc_spec/bpc only when bpc
> spec; linear: x bpc_spec/bpc. Floor the result. "Reset to spec" restores it; editing makes the note say it was edited.
Tiles per port t = floor(pixels per port / (tw x th)).

**Patterns**: None, Snake (turns back at the end of each line), Linear (each line starts from the same side), Manual.
8 start choices (corner/direction): {wpat}. The picker shows 8 small icons (green start, red end).

{fills}
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
{d['PC']} by port, red #ff3b3b dashed when over capacity), width max(2, min(tw,th)/30), with a filled arrow head at
each segment midpoint; a filled circle badge "P#" at the first tile and a dark rounded square "R#" at the last.

## 11. Power

Tick **Power distribution** to enable and choose the Distribution cable (setting pdt). Usable watts per circuit = V x A x (0.8 if
"Load circuits to 80%"). Tiles per circuit t = floor(usable / wmax), capped by the power link limit if set. Note text:
"One 120 V 20 A circuit loaded to 80% supplies 1,920 W, enough for 12 tiles of ... at 150 W max each."

Circuits are numbered k = 1, 2, ... across walls; with n circuits per cable (Socapex 6, L14-30 2, L21-30 3) circuit k is on cable ceil(k/n) as leg (k-1) mod n (legs 1-6 for Socapex, X,Y for
L14-30, X,Y,Z for L21-30); labels cable-circuit with no type letter: 1-1 ... 1-6, 2-1 ... or 1-X, 1-Y, 2-X ... No phase is assigned (the PDU does that).
powerCON to Edison (n = 1, no PDU): every circuit is its own cable and is labelled just k (1, 2, 3 ...); cables needed = circuits, no spares. Selecting it sets pvolt 120 and pamps 15. Edison shows two extra
fields, "Edison plugs per wall circuit (0 = do not check)" (pwall) and "Wall circuit breaker (A)" (pwallA). With pwall > 0, plug k is on wall circuit ceil(k / pwall); its load in amps is watts / pvolt, summed per wall circuit and
compared with pwallA x (0.8 if "Load circuits to 80%"). Engineering rows: "Edison plugs needed", "Peak load per plug" ("plug 3 9.4 A"), and with pwall > 0 "Wall circuits needed", "Peak load per wall circuit" ("(over)" after any
over its limit) and "Wall circuit over capacity". Labels: one pair per circuit, tags "1/2 EDISON PLUG END" (lines "Edison plug k[, wall circuit g]", "to <wall> <tile> (col, row)", tiles/watts/volts/breaker) and
"2/2 POWERCON END" ("<wall> <tile> POWER IN", "from Edison plug k", tiles/watts); the Power labels select is hidden. Power wiring works
like data wiring with the same patterns, corners and areas (Fewest circuits / Whole rows or columns / One continuous
path), capacity t, plus the power link limit; on half-tile layouts by each piece's own watts (circuit full when watts >
usable or tiles > link limit). Manual: Wire tiles, New circuit, Undo, Clear; "This circuit is full (12 tiles)."

Canvas rows: Power distribution (the chosen cable type), Circuit "120 V · 20 A · loaded to 80% = 1,920 W usable",
Circuits used, Min. circuits if every circuit is full, <cable name> cables "2 (3 spare circuits)", Peak load per cable "cable 1 24.0 A · cable 2 12.0 A" (sum of circuit watts / V per cable), Over capacity.

**Drawing power runs**: dashed line (dash 3w gap 2w, w = max(2, min(tw,th)/36)) through tile centres, colour from
{d['POWC']} by circuit; start badge = dark rounded box with a lightning-bolt icon and the circuit number k; small
square at the last tile. When a wall shows both data and power: data runs at (centre x - 0.2 tile w, centre y), power
at (centre x + 0.2 w, centre y + 0.2 h), and power is white on a black casing (2.4x width) with white badges;
over-capacity circuits stay red. With only one shown, it runs through the centres in its own colours.

## 12. Build animation (technician)

Per wall a simulation steps through the pieces in build order (cells in order of the start corner and Horizontal/
Vertical placement; for half-tile layouts, pieces sorted by their anchor cell's order then unit position). Phases per
tile: {sim}, scaled by Speed and a per-wall rate from {d['RATES']} (wall index); wall i waits i x {d['STAG']} s before
starting. walkin: tech walks in from the wall edge carrying the tile; move: walks beside the slot; place: turns and
lifts the tile into place (tile scales from carry size to full); lock: tile flashes into place (a ring sparkle expands
from its centre) and the tile becomes lit; walkout: turns and walks off. Loop build restarts after Pause before restart.
The LED build submenu (Animation Options) has Start (clear all walls and play), Stop (stop and show every wall finished), Reset (clear all walls and wait) and Play/Pause (freeze and resume; the label follows S.play).

The technician is a flat vector person (hard hat, hi-vis vest with reflective band and logo text or image, skin tone,
hair colour, face photo optional, name tag) sized to fit inside the wall (size = min(2.4 x tile height, 42% of canvas
height, wall height/1.05, wall width/0.85)), clipped to the wall, standing beside the slot on the side he came from,
facing it, with both hands on the carried tile. The carried tile is a dark #1b2028 rectangle with a light frame,
amber corner marks and a black handle, at the piece's own size. Crew: {d['crew']} by default, editable (name, skin,
hair, face photo), rotating so one person is not on two walls at once.

## 13. DVD screensaver

A logo bounces inside each wall (or the whole canvas). Logo sprite height 200 px: TileSmith logo (5 squares mark +
"TILESMITH"), Text (bold, BOXFONT) or an uploaded image. With "Change color on each bounce" the sprite is recoloured
(source-in) to a random hue at least 70° from the previous one. Size = dvdSize% of the shorter side (max 95% of the
area). Speed = dvdSpeed x 0.25 x shorter side px/s. Start at a random point, angle 30-60°.

Corner hit chance: after every bounce, with probability dvdCorner% x {d['DVD_MAX']}, aim for a corner: unfold the
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

**NDI®** (desktop): sender name ndiName; frame rates {nfr}; frames are the canvas read back as RGBA and sent as RGBX
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
options") under Animation Options, after NDI® options: sender/server name shName (default TileSmith), "Frame rate when
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
publishImageData(Uint8ClampedArray rgba, {{x:0,y:0,width:w,height:h}}, {{width:w,height:h}}, flipped=false) per frame,
only while server.hasClients (the first frame always goes out), dispose() on stop. Packaging: Windows
resources/spout/SpoutDX.dll + Spout-licence.txt; Mac Contents/Resources/syphon.node (rpath @loader_path/../Frameworks)
and Contents/Frameworks/Syphon.framework, licences in Resources/syphon. Info dialog: "Spout and Syphon" credits with
licences (Simplified BSD, BSD, MIT) and "View Spout / Syphon licences". On Android there is no Spout or Syphon; leave
this submenu out (or offer NDI only).

**Video export** (desktop, needs ffmpeg with the encoder): records at 60 fps: Blank intro seconds of empty canvas, the
live build, then Final hold; stream raw RGBA frames to ffmpeg `-f rawvideo -pix_fmt rgba -s WxH -framerate 60 -i
pipe:0 [format args] -an out`. Saved to Videos/TileSmith (Windows) or Movies/TileSmith (Mac) as
tilesmith-build-YYYYMMDD-HHMMSS.ext. Click again to cancel. Estimated length is shown.

{codecs}
**Cable labels** (section "Label printing options", placed after Animation Options; the whole section is hidden unless
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
"""

def main():
    d = asyncio.run(collect())
    OUT.write_text(build(d), encoding='utf-8')
    print('wrote', OUT, OUT.stat().st_size // 1024, 'KB')

if __name__ == '__main__':
    main()
