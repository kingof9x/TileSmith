"""Screenshots and animation frames for the Google AI Studio kit and the mobile manual.

Runs the real TileSmith page as the Android app sees it (android-aistudio/prepare-assets.js output, with a stand-in for
the Kotlin TileSmithAndroid interface), in dark mode, at tablet (1280x800) and phone (412x915) sizes.
Writes PNG and GIF files to kit/shots (or KIT_SHOTS) and kit/shots/index.json describing every picture.
"""
import asyncio, base64, io, json, os, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).parent
PROJ = pathlib.Path(os.environ.get('TILESMITH', '/home/claude/tilesmith-desktop'))
OUT = pathlib.Path(os.environ.get('KIT_SHOTS', HERE / 'kit' / 'shots'))
ASSETS = HERE / 'kit' / 'assets-build'
subprocess.run(['node', str(PROJ / 'android-aistudio' / 'prepare-assets.js'), str(ASSETS)], check=True, stdout=subprocess.DEVNULL)
APP = (ASSETS / 'tilesmith' / 'index.html').as_uri()

# stand-in for the Kotlin side (TileSmithBridge.kt) + a fixed random seed so the DVD logo and colours repeat exactly
MOCK = r"""
(()=>{let s=20261014;Math.random=()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const files=window.__files={};
window.TileSmithAndroid={writeChunk(n,b,a){if(!a||!files[n])files[n]=[];files[n].push(b);return ''},deleteFile(n){delete files[n];return ''},
 shareFile(n,m,id){setTimeout(()=>window.__tsmDone(id,true),20);return ''},openUrl(){return ''},keepAwake(){}};
})();
"""
# stop the page's own animation loop so frames can be stepped by hand: __hold() freezes it, then step(n) runs n frames of
# 1/60 s through the app's own tick() at a made-up clock and render() draws the canvas exactly as the app would
HOLD = r"""
(()=>{const R=window.requestAnimationFrame.bind(window);window.requestAnimationFrame=cb=>window.__held?0:R(cb);
window.__hold=()=>{window.__held=true;window.__now=Math.ceil(performance.now()/1000)*1000+1000};
window.__step=(n,dtMs)=>{dtMs=dtMs||1000/60;for(let i=0;i<n;i++){window.__now+=dtMs;tick(window.__now)}forceRen=true;tick(window.__now);vpDraw()};
})();
"""
SHOTS = []  # (file, group, title, notes)


def add(name, group, title, notes=''):
    SHOTS.append({'file': name, 'group': group, 'title': title, 'notes': notes})


def png_from_dataurl(u):
    return Image.open(io.BytesIO(base64.b64decode(u.split(',', 1)[1]))).convert('RGB')


def save(im, name):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p, optimize=True)
    return p


async def canvas(pg):
    return png_from_dataurl(await pg.evaluate("M.toDataURL('image/png')"))


