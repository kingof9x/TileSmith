"""Builds TileSmith-Mobile-Manual.pdf, the user manual for the Android and iOS apps (separate from the desktop manual).

Screenshots come from make_kit_shots.py / make_kit_anims.py (kit/shots, the real page running as the Android app).
Pattern, wiring and fit descriptions are read from make_manual.py, so both manuals describe them in the same words.
  python3 make_mobile_manual.py            -> tilesmith-desktop/TileSmith-Mobile-Manual.pdf
  MOBILE_MANUAL_OUT=x.pdf python3 make_mobile_manual.py
"""
import ast, asyncio, base64, datetime, html, json, os, pathlib
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).parent
ROOT = pathlib.Path(__import__('os').environ.get('TILESMITH_ROOT', pathlib.Path(__file__).resolve().parent.parent / 'tilesmith-desktop'))
SHOTS = pathlib.Path(os.environ.get('KIT_SHOTS', HERE / 'kit' / 'shots'))
OUT = pathlib.Path(os.environ.get('MOBILE_MANUAL_OUT', ROOT / 'TileSmith-Mobile-Manual.pdf'))
VERSION = json.loads((ROOT / 'package.json').read_text())['version'].rsplit('.0', 1)[0]
TODAY = datetime.date.today().strftime('%B %-d, %Y')
E = html.escape

# the desktop manual's descriptions, read without running make_manual.py
_D = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse((HERE / 'make_manual.py').read_text()).body
      if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.endswith('_DESC')}
PATTERN_DESC, FIT_DESC, FILL_DESC, PFILL_DESC = _D['PATTERN_DESC'], _D['FIT_DESC'], _D['FILL_DESC'], _D['PFILL_DESC']
INDEX = {x['file']: x for x in json.loads((SHOTS / 'index.json').read_text())}


def img(name, cap='', w='100%', maxh=None):
    assert (SHOTS / name).exists(), f'missing screenshot {name}'
    b64 = base64.b64encode((SHOTS / name).read_bytes()).decode()
    st = f' style="max-height:{maxh}"' if maxh else ''
    return f'<figure style="width:{w}"><img src="data:image/png;base64,{b64}"{st}>' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'


def row(*figs):
    return '<div class="row">' + ''.join(figs) + '</div>'


def table(head, rows, cls=''):
    return f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'


def build():
    phone = sorted(f for f in INDEX if f.startswith('p0') and 'portrait' in f)
    pats = table(['Pattern', 'What it shows'], [[f'<b>{E(p)}</b>', d] for p, d in PATTERN_DESC.items()])
    fits = table(['Image fit', 'What it does'], [[f'<b>{E(f)}</b>', d] for f, d in FIT_DESC.items()])
    fills = table(['Data wiring preference', 'How tiles are shared between ports'], [[f'<b>{E(f)}</b>', d] for f, d in FILL_DESC.items()])
    pfills = table(['Wiring preference', 'How tiles are shared between circuits'], [[f'<b>{E(f)}</b>', d] for f, d in PFILL_DESC.items()])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>TileSmith {VERSION} Mobile App Manual</title><style>
