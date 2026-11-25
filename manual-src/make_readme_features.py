# Feature screenshots for the README "What's new" section, taken from the running app:
#   python3 make_readme_features.py <app index.html> <output folder>
# Writes one PNG per feature (power-distros, power-per-wall, power-draw-circuit, build-running, cable-fibre, redundancy, rigging, cabinet-ids, locations, tile-faults, tile-catalog,
# languages, updates). Set CHROME to a Chromium binary if Playwright has no browser of its own.
# Set VERSION (e.g. VERSION=3.8) to show that version in the app header; the updates shot then shows VERSION offered
# to someone on the release before it. Without it the shots use the version in index.html.
import asyncio, json, re, sys, os
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annotate import annotate
APP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '../tilesmith-desktop/app/index.html')
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'readme-shots')
os.makedirs(OUT, exist_ok=True)
VERSION = os.environ.get('VERSION', '').lstrip('v')
TMP = []
def stamped(v):
    # a copy of the app next to the original (so its relative files load) showing version v, as set-version.js does
    s = open(APP, encoding='utf-8').read()
    s = re.sub(r'color:var\(--am\)">v[\d.]+</span></h1>', f'color:var(--am)">v{v}</span></h1>', s)
    s = re.sub(r"const APP_VERSION='[\d.]+';", f"const APP_VERSION='{v}';", s)
    t = os.path.join(os.path.dirname(APP), f'.readme-shot-{v}.html'); open(t, 'w', encoding='utf-8').write(s)
    if t not in TMP: TMP.append(t)
    return t

# open the side-panel sections whose titles start with these names (and their parents); close all others
OPEN = """(names)=>{document.querySelectorAll('#left details').forEach(d=>d.open=false);
 for(const n of names){const d=[...document.querySelectorAll('#left details')].find(x=>x.querySelector(':scope>summary').textContent.trim().startsWith(n));
  if(d)for(let e=d;e;e=e.parentElement)if(e.tagName=='DETAILS')e.open=true}}"""
# scroll the side panel so the first open section with this title is at the top
SCROLL = """(n)=>{const d=[...document.querySelectorAll('#left details')].find(x=>x.querySelector(':scope>summary').textContent.trim().startsWith(n));if(d)d.scrollIntoView({block:'start'})}"""
# the same two-wall show every shot starts from
BASE = """()=>{S.cw=3000;S.ch=1500;S.preset='ROE Black Pearl BP2V2';applyPreset();S.name='Main';S.cols=12;S.rows=6;S.ox=850;S.oy=220;S.pat='tileshade';S.ids=true;storeWall();
 addWall(false);S.name='IMAG Left';S.cols=4;S.rows=6;S.ox=60;S.oy=220;S.pat='tileshade';storeWall();
 S.proc='NovaStar VX1000 Pro';applySpec();walls.forEach(w=>{w.wmode='Snake';w.pmode='Snake'});S.wmode='Snake';S.pmode='Snake';S.showData=true;storeWall();
 selWall(0);showAll();sync();fit()}"""