PREP = "storeWall();showAll();sync();fit();forceRen=true"
# zoom the viewport onto the selected wall (close-ups of wall shapes)
ZOOM = "{const r=vp.getBoundingClientRect(),w=walls[cur];V.z=Math.min(r.width/wW(w),r.height/wH(w))*.9;V.x=(r.width-wW(w)*V.z)/2-w.ox*V.z;V.y=(r.height-wH(w)*V.z)/2-w.oy*V.z;forceRen=true}"


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []

        async def page(w, h, dpr, mobile=False, scheme='dark'):
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, color_scheme=scheme, has_touch=True, is_mobile=mobile)
            pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.add_init_script(MOCK + HOLD)
            await pg.goto(APP); await pg.wait_for_timeout(900)
            return ctx, pg

        # ------------------------------------------------------------------ tablet screens (1280 x 800)
        ctx, pg = await page(1280, 800, 1.5)
        ev = pg.evaluate

        async def full(name, title, notes=''):
            await pg.wait_for_timeout(250); await pg.screenshot(path=str(OUT / name)); add(name, 'tablet', title, notes)

        async def opensub(title, close_others=True):
            loc = pg.locator(f'xpath=//details[summary[contains(normalize-space(.), "{title}")]]').first
            await loc.evaluate("""(d,c)=>{if(c)document.querySelectorAll('#left details.subd').forEach(x=>{if(!x.contains(d))x.open=false});
                for(let e=d;e;e=e.parentElement&&e.parentElement.closest('details'))e.open=true;
                const L=document.querySelector('#left');L.scrollTop+=d.getBoundingClientRect().top-L.getBoundingClientRect().top-8}""", close_others)
            await pg.wait_for_timeout(200)
            return loc

        async def ui(title, name, ui_title, notes=''):
            loc = await opensub(title)
            await loc.screenshot(path=str(OUT / name)); add(name, 'panel', ui_title, notes)

        await full('t01-first-launch.png', 'First launch (tablet, landscape)',
                   'Default state: one 6x4 wall of Unilumin UpadIV 2.6 tiles on a 1920x1080 canvas, tileshade pattern. Left: settings panel. Top: action bar. Centre: viewport. Right: engineering panel.')
        await pg.locator('#bar').screenshot(path=str(OUT / 'ui-top-bar.png')); add('ui-top-bar.png', 'panel', 'Top bar (mobile app)', 'NDI® and Spout/Syphon buttons are hidden in the mobile app.')
        hc = await ev("(()=>{const a=document.querySelector('#left > h1').getBoundingClientRect(),b=document.querySelector('#left > h1 + div').getBoundingClientRect();return{x:a.left-4,y:a.top-4,width:Math.max(a.width,b.width)+8,height:b.bottom-a.top+8}})()")
        await pg.screenshot(path=str(OUT / 'ui-header.png'), clip=hc); add('ui-header.png', 'panel', 'App header', 'Title with the version in amber, subtitle in muted grey.')

        # a working setup: two walls, processor and data paths
        await ev(f"""()=>{{S.name='Main';S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.pat='tileshade';storeWall();showAll();addWall(false);S.name='Side';S.cols=4;S.rows=3;S.ox=1200;S.oy=300;storeWall();showAll();
            S.proc='NovaStar VX1000 Pro';applySpec();walls.forEach(w=>{{w.wmode='Snake'}});S.wmode='Snake';{PREP}}}""")
        await full('t02-two-walls-data.png', 'Two walls with data paths', 'Two walls (Main 6x4, Side 4x3), NovaStar VX1000 Pro, Snake data wiring drawn on the canvas, engineering panel filled in.')
        await ui('Canvas', 'ui-canvas.png', 'Canvas section')
        await ui('LED walls', 'ui-led-walls.png', 'LED walls submenu', 'Wall list (selected wall highlighted amber), Add wall / Duplicate / Remove, wall name, Tech starts at, Tile placement.')
        await full('t03-led-walls.png', 'Canvas > LED walls', '')
        await ui('Tile model', 'ui-tile-model.png', 'Tile model submenu', 'Preset list grouped by manufacturer, tile size in px and mm, pitch, weight, max watts, depth.')
        await ui('Size of LED Wall', 'ui-size.png', 'Size of LED Wall submenu', 'Columns, rows, quick sizes, Remove tiles / Restore all tiles.')
        await ui('Wall position', 'ui-position.png', 'Wall position submenu', 'Offset X / Y and alignment buttons.')
        await full('t04-wall-position.png', 'Canvas > Wall position', '')
        await ui('Engineering', 'ui-engineering-section.png', 'Engineering section (all submenus)', 'LED processor with Data wiring inside, Power with Power wiring inside.')
        await ui('LED processor', 'ui-led-processor.png', 'LED processor submenu (with Data wiring)', '')
        await ui('Data wiring', 'ui-data-wiring.png', 'Data wiring submenu', 'Pattern (None/Snake/Linear/Manual), 8 start icons, Data wiring preference with explanation, Show data paths, status.')
        await full('t05-data-wiring.png', 'Engineering > LED processor > Data wiring', '')
        await pg.locator('#right').screenshot(path=str(OUT / 'ui-engineering-panel.png')); add('ui-engineering-panel.png', 'panel', 'Engineering panel (right side)', 'Entire canvas, then one section per wall.')

        # manual data wiring in progress
        await ev(f"""()=>{{selWall(1);delWall();S.cols=10;S.rows=5;S.ox=0;S.oy=0;S.wmode='Manual';S.wman=[[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[9,1],[8,1],[7,1],[6,1],[5,1],[4,1],[3,1]],[[2,1],[1,1],[0,1],[0,2],[1,2],[2,2]]];{PREP}}}""")
        await ev("()=>document.querySelector('[data-a=wedit]').click()")
        await opensub('Data wiring'); await full('t06-manual-data-wiring.png', 'Manual data wiring', 'Pattern = Manual, Wire tiles pressed (button reads Stop wiring). Port P1 is full (17 tiles); P2 is being drawn.')
        await ev("()=>document.querySelector('[data-a=wedit]').click()")

        # power
        await ev(f"""()=>{{S.wmode='Snake';S.wman=[];S.pdist=true;S.pmode='Snake';{PREP}}}""")
        await ui('Power', 'ui-power.png', 'Power submenu (with Power wiring)', '')
        await ui('Power wiring', 'ui-power-wiring.png', 'Power wiring submenu', '')
        await full('t07-power-and-data.png', 'Data and power on the same wall', 'Data paths run left of the tile centres, power runs (white on black) right and below; circuit badges show a lightning bolt and the circuit number.')
        await ev(f"""()=>{{S.proc='None';S.wmode='None';{PREP}}}""")
        await opensub('Power wiring'); await full('t08-power-wiring.png', 'Engineering > Power > Power wiring', 'Power only: dashed runs in circuit colours.')
        await ev(f"""()=>{{S.pdist=false;S.pmode='None';S.cols=6;S.rows=4;{PREP}}}""")

        # test pattern + overlays
        await ui('Test pattern', 'ui-test-pattern.png', 'Test pattern section', 'Pattern list, Tile-shade color (tileshade patterns only), Image fit (image patterns), Scroll, Scroll speed, uploads, centre box (branded patterns).')
        await ev(f"""()=>{{S.addr=true;S.mm=true;{PREP}}}""")
        await ui('Tile borders', 'ui-borders.png', 'Tile borders & overlays submenu', 'Border colour and thickness, tile position arrows, tile IDs, pixel address, size in mm.')
        await full('t09-overlays.png', 'Test pattern > Tile borders & overlays', 'All overlays on: tile ID, pixel address, size in mm and position arrows.')
        await ev(f"""()=>{{S.addr=false;S.mm=false;{PREP}}}""")

        # remove tiles mode / half tiles
        await ev(f"""()=>{{S.cols=8;S.rows=4;S.gone=[[0,0],[1,0],[6,0],[7,0],[0,1],[7,1]];{PREP};{ZOOM}}}""")
        await ev("()=>document.querySelector('[data-a=gedit]').click()"); await opensub('Size of LED Wall')
        await full('t10-remove-tiles.png', 'Remove tiles mode', 'Removed spots show a red dashed outline with an X in the viewport only.')
        await ev("()=>document.querySelector('[data-a=gedit]').click()")
        await ev(f"""()=>{{S.gone=[];S.preset='ROE Carbon CB5';applyPreset();S.cols=6;S.rows=3;S.half=[];S.lay={{s:'h',uc:6,ur:6,p:[[0,1,1,1],[1,0,1,2],[2,0,1,2],[3,0,1,2],[4,0,1,2],[5,1,1,1],[0,2,1,2],[1,2,1,2],[2,2,2,1],[2,3,1,1],[3,3,1,1],[4,2,1,2],[5,2,1,2],[0,4,1,2],[1,4,1,2],[2,4,1,2],[3,4,1,2],[4,4,1,2],[5,4,1,2]]}};{PREP};{ZOOM}}}""")
        await ev("()=>document.querySelector('[data-a=hedit]').click()"); await opensub('Tile model')
        await ui('Size of LED Wall', 'ui-tile-model-half.png', 'Size of LED Wall submenu on a model with a half version', 'Shows the half-tile note, Convert bottom / top row to half tiles, Mark half tiles and Clear half tiles.')
        await full('t11-half-tiles.png', 'Mark half tiles mode (ROE Carbon CB5)', 'Half tiles along the top and in row 2, one full tile turned on its side; empty half spaces show a red X.')
        await ev("()=>document.querySelector('[data-a=hedit]').click()")
        await ev(f"""()=>{{S.preset='Unilumin UpadIV 2.6';applyPreset();S.lay={{}};S.cols=6;S.rows=4;{PREP}}}""")

        # animation options
        await ev(f"""()=>{{S.dvdOn=true;S.dvdSize=24;S.pat='SMPTEbars';S.ids=false;S.tpos=false;{PREP}}}""")
        await ev("()=>{__hold();__step(150)}")
        await ui('DVD screensaver', 'ui-dvd.png', 'DVD screensaver submenu', 'Logo source, text, upload, bounce area, size, speed, corner hit chance, colour change, perfect loop, loop length, export loop video (desktop only, hidden).')
        await full('t12-dvd.png', 'Animation Options > DVD screensaver', '')
        await ev(f"""()=>{{S.dvdOn=false;S.pat='tileshade';S.ids=true;S.tpos=true;{PREP}}}""")
        await ui('Animation Options', 'ui-animation-section.png', 'Animation Options section', 'In the mobile app: DVD screensaver, Build options (with Technician) and Video export. NDI® and Spout/Syphon options are hidden.')
        await ev("()=>{reset();S.play=true;__step(60*27.5)}")
        await ui('Build options', 'ui-build-options.png', 'Build options submenu', 'Speed, loop build, pause before restart, Start build / Instant skip hints.')
        await ui('Technician', 'ui-technician.png', 'Technician submenu', 'Hard hat and vest colours, vest logo text or image, crew details: name, skin tone, hair colour, face photo per crew member.')
        await full('t13-build-in-progress.png', 'Build in progress', 'The technician carries a tile to its slot; placed tiles show the pattern, empty slots are dashed outlines.')
        await ui('Video export', 'ui-video-export.png', 'Video export submenu (mobile)', 'Blank intro and final hold seconds, estimated length, the mobile note (records MP4 with the device encoder). Format/HAP choices are desktop only.')
        await ev("()=>{showAll();window.__held=false;requestAnimationFrame(loop)}")
        await pg.wait_for_timeout(300)

        # recording
        await ev(f"""()=>{{S.vIntro=1;S.vHold=1;S.speed=2;{PREP};if(!MediaRecorder.isTypeSupported('video/mp4'))window.mrType=()=>'video/webm'}}""")
        await pg.click('#bar [data-a=rec]'); await pg.wait_for_timeout(2600)
        await opensub('Video export'); await full('t14-recording.png', 'Recording a video', 'The top bar shows the red recording status (blank, building, hold); press Export video again to cancel.')
        for _ in range(60):
            await pg.wait_for_timeout(500)
            st = await ev("document.querySelector('#recs').textContent")
            if st.startswith('Saved') or 'not' in st.lower(): break
        await full('t15-recording-saved.png', 'Recording finished', 'After the share sheet closes the status reads "Saved tilesmith-build-....mp4".')
        await ev(f"""()=>{{S.speed=1;S.vIntro=5;S.vHold=10;{PREP}}}""")

        # dialogs, menus, toasts
        await ev("()=>document.querySelector('#bar [data-a=about]').click()"); await pg.wait_for_timeout(300)
        await full('t16-info-dialog.png', 'Info dialog', 'About, credits, contact and Ko-fi links, Reset saved settings. NDI®/Spout/Syphon entries are hidden in the mobile app.')
        await pg.locator('#about .dlg').screenshot(path=str(OUT / 'ui-info-dialog.png')); add('ui-info-dialog.png', 'panel', 'Info dialog', '')
        await ev("showAbout(0)")
        await pg.click('#bar [data-a=rxmlm]'); await pg.wait_for_timeout(200)
        await full('t17-resolume-menu.png', 'Resolume XML menu', 'Drop-down: One slice per LED wall / One slice per tile.')
        await pg.keyboard.press('Escape'); await ev("()=>{try{ddClose()}catch(e){}}")
        await pg.click('#bar [data-a=npat]'); await pg.wait_for_timeout(300)
        await full('t18-next-pattern-toast.png', 'Next pattern + toast', 'Next pattern moves the selected wall to the next pattern; the toast at the bottom names it.')
        await ev(f"""()=>{{S.pat='tileshade';{PREP}}}""")
        await pg.click('#bar [data-a=png]'); await pg.wait_for_timeout(900)
        await full('t19-saved-toast.png', 'After Export PNG', 'The file goes to the Android share sheet; when an app was picked the toast says "Saved tilesmith-canvas.png."')

        # spec sheet (the HTML file the app shares)
        await pg.click('#bar [data-a=spec]'); await pg.wait_for_timeout(800)
        spec = await ev("()=>window.__files['tilesmith-spec.html']")
        (OUT / 'spec-sheet.html').write_text(base64.b64decode(''.join(spec)).decode())
        sp = await ctx.new_page(); await sp.set_viewport_size({'width': 900, 'height': 1200}); await sp.goto((OUT / 'spec-sheet.html').as_uri()); await sp.wait_for_timeout(300)
        await sp.screenshot(path=str(OUT / 't20-spec-sheet.png'), full_page=True); add('t20-spec-sheet.png', 'tablet', 'Spec sheet (shared as tilesmith-spec.html)', 'Entire canvas and per-wall tables, the same rows as the engineering panel.')
        await sp.close(); (OUT / 'spec-sheet.html').unlink()
        await ctx.close()

        # light theme
        ctx, pg = await page(1280, 800, 1.5, scheme='light')
        await pg.screenshot(path=str(OUT / 't21-light-theme.png')); add('t21-light-theme.png', 'tablet', 'Light theme', 'The page follows the system light/dark setting (prefers-color-scheme).')
        await ctx.close()

        # ------------------------------------------------------------------ phone (412 x 915), stacked layout
        ctx, pg = await page(412, 915, 2, mobile=True)
        H = await pg.evaluate("document.documentElement.scrollHeight")
        ys = list(range(0, max(1, H - 915), 915 - 60)) + [max(0, H - 915)]
        ys = [y for i, y in enumerate(ys) if i == 0 or y - ys[i - 1] > 200]
        for n, y in enumerate(ys, 1):
            await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(200)
            name = f'p{n:02d}-phone-portrait.png'
            await pg.screenshot(path=str(OUT / name)); add(name, 'phone', f'Phone portrait, screen {n} of {len(ys)}', f'The page scrolled to {y} px of {H} px (the stacked layout: settings, then top bar and viewport, then engineering).')
        # the same with every section and submenu open: every control on the phone, screen by screen
        await pg.evaluate("()=>{document.querySelectorAll('#left details').forEach(d=>{if(getComputedStyle(d).display!='none')d.open=true});window.scrollTo(0,0)}")
        await pg.wait_for_timeout(300)
        H = await pg.evaluate("document.documentElement.scrollHeight")
        ys = list(range(0, max(1, H - 915), 915 - 60)) + [max(0, H - 915)]
        ys = [y for i, y in enumerate(ys) if i == 0 or y - ys[i - 1] > 200]
        for n, y in enumerate(ys, 1):
            await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(150)
            name = f'p{20 + n:02d}-phone-all-open.png'
            await pg.screenshot(path=str(OUT / name)); add(name, 'phone', f'Phone portrait, everything open, screen {n} of {len(ys)}', f'Every section and submenu open; the page scrolled to {y} px of {H} px.')
        await ctx.close()
        ctx, pg = await page(915, 412, 2, mobile=True)
        await pg.screenshot(path=str(OUT / 'p90-phone-landscape.png')); add('p90-phone-landscape.png', 'phone', 'Phone landscape', 'Three columns squeezed side by side (wider than 900 px).')
        await ctx.close()
        await b.close()
    assert not errs, errs
    (OUT / 'index.json').write_text(json.dumps(SHOTS, indent=1, ensure_ascii=False))
    print(f'[ok] {len(SHOTS)} screenshots in {OUT}')

if __name__ == '__main__':
    asyncio.run(main())