@page{{size:Letter;margin:18mm 17mm 20mm}}
:root{{--ac:#0e7c86;--am:#c27c00;--ink:#16202a;--mu:#5b6b7a;--ln:#d7dee5}}
body{{font-family:Inter,'DejaVu Sans',sans-serif;color:var(--ink);font-size:10.2pt;line-height:1.5;margin:0}}
h1{{font-size:20pt;margin:0 0 6pt;letter-spacing:-.01em;break-after:avoid}} h2{{font-size:13pt;margin:14pt 0 5pt;color:var(--ac);break-after:avoid}} h3{{font-size:11pt;margin:10pt 0 4pt;break-after:avoid}}
section.chap{{break-before:page}} p{{margin:0 0 7pt}} ul,ol{{margin:0 0 8pt;padding-left:18pt}} li{{margin:0 0 3pt}}
figure{{margin:6pt 0 10pt;break-inside:avoid}} figure img{{width:auto;max-width:100%;max-height:112mm;border:1px solid var(--ln);border-radius:4px;display:block;margin:0 auto}} figcaption{{font-size:8.6pt;color:var(--mu);margin-top:3pt;text-align:center}}
.row{{display:flex;gap:10pt;align-items:flex-start;break-inside:avoid}} .row figure{{flex:1}} .row figure img{{max-height:150mm}}
.side{{display:grid;grid-template-columns:1fr 44%;gap:14pt;align-items:start}} .side figure img{{max-height:150mm}}
table{{width:100%;border-collapse:collapse;margin:4pt 0 10pt;font-size:9.2pt}} th{{text-align:left;background:#eef3f6;border-bottom:1.5px solid var(--ln);padding:4pt 6pt}} td{{border-bottom:1px solid var(--ln);padding:4pt 6pt;vertical-align:top}}
table.small{{font-size:8.4pt}} tr{{break-inside:avoid}} code{{font-family:'DejaVu Sans Mono',monospace;font-size:8.6pt;background:#f1f4f6;padding:0 3px;border-radius:3px}}
.note{{border-left:3px solid var(--am);background:#fff8ea;padding:6pt 9pt;margin:6pt 0 10pt;break-inside:avoid}} .key{{font-weight:600;color:var(--ac)}}
.cover{{height:236mm;display:flex;flex-direction:column;justify-content:center}} .cover .mark{{width:64px;height:64px;margin-bottom:18pt}} .cover h1{{font-size:34pt;margin:0}} .cover .sub{{font-size:15pt;color:var(--mu);margin:4pt 0 24pt}}
.toc ol{{columns:2;column-gap:22pt;padding-left:16pt}} .toc li{{margin-bottom:4pt}}
.gest{{display:grid;grid-template-columns:auto 1fr;gap:4pt 12pt;margin:4pt 0 10pt}} .gest b{{color:var(--ac)}}
</style></head><body>
<div class="cover"><svg class="mark" viewBox="0 0 10 10"><rect width="10" height="10" rx="2" fill="#0f1720"/><g fill="#22a0ac"><rect x="1.5" y="1.5" width="2.2" height="2.2"/><rect x="6.3" y="1.5" width="2.2" height="2.2"/><rect x="3.9" y="3.9" width="2.2" height="2.2"/><rect x="1.5" y="6.3" width="2.2" height="2.2"/></g><rect x="6.3" y="6.3" width="2.2" height="2.2" fill="#ffb300"/></svg>
<h1>TileSmith Mobile</h1><div class="sub">LED Wall Pixel Map &amp; Test Pattern Generator · Android and iOS app manual</div>
<p><b>Version {VERSION}</b> · {TODAY}</p><p>Concept and development: Callum Davenport-Lambton · tilesmithapp@gmail.com</p>
<p style="color:var(--mu);margin-top:30pt;max-width:125mm">Lay out LED walls, test patterns and pixel maps, plan data and power wiring, and watch an animated technician build the wall. On your tablet or phone, offline, with files and videos you can share straight from the device.</p>
<p style="color:var(--mu);font-size:8.5pt;margin-top:40pt">This manual covers the mobile app. The Windows and Mac desktop app has its own manual (TileSmith-Manual.pdf).<br>NDI® is a registered trademark of Vizrt NDI AB. <a href="https://ndi.video/">ndi.video</a></p></div>

<section class="chap toc"><h1>Contents</h1><ol>
<li>The mobile app</li><li>Installing</li><li>The screen</li><li>Touch controls</li><li>Quick start</li><li>Canvas and LED walls</li><li>Tile model, size and shape</li><li>Test patterns and overlays</li><li>LED processor and data wiring</li><li>Power and power wiring</li><li>Engineering panel</li><li>Build animation and technician</li><li>DVD screensaver</li><li>Saving and sharing files</li><li>Recording a video</li><li>Info, saving and resetting</li><li>Battery and speed tips</li><li>Troubleshooting</li><li>Credits</li></ol></section>

<section class="chap"><h1>1. The mobile app</h1>
<p>TileSmith Mobile is the TileSmith LED wall tool on Android and iOS tablets and phones. It runs the <b>same TileSmith page</b> as the desktop and web versions, so the canvas, walls, tile models, test patterns, engineering, wiring, power and the build animation are identical: the same layout gives the same picture and the same numbers on a tablet as on the desktop. Everything works offline and is saved on the device automatically.</p>
{table(['', 'Mobile app', 'Desktop app (Windows, Mac)'], [
 ['Canvas, walls, presets, patterns, engineering, wiring, power, build animation, DVD screensaver', 'Yes', 'Yes'],
 ['Export PNG, PDF, Resolume XML', 'Yes: through the share sheet (Files, Drive, AirDrop, e-mail …)', 'Yes: saved to folders'],
 ['Export video', 'H.264 MP4, recorded in real time with the device\'s encoder', 'HAP, H.264, H.265, ProRes 422 HQ, ProRes 4444 (ffmpeg)'],
 ['Video export: DVD logo (perfect loop video)', 'No', 'Yes'],
 ['NDI® output, Spout (Windows), Syphon (Mac)', 'No (buttons and menus hidden)', 'Yes'],
 ['Touch: pinch to zoom, two-finger pan', 'Yes', 'Windows touch screens'],
])}
<div class="note">Tablets give the most room. On a phone the panels stack under each other and you scroll between them (chapter 3). A dedicated phone layout is planned.</div></section>

<section class="chap"><h1>2. Installing</h1>
<p>TileSmith Mobile is built from the TileSmith project. It is not in the app stores yet.</p>
<h2>Android (Android 7.0 or newer)</h2>
<ul><li><b>From the project's mobile folder</b> (Capacitor): follow <b>BUILD-ANDROID.txt</b>. You need Node.js and Android Studio; plug in your device and press Run.</li>
<li><b>From Google AI Studio</b>: follow <b>00-START-HERE.md</b> in the AI Studio kit. AI Studio builds a small Android app around the same TileSmith page, and it can install it on a USB-connected phone from the browser. The kit's <code>android-project</code> folder is the same app, ready for Android Studio.</li></ul>
<p>Both builds behave as this manual describes. They have different app IDs, so you can install both side by side and compare them. For video recording, keep <b>Android System WebView</b> and <b>Chrome</b> up to date from Google Play.</p>
<h2>iPhone and iPad (iOS / iPadOS 15 or newer)</h2>
<p>Follow <b>BUILD-IOS.txt</b>. You build on a Mac with Xcode and sign with your Apple ID. With a free Apple ID the app runs for 7 days, then needs installing again from Xcode; the paid Apple Developer Program removes that limit and adds TestFlight.</p>
<p>The header shows the version (<b>v{VERSION}</b>), so you can check which build you are running.</p></section>

<section class="chap"><h1>3. The screen</h1>
<p>On a <b>tablet</b>, or any screen wider than 900 points, TileSmith shows three columns:</p>
<ul><li><b>Settings</b> on the left, in collapsible sections. It scrolls on its own.</li>
<li>The <b>top bar</b> of actions and the <b>viewport</b> in the middle. The viewport is a preview of the master canvas: the picture your LED processor or media server would get.</li>
<li><b>Engineering</b> on the right.</li></ul>
{img('t01-first-launch.png', 'Tablet, landscape: a new install shows one 6 × 4 wall on a 1920 × 1080 canvas.')}
<p>On a <b>phone</b> the three parts stack. Scroll down past the settings to reach the top bar and viewport, then the engineering tables. Turning the phone sideways shows the three columns, side by side but narrow.</p>
{row(*[img(f, f'Phone, screen {i + 1}', maxh='120mm') for i, f in enumerate(phone[:3])])}
<p>The app follows the system <b>light or dark</b> setting.</p>
{row(img('t21-light-theme.png', 'Light theme'), img('p90-phone-landscape.png', 'Phone in landscape'))}
<h2>Top bar</h2>
{img('ui-top-bar.png', 'Top bar. It scrolls sideways when it does not fit.')}
{table(['Button', 'What it does'], [
 ['<b>ⓘ Info</b>', 'About TileSmith, credits, contact, Ko-fi and Reset saved settings (chapter 16).'],
 ['<b>Save</b> and <b>Open</b>', 'Next to New Project. Save keeps the whole project, with your images and crew, in one .tilesmith file; Open loads one.'],
 ['<b>Center canvas</b>', 'Centres the canvas in the viewport.'],
 ['<b>Show entire canvas</b>', 'Fits the whole canvas in the viewport again.'],
 ['<b>New Project</b>', 'Asks first, then wipes everything and starts a blank canvas. Undo brings it back.'],
 ['<b>Undo</b>', 'Opens a list of the last 20 changes; tap one to go back to just before it. The first item can be <i>Redo</i>.'],
 ['<b>Next pattern</b>', 'Moves the selected wall to the next test pattern; a message at the bottom names it.'],
 ['<b>Export PNG / Export PDF</b>', 'Save the canvas picture, or one PDF with the full raster, the spec sheet and the cable labels (chapter 14).'],
 ['<b>Resolume XML ▾</b>', 'Saves a Resolume Arena Advanced Output preset: One slice per LED wall or One slice per tile.'],
])}
<p>Next to the buttons: a red recording status, the zoom level and how many frames per second the canvas draws (<i>still</i> when nothing moves).</p></section>

<section class="chap"><h1>4. Touch controls</h1>
<div class="gest">
<b>Tap</b><span>Buttons, checkboxes and lists, as usual. Tap a wall in the viewport to select it.</span>
<b>One finger on a wall</b><span>Drag it. It snaps to the canvas edges and to other walls, keeping a 2 px gap.</span>
<b>One finger, editing modes</b><span>In <i>Wire tiles</i>, <i>Remove tiles</i> and <i>Mark half tiles</i>, tapping and dragging edit the selected wall instead of moving it.</span>
<b>One finger on empty space</b><span>Pans the viewport.</span>
<b>Two fingers</b><span>Pinch to zoom (up to 500%) around your fingers, and move to pan. Only the viewport zooms, never the whole screen.</span>
<b>Scroll</b><span>Swipe the settings or engineering panel to scroll it. On a phone, swipe outside the viewport to scroll the page.</span>
<b>Show entire canvas</b><span>Brings the whole canvas back into view.</span></div>
<p>Text and number fields open the keyboard. Colour fields open the system colour picker. Upload fields open the photo picker or file browser. Web links, Ko-fi and e-mail open in your browser or mail app.</p></section>

<section class="chap"><h1>5. Quick start</h1><ol>
<li><span class="key">Canvas</span>: tap the canvas size your media server outputs, for example <b>1080p Full HD</b>.</li>
<li><span class="key">Tile model</span> and <span class="key">Size of LED Wall</span>: choose your tile preset, then columns and rows.</li>
<li><span class="key">Test pattern</span>: choose a pattern, or tap <b>Next pattern</b> to step through them.</li>
<li><span class="key">Engineering › LED processor</span>: choose your processor, then a pattern under <span class="key">Data wiring</span>.</li>
<li><span class="key">Engineering › Power</span>: tick <b>Power distribution</b>, then a pattern under <span class="key">Power wiring</span>.</li>
<li>Open <b>Animation Options › LED build</b> and tap <b>Start</b> to watch the technician build the wall, or open <b>Video export</b> and tap <b>Export video</b> to record it.</li>
<li>Tap <b>Export PNG</b> or <b>Export PDF</b> and pick where the file goes.</li></ol>
{img('t02-two-walls-data.png', 'Two walls, a NovaStar VX1000 Pro and Snake data wiring.')}</section>

<section class="chap"><h1>6. Canvas and LED walls</h1>
<div class="side"><div><p><b>Canvases</b> lists every output raster; <b>Add canvas</b> makes another, each with its own submenu of LED wall options and its own outputs, shown side by side in the viewport (tap one to select it). Each canvas sets its output raster: Width and Height in pixels, or a preset (1080p Full HD, 4K UHD, 2K DCI, 4K DCI, 720p HD, 32:9 Banner). <b>Fit canvas to walls</b> moves the walls to the top-left and makes the canvas exactly as big as they are.</p>
<p><b>LED walls</b> lists every wall with its size, pixels, position and pattern. Tap a wall to select it; the selected wall has an amber border. <b>Add wall</b> places a new 4 × 3 wall beside the others. <b>Duplicate</b> copies the selected wall, and <b>Remove</b> deletes it (one wall always stays).</p>
<p>Sections marked with a wall's name (for example <i>Tile model · Main</i>) change the selected wall only. <b>Tech starts at</b> and <b>Tile placement</b> set where the technician begins and whether he builds row by row (Horizontal) or column by column (Vertical).</p></div>
{img('ui-led-walls.png', 'LED walls')}</div>
{img('cv-three-walls.png', 'Three walls on one canvas, each with its own pattern. With several walls, tile IDs start with W1, W2 …')}
<h2>Wall position</h2><div class="side"><div><p>Type <b>Offset X</b> and <b>Offset Y</b> in canvas pixels, or tap an alignment button: Top-Left, Center Both, Top-Center, Bottom-Left, Bottom-Center. You can also drag the wall in the viewport.</p></div>{img('ui-position.png', 'Wall position')}</div></section>

<section class="chap"><h1>7. Tile model, size and shape</h1>
<div class="side"><div><p><b>Tile model</b> has a <b>Brand</b> menu (ROE, Absen, Unilumin, INFiLED, YES TECH, Owl Vision) and a <b>Model</b> menu for that brand. The model fills in the tile's pixels, millimetres, pitch, weight, max watts and depth. Change any of them and the model becomes <b>Custom</b>. Pick <b>Custom</b> in Brand, fill in the fields, name it and press <b>Save as my preset</b> to keep it for later; it is also saved inside any project that uses it.</p>
<p><b>Size of LED Wall</b> sets Columns and Rows, with quick buttons 4×3, 6×4, 8×5, 10×6 and 16×9.</p></div>{img('ui-tile-model.png', 'Tile model')}</div>
<h2>Removing tiles</h2><p>For a wall that is not a rectangle, tap <b>Remove tiles</b> (Size of LED Wall). Then tap tiles in the viewport to take them out or put them back, or drag across several. Removed spots show a red ✕ in the viewport only, never in the output. <b>Restore all tiles</b> puts them all back.</p>
{row(img('t10-remove-tiles.png', 'Remove tiles mode'), img('cv-removed-tiles.png', 'The output: six corner tiles removed'))}
<h2>Half tiles</h2><p>Some models also come as a half tile (ROE Carbon CB3/CB5/CB8, YES TECH MU 500×1000, YES TECH MT II 1000×500). For these, the <b>Size of LED Wall</b> submenu shows <b>Convert bottom row to half tiles</b> and <b>Convert top row to half tiles</b> (tap again to restore full tiles) and <b>Mark half tiles</b>. While marking, a red <b>STOP MARKING HALF TILES</b> button sits at the top of the viewport. Tap in the viewport:</p>
<ul><li>Tap one half of a full tile to keep just that half.</li><li>Tap an empty half to put a half tile there.</li>
<li>Tap the line between two half tiles to join them into a full tile. This works upright, offset by half a tile, or on its side (ROE frames).</li><li>Tap a half tile to take it out.</li></ul>
<p>Drag to repeat the first tap's action. <b>Clear half tiles</b> goes back to full tiles.</p>
{row(img('t11-half-tiles.png', 'Mark half tiles (ROE Carbon CB5)'), img('cv-half-tiles.png', 'The output; half tiles end in ½'))}</section>

<section class="chap"><h1>8. Test patterns and overlays</h1>
<div class="side"><div><p>Choose the pattern for the selected wall under <b>Test pattern</b>. <b>Tile-shade color</b> appears for tileshade and tileshade-clean. For image patterns, <b>Image fit</b> decides how the picture fills the wall. <b>Scroll</b> moves any pattern diagonally, sideways or down, at <b>Scroll speed</b>. <b>Upload test pattern</b> opens the photo picker for the <i>custom</i> pattern. The branded patterns have a centre box for your own text or logo.</p></div>{img('ui-test-pattern.png', 'Test pattern')}</div>
{img('cv-patterns-all.png', 'All 25 patterns (overlays off)')}
{pats}
{fits}
<h2>Tile borders &amp; overlays</h2><div class="side"><div><p>Set the border colour and thickness, and turn on:</p><ul><li>the tile position arrows (↑ row counted from the bottom, → column from the left);</li><li>tile IDs, such as T05 [C5:R1];</li><li>pixel addresses;</li><li>tile sizes in mm.</li></ul></div>{img('ui-borders.png', 'Tile borders & overlays')}</div>
{img('cv-overlays-all.png', 'Every overlay on')}</section>

<section class="chap"><h1>9. LED processor and data wiring</h1>
<div class="side"><div><p>Choose your <b>Processor</b> (Brompton, NovaStar, Megapixel HELIOS, ROE Evision or Custom). The list only offers processors the maker lists for the selected tile (from ROE Visual's brochures; unlisted tiles are not restricted). <b>Receiving card in the tile</b> narrows it further and <b>Show incompatible processors</b> lifts the limit; a processor you already chose stays selected, with a warning naming any wall whose tile does not list it. TileSmith works out the <b>Pixels per port</b> for the frame rate and bit depth, and from that how many tiles one port can drive. <b>Reset to spec</b> restores the figure after you edit it. Data wiring appears once a processor is chosen.</p>
<p><b>Data wiring</b>: choose a Pattern (Snake, Linear or Manual) and one of the 8 start icons (green start, red end). Then choose a <b>Data wiring preference</b>. <b>Show data paths</b> draws the ports on the canvas, P1 to R1 and so on; a port over capacity is drawn dashed red.</p></div>{img('ui-data-wiring.png', 'Data wiring')}</div>
{fills}
{img('cv-data-wiring-all.png', 'The five preferences on a 10 × 5 wall, 17 tiles per port')}
<h2>Manual wiring</h2><ol><li>Set Pattern to <b>Manual</b> and tap <b>Wire tiles</b>.</li><li>Tap tiles in data order, or drag across them. Drag back to take tiles off again; tap the last tile to carry on from it. A port stops taking tiles when it is full.</li><li><b>New port</b> starts the next port, <b>Undo</b> removes the last tile, <b>Clear</b> starts again. Tap <b>Stop wiring</b> when you are done.</li></ol>
{img('t06-manual-data-wiring.png', 'Manual wiring: P1 is full, P2 is being drawn')}</section>

<section class="chap"><h1>10. Power and power wiring</h1>
<div class="side"><div><p>Tick <b>Power distribution</b> (Socapex, L14-30, L21-30 or powerCON to Edison cables) to see the power options. Set the circuit voltage, the breaker size and whether circuits are loaded to 80%; TileSmith shows how many tiles one circuit can supply. <b>Power link limit</b> caps the tiles per circuit. <b>Power wiring</b> works like data wiring, with circuits 1-1 … 1-6, 2-1 … (or 1-X, 1-Y … for twist-lock cables). Phases are left to the distro.</p></div>{img('ui-power-wiring.png', 'Power wiring')}</div>
{pfills}
{img('cv-power-wiring-all.png', 'The five preferences on a 10 × 5 wall, 16 tiles per circuit')}
{img('cv-data-and-power.png', 'Data and power together: power is drawn white on black, with lightning-bolt badges')}</section>

<section class="chap"><h1>11. Engineering panel</h1>
<div class="side"><div><p>The engineering panel (on the right on a tablet, at the bottom on a phone) shows totals for the <b>Entire canvas</b> and for each wall. The canvas section covers canvas and LED pixels, area, weight, peak and typical power, processor ports and processors needed, and with power on, circuits, Socapex cables and peak load per phase. Each wall section covers its tile model, wall pixels, position, tiles, size in metres and feet, area, weight, power, tiles per port or circuit, minimum ports and circuits, and its data and power paths.</p>
<p>Tap a section heading to fold it. The same tables go into the spec sheet pages of the exported PDF.</p></div>{img('ui-engineering-panel.png', 'Engineering', maxh='150mm')}</div></section>

<section class="chap"><h1>12. Build animation and technician</h1>
<p>Under <b>LED build</b> tap <b>Start</b> and a technician builds each wall tile by tile. He walks in carrying the tile, lifts it into its slot and locks it with a flash, then walks off while the next crew member brings the next tile. Each tile takes about 4.8 seconds at Speed 1. Several walls are built at the same time, each starting 0.6 s after the one before.</p>
{img('anim-build-strip.png', 'One tile, every 0.2 s')}
<div class="side"><div><h2>LED build</h2><p><b>Start</b>, <b>Stop</b> (shows the finished walls), <b>Reset</b> and <b>Play / Pause</b>. <b>Speed</b> (0.25× to 5×). <b>Loop build</b> restarts after <b>Pause before restart</b> seconds, which is handy on a display.</p>
<h2>Technician</h2><p>Pick a <b>Character style</b>: Classic or Character pack (your own artwork, cut into parts to the Character Pack art brief and loaded as a zip). Choose the hard hat and vest colours and the vest logo text, or upload a logo. With <b>Crew details &amp; name tags</b> on, each crew member has a name, skin tone, hair colour and an optional face photo, and wears a name tag. The crew take turns.</p></div>{img('ui-technician.png', 'Technician', maxh='140mm')}</div>
{img('anim-tech-looks.png', 'Hard hat, vest and logo options')}</section>

<section class="chap"><h1>13. DVD screensaver</h1>
<div class="side"><div><p>Under <b>Animation Options › DVD screensaver</b>, a logo bounces inside each wall or across the whole canvas. It can be the TileSmith logo, your text or an uploaded image. Set the size, the speed and the <b>corner hit chance</b>. <b>Change color on each bounce</b> gives the logo a new colour at every wall. <b>Perfect loop</b> makes the motion repeat exactly after the loop length. The loop-video export is a desktop feature.</p></div>{img('ui-dvd.png', 'DVD screensaver', maxh='130mm')}</div>
{img('anim-dvd-strip.png', 'The logo changing colour at each bounce')}</section>

<section class="chap"><h1>14. Saving and sharing files</h1>
<p>Export PNG, Export PDF and Resolume XML open the device's <b>share sheet</b>, where you pick where the file goes: Files, Google Drive, iCloud Drive, AirDrop, Quick Share, e-mail, a messaging app and so on.</p>
<ul><li>When you pick an app, TileSmith says <i>Saved …</i>. If you close the sheet, it says <i>Not saved: …</i> and nothing is kept.</li>
<li><b>Export PNG</b>: <code>tilesmith-canvas.png</code>, the full canvas at its real size.</li>
<li><b>Export PDF</b>: <code>TileSmith-WxH-date.pdf</code>. Page 1 is the full raster, then the spec sheet with every engineering figure, then the cable labels (one page per label sheet, at your label size). It opens in any PDF viewer.</li>
<li><b>Save label sheet</b> (Label printing options, shown once data or power wiring is defined): <code>tilesmith-cable-labels.html</code>, a sheet of labels for both ends of every data and power cable. Open it in a browser and print it at 100% scale on Avery 5160, 5163, L7160 or roll labels.</li>
<li><b>Resolume XML</b>: <code>tilesmith-WxH.xml</code>. Copy it to <i>Documents/Resolume Arena/Presets/Advanced Output</i> on the computer that runs Resolume, then pick it in Arena's Advanced Output.</li></ul>
{row(img('t19-saved-toast.png', 'After Export PNG'), img('t17-resolume-menu.png', 'Resolume XML menu'))}
</section>

<section class="chap"><h1>15. Recording a video</h1>
<div class="side"><div><p><b>Export video</b> (with <b>LED build</b> ticked) records the master canvas as an <b>H.264 MP4</b> at 60 frames per second, using the device's own video encoder. The recording has three parts: the <b>Blank intro</b>, then the live build, then the <b>Final hold</b> of the finished walls. The estimated length is shown under the settings.</p>
<ol><li>Set Blank intro and Final hold (Video export).</li><li>Tap <b>Export video</b>. The top bar shows <i>● REC blank</i>, then <i>building</i>, then <i>hold</i>.</li><li>Keep TileSmith open. The screen stays on while it records.</li><li>When it finishes, the share sheet opens with <code>tilesmith-build-YYYYMMDD-HHMMSS.mp4</code>. On iPhone and iPad, <i>Save Video</i> puts it in Photos. On Android, choose Photos, Drive or Files.</li></ol>
<p>Tap <b>Export video</b> again while it records to cancel.</p></div>{img('ui-video-export.png', 'Video export (mobile)')}</div>
{row(img('t14-recording.png', 'Recording'), img('t15-recording-saved.png', 'Saved'))}
<div class="note">The video is recorded in real time, so switching apps or locking the device interrupts it. Large canvases on older devices can drop frames. If that happens, tap <b>Fit canvas to walls</b> or choose a smaller canvas, and keep the device on its charger. HAP and ProRes need the desktop app.</div></section>

<section class="chap"><h1>16. Info, saving and resetting</h1>
<div class="side"><div><p><b>ⓘ Info</b> shows the version, credits, the contact address and the Ko-fi link to support the project. <b>Reset saved settings</b> goes back to the defaults after you confirm.</p>
<p>Everything you set up (walls, patterns, wiring, crew, uploaded pictures) is <b>saved automatically</b> on the device and comes back the next time you open TileSmith. Installing a newer build keeps it. Uninstalling the app deletes it.</p>
<p><b>Moving to another device:</b> use <b>Save</b> to write a project file and open it on the other device; it carries the walls and wiring plus every custom tile and NovaStar receiving card file the walls use, and adds them to that device's library. A full Backup and Restore feature for all settings is planned for a later version.</p></div>{img('ui-info-dialog.png', 'Info')}</div></section>

<section class="chap"><h1>17. Battery and speed tips</h1><ul>
<li>When nothing moves, TileSmith stops drawing (the top bar says <i>still</i>). The build animation, the DVD screensaver, sweep and scrolling patterns keep it drawing.</li>
<li>Big canvases (4K and more) and many walls take more work. <b>Fit canvas to walls</b> removes empty canvas.</li>
<li>For long recordings or a looping display, keep the device on its charger.</li>
<li>Tablets give the most room. On a phone, landscape shows all three columns at once.</li></ul></section>

<section class="chap"><h1>18. Troubleshooting</h1>{table(['Problem', 'What to do'], [
 ['Export video says this device cannot record MP4 video', 'Android: update <b>Android System WebView</b> and <b>Chrome</b> from Google Play (Android 7 cannot get a new enough version). iPhone and iPad: update iOS / iPadOS.'],
 ['A save does nothing, or says <i>Not saved</i>', 'Pick an app in the share sheet (Files, Drive …). Closing the sheet cancels the save.'],
 ['The video stopped, froze or is shorter than expected', 'Keep TileSmith open and on screen while it records. Switching apps or locking the device interrupts the recording.'],
 ['Pinch zooms the whole page instead of the canvas', 'Pinch inside the viewport. If the whole page still zooms, the build is missing its mobile setup: rebuild with the project\'s scripts (npm run android / npm run ios, or prepare-assets.js for the AI Studio build).'],
 ['The app shows "The TileSmith page is not in this app yet"', 'AI Studio build: copy android-assets/tilesmith into app/src/main/assets/ (see 00-START-HERE.md in the AI Studio kit).'],
 ['Everything is tiny on a phone', 'Use landscape, zoom the viewport with two fingers, or use a tablet. A phone layout is planned.'],
 ['iPhone/iPad app stops opening after a week', 'Free Apple ID builds expire after 7 days. Run it again from Xcode (BUILD-IOS.txt).'],
 ['Settings are wrong after testing', 'ⓘ Info › Reset saved settings.'],
 ['No Start NDI® button', 'NDI®, Spout and Syphon are desktop features. Use the Windows or Mac app for live output.'],
])}
<p>Build problems are covered in BUILD-ANDROID.txt, BUILD-IOS.txt and the AI Studio kit's 00-START-HERE.md.</p></section>

<section class="chap"><h1>19. Credits</h1>
<p>TileSmith: concept and development by <b>Callum Davenport-Lambton</b> · tilesmithapp@gmail.com · support the project at <b>ko-fi.com/kingof9x</b>.</p>
<p>The mobile app is built with Capacitor (Android and iOS) or, for the Google AI Studio build, Kotlin with Jetpack Compose and AndroidX WebKit.</p>
<p>NDI® is a registered trademark of Vizrt NDI AB (<a href="https://ndi.video/">ndi.video</a>, tools at <a href="https://ndi.video/tools/">ndi.video/tools</a>). NDI® output is part of the desktop app and is not included in the mobile app.</p></section>
</body></html>"""


async def main():
    page_html = build()
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.set_content(page_html, wait_until='load'); await pg.wait_for_timeout(500)
        foot = f'<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#7a8896;width:100%;padding:0 17mm;display:flex;justify-content:space-between"><span>TileSmith v{VERSION} · Mobile App Manual</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
        await pg.pdf(path=str(OUT), format='Letter', print_background=True, display_header_footer=True, header_template='<div></div>', footer_template=foot,
                     margin={'top': '18mm', 'bottom': '20mm', 'left': '17mm', 'right': '17mm'})
        await b.close()
    print('wrote', OUT, OUT.stat().st_size // 1024, 'KB')

if __name__ == '__main__':
    asyncio.run(main())
