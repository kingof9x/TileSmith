"""Refreshes the code excerpts in the website's reading guides from the real files, so line numbers stay right.

  python3 manual-src/make_code_guides.py           # rewrite the excerpts in place
  python3 manual-src/make_code_guides.py --check   # exit 1 if any excerpt is out of date (or its anchor is gone)

Each excerpt in website/read-the-code/index.html and website/read-rust/index.html sits between two markers:

  <!--code file="tilesmith-desktop/app/index.html" find="function pwC(" lines="0:1" cut="150"-->
  ... generated <pre> ...
  <!--/code-->

file   the file to quote, from the repository root
find   text on the first line to quote (the first line that contains it); the excerpt follows the code when it moves
lines  "a:b": quote from a lines before/after the found line to b lines after it (default "0:0")
cut    shorten each line to this many characters and add a grey "…" (index.html has lines of 100,000+ characters)
around optional: on the found line, show `cut` characters around this text instead of the start of the line
skip   optional: "a:b" lines (relative, like lines) to leave out, shown as one "⋮" line

The map of index.html in read-the-code/ (<!--filemap--> ... <!--/filemap-->) is made from REGIONS below the same way:
each region starts at the first line containing its anchor text.
"""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [ROOT / 'website' / 'read-the-code' / 'index.html', ROOT / 'website' / 'read-rust' / 'index.html']
MARK = re.compile(r'(<!--code (?P<attrs>.*?)-->)(?P<body>.*?)(<!--/code-->)', re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')

APP = 'tilesmith-desktop/app/index.html'
FMARK = re.compile(r'(<!--filemap-->)(.*?)(<!--/filemap-->)', re.S)
COLORS = {'map': '#e6edf3', 'style': '#6b7280', 'html': '#94a3b8', 'data': '#a78bfa', 'state': '#22d3ee', 'ui': '#4ade80', 'engine': '#ffb020',
          'draw': '#f472b6', 'crew': '#fb923c', 'outputs': '#60a5fa', 'exports': '#ffe066', 'startup': '#ff5a5a'}
# (anchor text, kind, title, what is there, grep pattern to find it yourself); in file order
REGIONS = [
    ('<style>', 'style', 'Styles (CSS)', 'How everything looks: colours, panels, buttons. Line 67 alone is about 370,000 characters: the app\'s fonts, stored as base64 text so the app works offline. Keep word wrap off or skip that line.', "'^<style>'"),
    ('</style>', 'html', 'The page skeleton (HTML)', 'The top bar, the empty left panel, the viewport canvas and the right panel. Most of the left panel is not here: build() writes it later from templates.', "'id=\"vp\"'"),
    ('// ---------- Language:', 'data', 'Translations: TR', 'The first of two scripts. TR maps every English text in the app to nine other languages, one entry per line. setLang() at the end of this script swaps the text in place.', "'^const TR='"),
    ('HOW THIS FILE WORKS', 'map', 'Read this first: the file\'s own map', 'A 50-line comment at the top of the second script that explains state, the edit loop, the frame loop, engineering, translation and tests in plain English. Every other section starts with a // ---------- header.', "'HOW THIS FILE WORKS'", True),
    ('// ---------- tile catalogue P:', 'data', 'Tile catalogue: P', 'Every built-in tile model with its size, pixels, weight and watts, as the maker prints them. One model per line.', "'^const P='"),
    ('NovaStar receiving card files', 'engine', 'Receiving card files', 'A small library of NovaStar .rcfg files stored in the browser (IndexedDB), linked to tile models.', "'rcfg'"),
    ('// ---------- PWRSRC', 'data', 'Where tile figures come from: PWRSRC', 'The datasheet link and date behind each tile model\'s figures, shown in the Engineering panel.', "'PWRSRC'"),
    ('// ---------- S: default settings', 'state', 'Settings: S', 'Start here. S holds every setting with its default value, one per line: canvas size, tile model, colours, processor, power, outputs. Every panel reads and writes it.', "'^const S='"),
    ('// ---------- LED walls (', 'state', 'Walls: walls and WK', 'Each wall is an object holding its own copy of the per-wall settings (the keys listed in WK). S always shows the selected wall; storeWall() copies S back into it.', "'^const WK='"),
    ('// ---------- several canvases', 'state', 'Canvases: CVS', 'Each canvas is its own output picture with its own walls. Switching canvas swaps the globals.', "'function switchTo'"),
    ('// ---------- tiles of a wall', 'engine', 'Tiles of a wall: pieces()', 'Turns a wall\'s columns, rows, removed tiles and half tiles into a list of tile rectangles. Almost everything else asks pieces() first.', "'function pieces('"),
    ('// ---------- panel sub-menus', 'ui', 'Panels: build(), sync(), LIM, input', 'build() writes the left panel\'s HTML from templates (F() makes one labelled box). sync() brings every panel up to date. LIM holds each number\'s allowed range. The input and change listeners turn a typed value into S[key] with applyKey().', "'^function (build|sync|applyKey)'"),
    ('// ---------- Flown from motors', 'crew', 'Flown walls', 'How a flown wall is hung from motors a row at a time, top row first.', "'Flown'"),
    ('// ---------- patterns', 'draw', 'Test patterns: pat()', 'Every test pattern, drawn onto one wall.', "'^function pat('"),
    ('// ---------- worker', 'crew', 'The Classic technician: worker()', 'The flat-shaded technician, drawn from shapes for each pose.', "'^function worker('"),
    ('// ---------- LED processors', 'data', 'Processors: PROC', 'Every LED processor: pixels per port, ports, and how frame rate and bit depth change them.', "'^const PROC='"),
    ('// ---------- data wiring', 'engine', 'Data wiring: portPlan()', 'Which processor port feeds which tiles, in which order.', "'^function portPlan'"),
    ('// ---------- power: like data wiring', 'engine', 'Power: pwC(), powerPlan()', 'Usable watts per circuit (pwC) and which circuit feeds which tiles (powerPlan).', "'^function (pwC|powerPlan)'"),
    ('// ---------- distros', 'engine', 'Distros and phases', 'Circuits rolled up to cables, distro outputs and the three phases, with the load on each leg.', "'dsState'"),
    ('// ---------- editing the tiles', 'ui', 'Editing tiles', 'Removing tiles, half tiles and other edits made by clicking the wall.', "'halfEdit'"),
    ('// ---------- render master', 'draw', 'Drawing a frame: render()', 'Draws every wall onto the hidden master canvas: patterns, outlines, labels, data and power runs, the crew. The build animation (stepSim) is here too.', "'^function (render|stepSim)'"),
    ('// ---------- crew styles', 'crew', 'Crew styles: Hand-drawn and Backlit', 'The 3D motion-captured crew and the backlit silhouette style.', "'Rocketbox'"),
    ('// ---------- tile repair', 'crew', 'Tile repair', 'The Fix glitch animation: a technician swaps a faulty tile.', "'Fix glitch'"),
    ('// ---------- Tile faults', 'draw', 'Tile faults', 'Simulated LED failures: dead tiles, flicker, colour channels out and more.', "'glType'"),
    ('// ---------- picking faulty tiles', 'ui', 'Viewport: picking and vpDraw()', 'Clicking and dragging on tiles, and vpDraw(), which copies the master canvas to the screen at the current zoom.', "'^function vpDraw'"),
    ('// ---------- cable lengths', 'engine', 'Cable lengths and wall totals: wst()', 'Cable lengths per wall, and wst(): pixels, area, weight and watts for one wall.', "'^function wst('"),
    ('// ---------- locations', 'engine', 'Locations', 'Named places where gear is staged (stage left, FOH…). In the code they are still called zones.', "'zones'"),
    ('// ---------- redundancy', 'engine', 'Redundancy', 'Backup data paths for each wall.', "'wred'"),
    ('// ---------- rigging', 'engine', 'Rigging and the Engineering panel: info()', 'Bumpers, truss and hoist loads. info() near the end fills the right-hand Engineering panel with every figure.', "'^function info('"),
    ('// ---------- cable labels', 'exports', 'Cable labels', 'Printable labels for both ends of every data and power cable.', "'cable labels'"),
    ('// ---------- Export PDF', 'exports', 'PDF export', 'A PDF writer made by hand: the raster, the spec sheet and the labels.', "'^function exportPDF'"),
    ('// ---- Layered pixel map export', 'exports', 'SVG and PSD export', 'Layered files written byte by byte, with no libraries.', "'PSD'"),
    ('// ---------- show binder', 'exports', 'Show binder', 'The PDF with a cover, contents, a page per wall and a pull sheet.', "'binder'"),
    ('// ---------- Cabinet IDs', 'draw', 'Cabinet IDs pattern', 'Each tile\'s data address drawn on it as a test pattern.', "'Cabinet ID'"),
    ('// ---------- send a canvas to a display', 'outputs', 'Send to a display', 'A borderless full-screen window on another monitor.', "'outInit'"),
    ('// ---------- processor config', 'exports', 'Processor config files', 'Experimental NovaStar screen files.', "'.scr'"),
    ('// ---------- Resolume', 'exports', 'Resolume preset', 'An Advanced Output XML preset for Resolume Arena.', "'Resolume'"),
    ('// ---------- real NDI', 'outputs', 'NDI® output', 'Loads the NDI® library through koffi and sends every frame. DESK and MOBILE, the "where am I running" flags, are set here.', "'^const DESK'"),
    ('// ---------- Spout (Windows)', 'outputs', 'Spout and Syphon', 'Shares the picture with other programs on the same computer.', "'Spout'"),
    ('// ---------- Report a bug', 'ui', 'Report a bug', 'Screenshots the whole window, lets you draw on it and prepares an e-mail.', "'bugrpt'"),
    ('// Check for updates:', 'outputs', 'Updates', 'Asks GitHub for the latest release, and Update now (download, check, install).', "'UPD_API'"),
    ('// Add-ons (Info window', 'outputs', 'Add-ons: NDI® Runtime and ffmpeg', 'Finds, or downloads when you ask, the parts TileSmith does not ship.', "'Add-ons'"),
    ('// Export video under Video export', 'exports', 'Video export (ffmpeg)', 'Starts ffmpeg and pipes raw frames into it: HAP, ProRes, H.264.', "'^function recStart'"),
    ('// ---------- DVD screensaver', 'draw', 'DVD screensaver', 'The bouncing logo, and the perfect-loop maths after it.', "'dvd'"),
    ('// ---------- frame clock', 'engine', 'The main loop: tick() and loop()', 'loop() runs before every screen refresh; tick() moves the animations and redraws only when something changed.', "'^function (tick|loop)'"),
    ('// ---------- undo / redo', 'state', 'Saving and undo', 'saveSoon() saves 0.4 s after a change; undo keeps 20 snapshots.', "'^function save'"),
    ('// ---------- Save / Open project', 'state', 'Project files and loadState()', 'Writing and reading .tilesmith files, and loadState(), which reads your last settings at start.', "'^function loadState'"),
    ('cc=0;loadState();', 'startup', 'Startup', 'The last lines of the file. They run once, when everything above has been defined: load settings, build the panels, start the loop.', "'cc=0;loadState();'"),
]

KW = {
    'js': set('const let var function return if else for while do switch case break continue new typeof instanceof in of '
              'try catch finally throw class extends async await true false null undefined this'.split()),
    'rs': set('as async await break const continue crate dyn else enum extern false fn for if impl in let loop match mod move '
              'mut pub ref return self Self static struct super trait true type unsafe use where while'.split()),
    'py': set('import from as def async await with for in if else elif return and or not True False None'.split()),
}


def lang_of(path):
    return {'.rs': 'rs', '.py': 'py', '.toml': 'toml'}.get(pathlib.Path(path).suffix, 'js')


def highlight(line, lang):
    """A small tokenizer: comments grey, strings yellow, keywords cyan, numbers pink. Good enough for short excerpts."""
    out, i, n = [], 0, len(line)
    esc = html.escape
    while i < n:
        c = line[i]
        if lang in ('py', 'toml') and c == '#':
            out.append(f'<span class="c">{esc(line[i:])}</span>'); break
        if line.startswith('//', i) and lang not in ('py', 'toml'):
            out.append(f'<span class="c">{esc(line[i:])}</span>'); break
        if lang == 'rs' and c == "'" and i + 2 < n and (line[i + 1].isalpha() or line[i + 1] == '_') and line[i + 2] != "'":
            j = i + 1
            while j < n and (line[j].isalnum() or line[j] == '_'):
                j += 1
            out.append(f'<span class="k">{esc(line[i:j])}</span>'); i = j; continue
        if c in '"\'`' and not (lang == 'rs' and c == '`'):
            j = i + 1
            while j < n and line[j] != c:
                j += 2 if line[j] == '\\' else 1
            j = min(j + 1, n)
            out.append(f'<span class="s">{esc(line[i:j])}</span>'); i = j; continue
        if c.isdigit() and (i == 0 or not (line[i - 1].isalnum() or line[i - 1] == '_')):
            j = i
            while j < n and (line[j].isalnum() or line[j] in '._'):
                j += 1
            out.append(f'<span class="n">{esc(line[i:j])}</span>'); i = j; continue
        if c.isalpha() or c in '_$':
            j = i
            while j < n and (line[j].isalnum() or line[j] in '_$'):
                j += 1
            word = line[i:j]
            if word in KW.get(lang, ()):
                out.append(f'<span class="k">{esc(word)}</span>')
            elif lang == 'rs' and j < n and line[j] == '!':
                out.append(f'<span class="m">{esc(word)}!</span>'); j += 1
            else:
                out.append(esc(word))
            i = j; continue
        out.append(esc(c)); i += 1
    return ''.join(out)


def excerpt(attrs):
    a = dict(ATTR.findall(attrs))
    path = ROOT / a['file']
    lines = path.read_text(encoding='utf-8').split('\n')
    hit = next((k for k, s in enumerate(lines) if a['find'] in s), None)
    if hit is None:
        raise SystemExit(f'{a["file"]}: no line contains {a["find"]!r}; update the marker in the guide')
    lo, hi = (int(x) for x in a.get('lines', '0:0').split(':'))
    sk = [int(x) for x in a['skip'].split(':')] if 'skip' in a else None
    cut, lang = int(a.get('cut', '0')), lang_of(a['file'])
    rows, width = [], len(str(hit + hi + 1))
    for k in range(hit + lo, hit + hi + 1):
        rel = k - hit
        if sk and sk[0] <= rel <= sk[1]:
            if rel == sk[0]:
                rows.append(f'<span class="ln">{"":>{width}}</span> <span class="c">⋮</span>')
            continue
        s = lines[k].rstrip()
        more = pre = ''
        if rel == 0 and 'around' in a and a['around'] in s:
            at = max(0, s.index(a['around']) - 30)
            if at:
                s, pre = s[at:], '<span class="more">…</span>'
        if cut and len(s) > cut:
            s, more = s[:cut], '<span class="more">…</span>'
        rows.append(f'<span class="ln">{k + 1:>{width}}</span> {pre}{highlight(s, lang)}{more}')
    first, last = hit + lo + 1, hit + hi + 1
    where = f'{a["file"]} · line {first}' if first == last else f'{a["file"]} · lines {first}–{last}'
    note = ' · long lines shortened' if cut and any('class="more"' in r for r in rows) else ''
    return f'<figure class="src"><figcaption>{html.escape(where)}{note}</figcaption><pre>' + '\n'.join(rows) + '</pre></figure>'


def filemap():
    lines = (ROOT / APP).read_text(encoding='utf-8').split('\n')
    regions, last = [], 0
    for anchor, kind, title, text, grep, *start in REGIONS:
        hit = next((k for k in range(last, len(lines)) if anchor in lines[k]), None)
        if hit is None:
            raise SystemExit(f'{APP}: no line after {last + 1} contains {anchor!r}; update REGIONS in make_code_guides.py')
        regions.append({'line': hit + 1, 'kind': kind, 'title': title, 'text': text, 'grep': grep, 'start': bool(start)})
        last = hit + 1
    # the grep shown for a region must land inside it first; if the short pattern matches earlier in the file, show a
    # grep for the region's own header line instead
    for i, (r, (anchor, *_)) in enumerate(zip(regions, REGIONS)):
        end = regions[i + 1]['line'] - 1 if i + 1 < len(regions) else len(lines)
        g = r['grep'].strip("'")   # ERE when it has |, else plain text with an optional leading ^ (as grep reads them)
        pat = re.compile(g if '|' in g else ('^' if g.startswith('^') else '') + re.escape(g.lstrip('^')))
        first = next((k + 1 for k, s in enumerate(lines) if pat.search(s)), None)
        if first is None or not r['line'] <= first <= end:
            r['grep'] = "-F '" + anchor + "'"
        elif '|' in r['grep']:
            r['grep'] = '-E ' + r['grep']
    data = {'total': len(lines) - (lines[-1] == ''), 'colors': COLORS, 'regions': regions}
    return '<script type="application/json" id="fmdata">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def main():
    check, stale = '--check' in sys.argv, []
    for page in PAGES:
        text = page.read_text(encoding='utf-8')
        new = MARK.sub(lambda m: m.group(1) + excerpt(m.group('attrs')) + m.group(4), text)
        new = FMARK.sub(lambda m: m.group(1) + filemap() + m.group(3), new)
        if new != text:
            stale.append(page.relative_to(ROOT))
            if not check:
                page.write_text(new, encoding='utf-8')
    if check and stale:
        print('out of date:', *stale, '(run python3 manual-src/make_code_guides.py)'); sys.exit(1)
    print('updated:' if stale else 'up to date', *stale)


if __name__ == '__main__':
    main()
