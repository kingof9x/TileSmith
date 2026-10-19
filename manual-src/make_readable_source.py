"""Readable copy of the TileSmith page for porting: splits app/index.html into index.html + style.css + app.js, moves
the embedded test-pattern pictures out to images/, formats the code with Prettier and writes FUNCTIONS.md, an index of
every top-level function with its line number in app.js.

  python3 make_readable_source.py <out-folder>

The exact app is still the single file app/index.html; this copy is for reading (the images are loaded from files, so
opened straight from disk the PNG export of image patterns can be blocked by the browser).
"""
import json, pathlib, re, subprocess, sys

PROJ = pathlib.Path('/home/claude/tilesmith-desktop')
PRETTIER = pathlib.Path(__file__).parent / 'tools' / 'node_modules' / '.bin' / 'prettier'   # npm install in tools/

# what the main functions do (shown in FUNCTIONS.md); everything else is listed by name only
ROLE = {
 'render': 'Draws the whole master canvas (the output raster) for one frame: walls, patterns, overlays, data/power paths, technicians, lock sparkles.',
 'tick': 'One animation step: advances time T, the build simulation, the DVD logo and time-based patterns, and redraws when something moves.',
 'loop': 'requestAnimationFrame loop at up to 60 fps (the output timer takes over while NDI/Spout/Syphon run on desktop).',
 'step': 'Advances every wall\'s build simulation by dt seconds (and the loop-build pause).',
 'stepSim': 'Build state machine for one wall: wait → walkin → move → place → lock → walkout → next tile.',
 'mkSim': 'New build simulation state for wall i (staggered start delay, per-wall rate).',
 'reset': 'Starts the build from an empty wall on every wall.',
 'showAll': 'Shows every wall finished (the LED build Stop button).',
 'drawWallTech': 'Positions the technician and the carried tile for the current phase (walk in, move, place, lock, walk out) and calls drawTech.',
 'worker': 'Draws the technician (flat vector person) at feet position x,y with size s and pose o (facing angle, gait, arms, carry, lock, hands).',
 'drawTech': 'Calls worker().',
 'cab': 'Draws the carried tile (dark face, frame, amber corner marks, handle).',
 'techBox': 'Technician size and the wall rectangle he is clipped to.',
 'pat': 'Draws a wall\'s test pattern (all patterns, image fit, scroll).',
 'vpDraw': 'Draws the viewport: the master canvas scaled by zoom/pan, canvas and wall outlines, editing marks, snap guides.',
 'fit': 'Zoom and pan so the canvas fits the viewport.',
 'pieces': 'The wall as a list of physical tiles (pieces): plain grid minus removed tiles, or the half-tile layout.',
 'autoChains': 'Automatic data/power chains for Snake/Linear patterns with the five wiring preferences.',
 'blockGrid': 'Fewest ports / Whole rows: picks the block grid that uses the fewest chains.',
 'portPlan': 'Data ports (P#/R#) for every wall, numbered across walls, with over-capacity flags.',
 'powerPlan': 'Power circuits for every wall, numbered across walls, with watts; cables are Socapex, L14-30 or L21-30 (no phases).',
 'pickCrew': 'Picks the next crew member for a wall, never one already busy on another wall.',
 'dvdStep': 'Moves the DVD logo(s) (free bounce or perfect loop).',
 'dvdRun': 'Free bounce for one area: move, detect wall/corner hits, recolour.',
 'dvdLoopPlan': 'Perfect loop plan: m, n crossings so position and colour repeat after the loop length.',
 'dvdSpr': 'Builds (and caches) the logo sprite, recoloured to a hue.',
 'exportPDF': 'Builds the Export PDF file: full raster page, spec sheet pages, cable label pages (own PDF writer).',
 'saveNow': 'Saves all settings as JSON (localStorage in the browser and mobile app).',
 'loadState': 'Loads and validates saved settings.',
 'sync': 'Copies settings into the panel inputs and refreshes the engineering panel.',
 'storeWall': 'Copies the per-wall settings from S into the selected wall.',
 'loadWall': 'Copies the selected wall\'s settings into S.',
 'recStartMR': 'Mobile app: records the master canvas with MediaRecorder (H.264 MP4) and streams it to a file.',
 'mobSave': 'Mobile app: saves a file through the share sheet (window.TSM.saveFile).',
}


def main(out):
    out = pathlib.Path(out); (out / 'images').mkdir(parents=True, exist_ok=True)
    s = (PROJ / 'app' / 'index.html').read_text()
    a = s.index('<script>') + len('<script>'); b = s.rindex('</script>')
    js = s[a:b]
    st0 = s.index('<style>') + len('<style>'); st1 = s.index('</style>')
    css = s[st0:st1]
    head = s[:s.index('<style>')]
    body = s[st1 + len('</style>'):s.index('<script>')]
    # embedded pictures -> files
    names = {}
    def img(m):
        key, data = m.group(1), m.group(2)
        fn = re.sub(r'[^a-z0-9]+', '-', key.lower()).strip('-') + '.png'
        (out / 'images' / fn).write_bytes(__import__('base64').b64decode(data))
        names[key] = fn
        return f"'{key}':'images/{fn}'"
    js = re.sub(r"'([^']+)':'data:image/png;base64,([A-Za-z0-9+/=]+)'", img, js)
    assert 'data:image/png;base64,' not in js, 'an embedded picture was not moved out'
    (out / 'app.js').write_text('// TileSmith app code (readable copy of the <script> in app/index.html, formatted, pictures moved to images/)\n' + js)
    (out / 'style.css').write_text(css)
    (out / 'index.html').write_text(head + '<link rel="stylesheet" href="style.css">\n</head>' + body.replace('</head>', '', 1) + '<script src="app.js"></script></body></html>\n')
    fmt = [str(PRETTIER)] if PRETTIER.exists() else ['npx', '--yes', 'prettier@3.3.3']   # any Prettier 3 formats the same way
    subprocess.run(fmt + ['--write', '--print-width', '120', '--log-level', 'warn', str(out / 'app.js'), str(out / 'style.css'), str(out / 'index.html')], check=True)
    code = (out / 'app.js').read_text().split('\n')
    funcs = []
    for i, line in enumerate(code, 1):
        m = re.match(r'^(?:async )?function (\w+)\s*\(([^)]*)\)', line)
        if m: funcs.append((m.group(1), m.group(2), i))
    rows = '\n'.join(f'| `{n}({a})` | {i} | {ROLE.get(n, "")} |' for n, a, i in funcs)
    (out / 'FUNCTIONS.md').write_text(f"""# TileSmith app.js - function index

{len(funcs)} top-level functions in app.js ({len(code)} lines). The main ones have a short description; read the code for the rest.
Global state: `S` (settings of the selected wall + global settings), `walls` (all walls), `cur` (selected wall), `sims`
(build simulation per wall), `crew`, `V` (viewport zoom/pan), `M`/`mc` (master canvas and its 2D context), `T` (time in s).

| Function | Line | What it does |
|---|---|---|
{rows}
""")
    print(f'[ok] readable source in {out}: app.js {len(code)} lines, {len(funcs)} functions, {len(names)} images')
    return names


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'readable')