async def shot(pg, name, setup, open_names, scroll=None, wait=1200, eng=None, annot=None):
    await pg.evaluate(setup)
    if open_names is not None: await pg.evaluate(OPEN, open_names)
    if scroll: await pg.evaluate(SCROLL, scroll)
    await pg.evaluate("()=>{sync();fit()}")
    await pg.wait_for_timeout(wait)
    if eng: await pg.evaluate("(q)=>{const e=document.querySelector(q);if(e)e.scrollIntoView({block:'start'})}", eng); await pg.wait_for_timeout(300)
    if annot: await annotate(pg, annot)  # circles and arrows on the controls the README's steps name
    await pg.screenshot(path=os.path.join(OUT, name + '.png'))
    print('wrote', name + '.png')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {})); errs = []
        async def fresh(app=None):
            pg = await b.new_page(viewport={'width': 1600, 'height': 960}, device_scale_factor=1)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + (app or (stamped(VERSION) if VERSION else APP))); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(900)
            await pg.evaluate(BASE); return pg
        pg = await fresh()
        await shot(pg, 'power-distros', """()=>{S.pdist=true;S.showPow=true;S.showData=false;distAct('dadd');distAct('dadd');S.phaseView=true;S.autoBal=true;storeWall();sync()}""",
                   ['Power', 'Distros'], 'Distros')
        await pg.close(); pg = await fresh()
        # two walls, each on its own Socapex cable: This wall (Start this wall on its own cable) and the power tray
        await shot(pg, 'power-per-wall', """()=>{S.showPow=true;S.showData=false;S.proc='None';walls.forEach(w=>{w.wmode='None'});S.wmode='None';distAct('dadd');storeWall();selWall(0);sync();
          setTimeout(()=>{const k=document.querySelector('#pcabSet');if(k)k.scrollIntoView({block:'center'})},300)}""", ['Power', 'This wall'], None, 1500,
                   annot=[{'sel': 'label:has([data-k=pown])', 'n': 3, 'dx': 230, 'dy': 0, 'pad': 4},
                          {'sel': '#pcabCards .pchip.sp', 'all': True, 'n': 'S', 'dx': 230, 'dy': -45, 'pad': 4},
                          {'sel': '#ptray .ptchip', 'all': True, 'n': 4, 'dx': 120, 'dy': 95, 'pad': 6}])
        await pg.close(); pg = await fresh()
        # how-to: draw power circuits by hand on one wall (This wall cable card, Draw circuit, chips), numbered like the README steps
        await pg.evaluate("""()=>{selWall(1);delWall();selWall(0);S.cols=8;S.rows=4;S.ox=200;S.oy=200;S.cw=2400;S.ch=1200;S.showPow=true;S.showData=false;S.proc='None';
          S.wmode='None';S.pmode='Manual';S.pman=[];distAct('dadd');storeWall();sync();fit()}""")
        await pg.evaluate(OPEN, ['Power', 'This wall'])
        await pg.click('[data-pcx=draw]'); await pg.wait_for_timeout(300)
        TILE = """(cr)=>{const r=document.querySelector('#vp').getBoundingClientRect(),w=walls[cur],tw=wW(w)/w.cols,th=wH(w)/w.rows;
          return cr.map(([c,rw])=>({x:r.left+V.x+(w.ox+(c+.5)*tw)*V.z,y:r.top+V.y+(w.oy+(rw+.5)*th)*V.z}))}"""
        async def drag(cells):
            pts = await pg.evaluate(TILE, cells)
            await pg.mouse.move(pts[0]['x'], pts[0]['y']); await pg.mouse.down()
            for q in pts[1:]: await pg.mouse.move(q['x'], q['y'], steps=4)
            await pg.mouse.up(); await pg.wait_for_timeout(300)
        await drag([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]])   # circuit 1-1 along the top row
        await pg.click('#pcabCards .pchip.sp'); await pg.wait_for_timeout(200)          # a spare chip starts circuit 1-2
        await drag([[7, 1], [6, 1], [5, 1], [4, 1]])
        drawn = await pg.evaluate("()=>S.pman.map(c=>c.length)"); assert drawn == [8, 4], drawn
        await shot(pg, 'power-draw-circuit', """()=>{setTimeout(()=>{const k=document.querySelector('#pcabCards');if(k)k.scrollIntoView({block:'center'})},200)}""", None, None, 900,
                   annot=[{'sel': '[data-pcx=draw]', 'n': 1, 'dx': 40, 'dy': 50, 'pad': 4},
                          {'sel': '#vp', 'n': 2, 'corner': 'tl', 'pad': -4},
                          {'sel': '#pcabCards .pchip.sp', 'n': 3, 'dx': -20, 'dy': -48, 'pad': 4}])
        await pg.close(); pg = await fresh()
        # the LED build running: the toolbar button reads Stop LED Build and is lit green while the effect is on
        await shot(pg, 'build-running', """()=>{selWall(1);delWall();selWall(0);S.cols=10;S.rows=5;S.ox=300;S.oy=150;S.cw=2400;S.ch=1200;S.showData=false;storeWall();
          document.querySelector('[data-a=bldgo]').click();for(let i=0;i<60*900&&sims[0].i<27;i++)step(1/60);forceRen=true}""", [], None, 1500,
                   annot=[{'sel': '[data-a=bldgo]', 'pad': 4}])
        await pg.close(); pg = await fresh()
        await shot(pg, 'cable-fibre', """()=>{S.cabOn=true;S.cunit='m';S.cslack=10;selWall(0);S.cdD=140;S.cdP=20;S.wfib='Auto';storeWall();selWall(1);S.cdD=30;S.cdP=15;storeWall();selWall(0);sync()}""",
                   ['Cable lengths'], 'Cable lengths')
        await pg.close(); pg = await fresh()
        await shot(pg, 'redundancy', """()=>{S.cabOn=true;selWall(0);S.wred='Full';S.cdD=140;storeWall();selWall(1);S.wred='Loop';storeWall();selWall(0);S.gOn=false;sync()}""",
                   ['LED processor'], 'LED processor', eng='details[data-eng="sig"]')
        await pg.close(); pg = await fresh()
        await shot(pg, 'rigging', """()=>{selWall(1);delWall();selWall(0);S.ox=200;S.rigOn=true;S.bmode='Flown from truss';S.tsec='1, 2, 3';S.thn=3;S.tex=0.5;storeWall();sync()}""",
                   ['Rigging'], 'Rigging')
        await pg.close(); pg = await fresh()
        await shot(pg, 'cabinet-ids', """()=>{S.pports=4;storeWall();walls.forEach(w=>w.pat='cabinet IDs');S.pat='cabinet IDs';storeWall();sync()}""",
                   ['Cabinet IDs'], 'Cabinet IDs')
        await pg.close(); pg = await fresh()
        await shot(pg, 'locations', """()=>{zAdd();zAdd();S.zones[0].name='Stage';S.zones[1].name='FOH';selWall(0);S.zone=S.zones[0].id;storeWall();selWall(1);S.zone=S.zones[1].id;storeWall();S.zProc=S.zones[1].id;selWall(0);sync()}""",
                   ['Locations'], 'Locations')
        await pg.close(); pg = await fresh()
        await shot(pg, 'tile-faults', """()=>{S.glType='Random mix';S.glPick='Random';S.glN=6;sync();glGo();sync()}""",
                   ['Tile faults'], 'Tile faults', wait=2000)
        await pg.close(); pg = await fresh()
        await pg.evaluate(OPEN, ['Tile model'])
        await pg.evaluate(SCROLL, 'Tile model')
        await pg.fill('#tFind', 'AR3.9'); await pg.wait_for_timeout(300)
        await shot(pg, 'tile-catalog', "()=>{}", ['Tile model'], 'Tile model')
        await pg.close(); pg = await fresh()
        # the whole UI in Portuguese (Brazil), with the Canvases and Tile model menus open
        await pg.evaluate(OPEN, ['Canvases', 'Tile model'])
        await shot(pg, 'languages', "()=>{setLang('pt-BR');sync()}", None, wait=800)
        await pg.close()
        # Info > Updates after Check for updates finds a newer release (GitHub mocked, no network needed)
        nxt = VERSION or '0'
        if VERSION:
            prev = VERSION.split('.'); prev[-1] = str(int(prev[-1]) - 1); pg = await fresh(stamped('.'.join(prev)))
        else:
            pg = await fresh(); ver = await pg.evaluate("()=>APP_VERSION"); nxt = ver.split('.'); nxt[-1] = str(int(nxt[-1]) + 1); nxt = '.'.join(nxt)
        rel = {'tag_name': 'v' + nxt, 'html_url': 'https://github.com/kingof9x/TileSmith/releases/tag/v' + nxt, 'assets': []}
        await pg.route('https://api.github.com/**', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(rel),
                                                                      headers={'Access-Control-Allow-Origin': '*'}))
        await pg.click('[data-a=about]'); await pg.wait_for_timeout(300)
        await pg.click('#updChk'); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>document.getElementById('updBox').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=os.path.join(OUT, 'updates.png')); print('wrote updates.png')
        await b.close()
        for t in TMP: os.remove(t)
        assert not errs, errs
asyncio.run(main())
