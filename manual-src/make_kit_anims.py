"""Canvas renders and animation frames for the Google AI Studio kit and the mobile manual.

Every picture is the master canvas (the exact output raster) read back from the real TileSmith page, with the page's
own animation loop frozen and stepped 1/60 s at a time through its own tick() (see HOLD in make_kit_shots.py).
Writes into kit/shots (or KIT_SHOTS): cv-*.png (patterns, wiring, wall shapes), anim-*.png (frame strips, poses)
and anim-*.gif, and appends their descriptions to kit/shots/index.json.
"""
import asyncio, io, json, math, pathlib
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright
import make_kit_shots as K

OUT = K.OUT
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SHOTS = []


def add(name, group, title, notes=''):
    SHOTS.append({'file': name, 'group': group, 'title': title, 'notes': notes})


def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONTB if bold else FONT, sz)
    except Exception:
        return ImageFont.load_default()


def fitw(im, w):
    return im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def grid(frames, labels, cols, w, title=None, pad=8, bg=(13, 18, 23)):
    """frames side by side in rows, each with a label underneath (time, phase ...)."""
    fr = [fitw(f, w) for f in frames]
    h = max(f.height for f in fr)
    lab = 22; top = 34 if title else 0
    rows = math.ceil(len(fr) / cols)
    G = Image.new('RGB', (pad + cols * (w + pad), top + pad + rows * (h + lab + pad)), bg)
    d = ImageDraw.Draw(G)
    if title:
        d.text((pad, 8), title, fill=(230, 237, 243), font=font(18, True))
    for i, (f, t) in enumerate(zip(fr, labels)):
        x = pad + (i % cols) * (w + pad); y = top + pad + (i // cols) * (h + lab + pad)
        G.paste(f, (x, y)); d.text((x, y + h + 3), t, fill=(138, 154, 168), font=font(13))
    return G


def gif(frames, name, fps, w):
    fr = [fitw(f, w).convert('P', palette=Image.ADAPTIVE, colors=192) for f in frames]
    fr[0].save(OUT / name, save_all=True, append_images=fr[1:], duration=round(1000 / fps), loop=0, optimize=True, disposal=1)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=1, color_scheme='dark')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.add_init_script(K.MOCK + K.HOLD)
        await pg.goto(K.APP); await pg.wait_for_timeout(900)
        ev = pg.evaluate
        await ev("()=>__hold()")
        PREP = K.PREP

        async def cv():
            return await K.canvas(pg)

        async def setup(js, frames=2):
            await ev(f"()=>{{{js};{PREP}}}"); await ev(f"()=>__step({frames})")

        async def at(t):
            """jump the made-up clock to T = t seconds (patterns that depend on time) and draw"""
            await ev(f"()=>{{window.__now={t * 1000};lastStep=window.__now;__step(1)}}")

        # ------------------------------------------------------------------ test patterns, one 6x4 wall filling the canvas
        base = "walls=[walls[0]];loadWall(0);S.preset='Unilumin UpadIV 2.6';applyPreset();S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.cw=1152;S.ch=768;M.width=1152;M.height=768;S.lay={};S.gone=[];S.pdir='none';S.ids=false;S.tpos=false;S.addr=false;S.mm=false;S.dvdOn=false;S.proc='None';S.pdist=false;S.wmode='None';S.pmode='None'"
        pats = await ev("PAT_LIST")
        pat_imgs = []
        for i, pn in enumerate(pats):
            extra = ''
            if pn.startswith('branded'):
                extra = ";S.boxMode='Text';S.boxText='YOUR SHOW';S.boxCol='#ffffff'"
            await setup(f"{base};S.pat={json.dumps(pn)}{extra}")
            await at(100.8 if pn == 'tileshade-cycle' else 100.0)
            await pg.wait_for_timeout(150 if pn.startswith(('disguise', 'branded')) else 0)
            await at(100.8 if pn == 'tileshade-cycle' else 100.0)
            im = await cv(); fn = f'cv-pattern-{i + 1:02d}-{pn.replace(" ", "-").replace(":", "x")}.png'
            K.save(im, fn); add(fn, 'pattern', f'Test pattern: {pn}', 'Drawn on a 6 x 4 wall of 192 x 192 px tiles (1152 x 768 px), overlays off (borders always on).')
            pat_imgs.append((im, pn))
        K.save(grid([x[0] for x in pat_imgs], [x[1] for x in pat_imgs], 5, 300, 'All test patterns (6 x 4 wall, overlays off)'), 'cv-patterns-all.png')
        add('cv-patterns-all.png', 'pattern', 'All 25 test patterns at a glance', '')
        await setup(f"{base};S.pat='tileshade';S.ids=true;S.tpos=true;S.addr=true;S.mm=true;S.bt=3"); await at(100)
        K.save(await cv(), 'cv-overlays-all.png'); add('cv-overlays-all.png', 'pattern', 'Every tile overlay on (tileshade)', 'Tile ID "T05 [C5:R1]", pixel address in yellow, size in mm in cyan, position arrows (↑ row from the bottom, → column from the left).')
        await setup(f"{base};S.pat='tileshade'"); await at(100)
        await ev("()=>{const w=walls[0];}")

        # ------------------------------------------------------------------ data wiring: 10 x 5 wall, NovaStar VX1000 Pro (17 tiles per port)
        wbase = "walls=[walls[0]];loadWall(0);S.preset='Unilumin UpadIV 2.6';applyPreset();S.cols=10;S.rows=5;S.ox=0;S.oy=0;S.cw=1920;S.ch=960;M.width=1920;M.height=960;S.pat='tileshade-clean';S.ids=false;S.tpos=false;S.addr=false;S.mm=false;S.lay={};S.gone=[]"
        fills = await ev("WFILL"); pfills = await ev("PFILL")
        imgs = []
        for i, f in enumerate(fills):
            await setup(f"{wbase};S.proc='NovaStar VX1000 Pro';applySpec();S.pdist=false;S.pmode='None';S.wmode='Snake';S.wcorner='Top-left';S.wdir='Horizontal';S.wfill={json.dumps(f)}"); await at(100)
            im = await cv(); fn = f'cv-data-wiring-{i + 1}-{f.lower().replace(" ", "-")}.png'; K.save(im, fn); imgs.append(im)
            add(fn, 'wiring', f'Data wiring preference: {f}', '10 x 5 wall, NovaStar VX1000 Pro at 60 Hz 8-bit = 650,000 px per port = 17 tiles per port; Snake from the top-left, horizontal.')
        K.save(grid(imgs, fills, 3, 420, 'Data wiring preferences (Snake, top-left, horizontal, 17 tiles per port)'), 'cv-data-wiring-all.png'); add('cv-data-wiring-all.png', 'wiring', 'All data wiring preferences side by side', '')
        imgs = []
        for i, f in enumerate(pfills):
            await setup(f"{wbase};S.proc='None';S.wmode='None';S.pdist=true;S.pvolt=120;S.pamps=20;S.derate=true;S.plink=0;S.pmode='Snake';S.pcorner='Top-left';S.pwdir='Horizontal';S.pfill={json.dumps(f)}"); await at(100)
            im = await cv(); fn = f'cv-power-wiring-{i + 1}-{f.lower().replace(" ", "-")}.png'; K.save(im, fn); imgs.append(im)
            add(fn, 'wiring', f'Power wiring preference: {f}', '10 x 5 wall, 120 V 20 A loaded to 80% = 1,920 W = 16 tiles of 120 W per circuit; Snake from the top-left, horizontal.')
        K.save(grid(imgs, pfills, 3, 420, 'Power wiring preferences (Snake, top-left, horizontal, 16 tiles per circuit)'), 'cv-power-wiring-all.png'); add('cv-power-wiring-all.png', 'wiring', 'All power wiring preferences side by side', '')
        wpat = await ev("WPAT")
        for mode in ('Snake', 'Linear'):
            imgs = []; labs = []
            for c, d in wpat:
                await setup(f"{wbase};S.cols=6;S.rows=4;S.cw=1152;S.ch=768;M.width=1152;M.height=768;S.proc='NovaStar VX1000 Pro';applySpec();S.pdist=false;S.wmode='{mode}';S.wcorner='{c}';S.wdir='{d}';S.wfill='One continuous path'"); await at(100)
                imgs.append(await cv()); labs.append(f'{c}, {d.lower()}')
            fn = f'cv-data-{mode.lower()}-8-starts.png'; K.save(grid(imgs, labs, 4, 300, f'{mode}: the 8 start corners and directions'), fn)
            add(fn, 'wiring', f'{mode} data wiring from each of the 8 starts', '6 x 4 wall, One continuous path (17 tiles per port), so the path order is easy to follow.')
        await setup(f"{wbase};S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.wfill='Fewest ports';S.pdist=true;S.pmode='Snake';S.pfill='Fewest circuits';S.ids=true"); await at(100)
        K.save(await cv(), 'cv-data-and-power.png'); add('cv-data-and-power.png', 'wiring', 'Data and power on one wall', 'Data runs at the tile centre minus 0.2 tile width; power at plus 0.2 width and 0.2 height, white on a black casing, with lightning-bolt circuit badges.')

        # ------------------------------------------------------------------ wall shapes and multiple walls
        await setup("walls=[walls[0]];loadWall(0);S.proc='None';S.wmode='None';S.pdist=false;S.pmode='None';S.preset='ROE Carbon CB5';applyPreset();S.cols=6;S.rows=3;S.ox=0;S.oy=0;S.cw=624;S.ch=624;M.width=624;M.height=624;S.pat='tileshade';S.ids=true;S.tpos=true;S.gone=[];S.half=[];S.lay={s:'h',uc:6,ur:6,p:[[0,1,1,1],[1,0,1,2],[2,0,1,2],[3,0,1,2],[4,0,1,2],[5,1,1,1],[0,2,1,2],[1,2,1,2],[2,2,2,1],[2,3,1,1],[3,3,1,1],[4,2,1,2],[5,2,1,2],[0,4,1,2],[1,4,1,2],[2,4,1,2],[3,4,1,2],[4,4,1,2],[5,4,1,2]]}"); await at(100)
        K.save(await cv(), 'cv-half-tiles.png'); add('cv-half-tiles.png', 'shape', 'Half tiles (ROE Carbon CB5)', 'Top row: half tiles at both ends, full tiles offset by half a tile between them; row 2: one full tile turned on its side over two halves. IDs of half tiles end in ½.')
        await setup("S.preset='Unilumin UpadIV 2.6';applyPreset();S.lay={};S.cols=8;S.rows=4;S.cw=1536;S.ch=768;M.width=1536;M.height=768;S.gone=[[0,0],[1,0],[6,0],[7,0],[0,1],[7,1]]"); await at(100)
        K.save(await cv(), 'cv-removed-tiles.png'); add('cv-removed-tiles.png', 'shape', 'Removed tiles', '8 x 4 wall with six corner tiles removed; tile IDs keep their grid numbers.')
        await setup("S.gone=[];S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.cw=1920;S.ch=1080;M.width=1920;M.height=1080;S.ids=true;S.tpos=true;S.name='Main';S.pat='tileshade';storeWall();addWall(false);addWall(false);Object.assign(walls[1],{name:'Side',ox:1154,oy:0,cols:3,rows:3,pat:'SMPTEbars'});Object.assign(walls[2],{name:'Floor',ox:0,oy:800,cols:8,rows:1,pat:'rgbramp'});loadWall(0)"); await at(100)
        K.save(await cv(), 'cv-three-walls.png'); add('cv-three-walls.png', 'shape', 'Three walls on one canvas', 'Each wall has its own pattern; with several walls tile IDs start with W1, W2 ...')

        # ------------------------------------------------------------------ build animation
        # one 6 x 3 wall filling a 1152 x 576 canvas: the technician is 0.42 x 576 = 242 px tall
        bbase = "walls=[walls[0]];loadWall(0);S.preset='Unilumin UpadIV 2.6';applyPreset();S.cols=6;S.rows=3;S.ox=0;S.oy=0;S.cw=1152;S.ch=576;M.width=1152;M.height=576;S.pat='tileshade';S.ids=true;S.tpos=false;S.addr=false;S.mm=false;S.lay={};S.gone=[];S.dvdOn=false;S.speed=1;S.loop=false;S.corner='Top-left';S.dir='Horizontal';S.cd=true;S.proc='None';S.pdist=false"
        await setup(bbase); await at(100); await ev("()=>{reset();S.play=true;lastStep=window.__now;__step(1)}")
        frames = []; labels = []; info = []
        fps = 15; total = 10.0
        for k in range(int(total * fps) + 1):
            if k: await ev(f"()=>__step({60 // fps})")
            s = await ev("()=>{const x=sims[0];return{ph:x.ph,t:+x.t.toFixed(2),i:x.i,inst:x.inst}}")
            frames.append(await cv()); labels.append(f"{k / fps:.2f} s  {s['ph']} tile {s['i'] + 1}"); info.append(s)
        gif(frames, 'anim-build-first-tiles.gif', fps, 576); add('anim-build-first-tiles.gif', 'animation', 'Build animation: the first two tiles (real time, 15 fps)', 'Phases per tile at Speed 1: walkin 0.8 s, move 1.1 s, place 0.8 s, lock 0.6 s, walkout 1.5 s = 4.8 s per tile.')
        pick = [i for i in range(0, 73, 3)][:24]
        K.save(grid([frames[i] for i in pick], [labels[i] for i in pick], 4, 360, 'Build animation, first tile, every 0.2 s (Speed 1)'), 'anim-build-strip.png')
        add('anim-build-strip.png', 'animation', 'Build animation frame strip (first tile)', 'walkin: walks in from the wall edge carrying the tile; move: walks beside the slot; place: turns and lifts the tile into place (it grows from carry size to full size); lock: the tile flashes into place and a ring sparkle expands; walkout: turns and walks off.')
        # close-ups of each phase (left part of the canvas around the first slot)
        moments = [(0.6, 'walkin (carrying)'), (1.3, 'move'), (2.0, 'place: turning'), (2.5, 'place: lifting'), (2.75, 'lock'), (3.05, 'lock: sparkle'), (3.5, 'walkout: turning'), (4.4, 'walkout: leaving')]
        crops = []
        for t, lab in moments:
            k = round(t * fps); crops.append(frames[k].crop((0, 0, 576, 576)))
        K.save(grid(crops, [f'{t:.2f} s  {lab}' for t, lab in moments], 4, 288, 'Technician close-ups by phase'), 'anim-tech-phases.png')
        add('anim-tech-phases.png', 'animation', 'Technician close-ups by phase', '')
        # whole wall time-lapse at Speed 4
        await setup(bbase + ";S.speed=4"); await at(100); await ev("()=>{reset();S.play=true;lastStep=window.__now;__step(1)}")
        tl = []
        for k in range(0, 24 * 10 + 1):
            if k: await ev("()=>__step(5)")
            tl.append(await cv())
            if await ev("allDone()"): break
        for _ in range(12): tl.append(tl[-1])
        gif(tl, 'anim-build-timelapse.gif', 12, 576); add('anim-build-timelapse.gif', 'animation', 'Whole 6 x 3 wall built at Speed 4', 'Tiles are placed row by row from the top-left (Tech starts at = Top-left, Tile placement = Horizontal).')
        K.save(grid(tl[::max(1, len(tl) // 8)][:8], [f'{i * max(1, len(tl) // 8) * 5 / 60 * 4:.0f} s (real build time)' for i in range(8)], 4, 360, 'Build progress at Speed 4'), 'anim-build-progress.png')
        add('anim-build-progress.png', 'animation', 'Build progress (snapshots)', '')
        # three walls start 0.6 s apart with different rates
        await setup(bbase + ";S.cw=1920;S.ch=1080;M.width=1920;M.height=1080;S.cols=4;S.rows=3;S.name='A';storeWall();addWall(false);S.name='B';storeWall();addWall(false);S.name='C';storeWall();walls[0].ox=0;walls[0].oy=0;walls[1].ox=772;walls[1].oy=0;walls[2].ox=0;walls[2].oy=580;loadWall(0)"); await at(100)
        await ev("()=>{reset();S.play=true;lastStep=window.__now;__step(1)}")
        mw = []; mlab = []
        for k in range(8):
            if k: await ev("()=>__step(30)")
            mw.append(await cv()); mlab.append(f'{k * 0.5:.1f} s')
        K.save(grid(mw, mlab, 4, 360, 'Three walls: wall i starts i x 0.6 s later, each at its own pace'), 'anim-multiwall-start.png')
        add('anim-multiwall-start.png', 'animation', 'Several walls building at once', 'Per-wall pace multipliers 1, 0.88, 1.1, 0.94, 1.06, 0.84, 1.14, 0.97; one crew member per wall at a time.')

        # technician pose sheet, drawn straight with the app's own drawTech() on a separate canvas
        poses = await ev("""()=>{const out=[];const C=document.createElement('canvas');C.width=260;C.height=300;const c=C.getContext('2d');
          const shot=(o,m)=>{c.fillStyle='#1a222b';c.fillRect(0,0,260,300);drawTech(c,130,285,250,Object.assign({th:Math.PI/2,mv:0,g:0,u:0,m:m||crew[0],carry:false,lock:false,shake:0,hands:null},o));return C.toDataURL()};
          const A=[[Math.PI/2,'front (π/2)'],[.75,'walk angle 0.75'],[.3,'work angle 0.3'],[Math.PI-.75,'3/4 left (π-0.75)'],[-Math.PI/2,'back (-π/2)']];
          A.forEach(([th,n])=>out.push([shot({th}),n]));
          [0,1,2,3].forEach(k=>out.push([shot({th:.75,mv:1,g:k*Math.PI/2}),'walk, g = '+(k*90)+'°']));
          out.push([shot({th:.3,carry:true,u:0}),'arms: carry, u = 0']);out.push([shot({th:.3,carry:true,u:1}),'arms: carry, u = 1']);out.push([shot({th:.3,lock:true,u:1}),'arms: lock']);
          crew.forEach((m,i)=>out.push([shot({th:Math.PI/2},m),m[0]]));return out}""")
        pim = [K.png_from_dataurl(u) for u, _ in poses]
        K.save(grid(pim, [n for _, n in poses], 6, 200, 'Technician drawn by drawTech(c, x, y, size, pose): angles, walk cycle, arms, default crew'), 'anim-tech-poses.png')
        add('anim-tech-poses.png', 'animation', 'Technician pose sheet', 'th = facing angle (π/2 front, 0 side right, π side left, -π/2 back); mv = walking amount; g = gait phase (radians, advances with x position); u = lift amount; carry/lock = arm poses. Crew rotate: Marcus, Elena, David, Chen, Priya, Malik.')
        looks = await ev("""()=>{const out=[];const C=document.createElement('canvas');C.width=260;C.height=300;const c=C.getContext('2d');const keep=[S.hat,S.vest,S.logo,S.cd];
          const L=[['#ffcc00','#b6ff00','TILESMITH',true,'default'],['#ffffff','#ff6a00','CREW',true,'white hat, orange vest'],['#e11d48','#f5e800','LED',false,'red hat, no name tag']];
          L.forEach(([h,v,l,cd,n])=>{S.hat=h;S.vest=v;S.logo=l;S.cd=cd;c.fillStyle='#1a222b';c.fillRect(0,0,260,300);drawTech(c,130,285,250,{th:Math.PI/2,mv:0,g:0,u:0,m:crew[1],carry:false,lock:false,shake:0,hands:null});out.push([C.toDataURL(),n]);
            c.fillStyle='#1a222b';c.fillRect(0,0,260,300);drawTech(c,130,285,250,{th:-Math.PI/2,mv:0,g:0,u:0,m:crew[1],carry:false,lock:false,shake:0,hands:null});out.push([C.toDataURL(),'back: logo '+l])});
          [S.hat,S.vest,S.logo,S.cd]=keep;return out}""")
        K.save(grid([K.png_from_dataurl(u) for u, _ in looks], [n for _, n in looks], 6, 200, 'Technician options: hard hat and vest colours, vest logo text, name tags'), 'anim-tech-looks.png')
        add('anim-tech-looks.png', 'animation', 'Technician options', 'From the Technician submenu: Hard hat colour, Vest colour, Vest logo text (or image), Crew details & name tags.')
        # the carried tile (cab) at full size
        cabu = await ev("""()=>{const C=document.createElement('canvas');C.width=240;C.height=240;const c=C.getContext('2d');c.fillStyle='#050608';c.fillRect(0,0,240,240);cab(c,120,120,{tw:192,th:192},1);return C.toDataURL()}""")
        K.save(K.png_from_dataurl(cabu), 'anim-carried-tile.png'); add('anim-carried-tile.png', 'animation', 'The carried tile (cab)', 'Dark #1b2028 face, #8ea0b0 frame, amber #e8c11c corner marks, black handle bar in the middle; drawn at the tile size times the carry scale.')

        # ------------------------------------------------------------------ DVD screensaver
        await setup("walls=[walls[0]];loadWall(0);S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.cw=1152;S.ch=768;M.width=1152;M.height=768;S.pat='SMPTEbars';S.ids=false;S.tpos=false;S.dvdOn=true;S.dvdSrc='TileSmith logo';S.dvdArea='Each LED wall';S.dvdSize=20;S.dvdSpeed=1;S.dvdCorner=10;S.dvdTint=true;S.dvdLoop=false;DVD_ST.delete(walls[0])"); await at(100)
        dv = []; dlab = []
        for k in range(0, 8 * 15 + 1):
            if k: await ev("()=>__step(4)")
            dv.append(await cv())
            st = await ev("()=>{const s=DVD_ST.get(walls[0]);return s?{b:s.b,c:s.c,hue:s.hue}:null}")
            dlab.append(f"{k / 15:.1f} s  bounces {st['b'] if st else 0}")
        gif(dv, 'anim-dvd.gif', 15, 576); add('anim-dvd.gif', 'animation', 'DVD screensaver (8 s, real time)', 'Logo height 20% of the wall\'s shorter side, speed 0.25 x shorter side per second, recoloured at every bounce.')
        K.save(grid(dv[::10][:12], dlab[::10][:12], 4, 300, 'DVD screensaver every 0.67 s'), 'anim-dvd-strip.png'); add('anim-dvd-strip.png', 'animation', 'DVD screensaver frame strip', '')
        await setup("S.dvdCorner=100;DVD_ST.delete(walls[0])"); await at(200)
        dv = []; hit = None
        for k in range(0, 20 * 15):
            if k: await ev("()=>__step(4)")
            dv.append(await cv())
            st = await ev("()=>{const s=DVD_ST.get(walls[0]);return s?s.c:0}")
            if st and hit is None: hit = k
            if hit is not None and k > hit + 12: break
        gif(dv[max(0, (hit or 0) - 30):], 'anim-dvd-corner.gif', 15, 576); add('anim-dvd-corner.gif', 'animation', 'DVD corner hit (corner hit chance 100)', 'At 100 about 45% of bounces aim for a corner.')
        sprites = await ev("""()=>{const out=[];[['TileSmith logo',''],['Text','YOUR SHOW']].forEach(([src,t])=>{S.dvdSrc=src;S.dvdText=t;DVD_SPR.clear();const s=dvdSpr(null);if(s){const C=document.createElement('canvas');C.width=s.width+20;C.height=s.height+20;const c=C.getContext('2d');c.fillStyle='#000';c.fillRect(0,0,C.width,C.height);c.drawImage(s,10,10);out.push([C.toDataURL(),src])}
          const h=dvdSpr(200);if(h){const C=document.createElement('canvas');C.width=h.width+20;C.height=h.height+20;const c=C.getContext('2d');c.fillStyle='#000';c.fillRect(0,0,C.width,C.height);c.drawImage(h,10,10);out.push([C.toDataURL(),src+' (recoloured, hue 200)'])}});S.dvdSrc='TileSmith logo';S.dvdText='TILESMITH';return out}""")
        K.save(grid([K.png_from_dataurl(u) for u, _ in sprites], [n for _, n in sprites], 2, 460, 'DVD logo sprites (200 px tall)'), 'anim-dvd-sprites.png'); add('anim-dvd-sprites.png', 'animation', 'DVD logo sprites', '')
        await setup("S.dvdOn=false;S.dvdCorner=10")

        # ------------------------------------------------------------------ moving patterns
        pbase = "walls=[walls[0]];loadWall(0);S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.cw=1152;S.ch=768;M.width=1152;M.height=768;S.ids=false;S.tpos=false;S.dvdOn=false;S.pdir='none'"
        await setup(pbase + ";S.pat='tileshade-cycle'")
        tc = []; tcl = []
        for k in range(0, 76):
            t = 100 + k / 10; await at(t); tc.append(await cv()); tcl.append(f'T = {t - 100:.1f} s')
        gif(tc, 'anim-tileshade-cycle.gif', 10, 576); add('anim-tileshade-cycle.gif', 'animation', 'tileshade-cycle (7.5 s)', 'Each tile holds its colour for 1.0 s, then for 1.5 s the next colour slides in from the left (smoothstep easing) and pushes the current one out: one step every 2.5 s.')
        sel = [9, 10, 12, 14, 16, 18, 20, 22, 24, 25]
        K.save(grid([tc[i] for i in sel], [tcl[i] for i in sel], 5, 300, 'tileshade-cycle: one 2.5 s step (slide from T = 1.0 s to 2.5 s)'), 'anim-tileshade-cycle-strip.png'); add('anim-tileshade-cycle-strip.png', 'animation', 'tileshade-cycle frame strip', '')
        await setup(pbase + ";S.pat='cycle'")
        cy = []; cyl = []
        for k in range(8):
            await at(100.2 + k * 1.5); cy.append(await cv()); cyl.append(f'T = {k * 1.5:.1f} s')
        K.save(grid(cy, cyl, 4, 300, 'cycle: full-field colour, one step every 1.5 s'), 'anim-cycle-strip.png'); add('anim-cycle-strip.png', 'animation', 'cycle frame strip', 'Colours #f00 #0f0 #00f #fff #000 #ff0 #0ff #f0f; index = floor(T / 1.5) mod 8.')
        await setup(pbase + ";S.pat='sweep'")
        sw = []; swl = []
        for k in range(0, 61):
            await at(100 + k / 10); sw.append(await cv()); swl.append(f'T = {k / 10:.1f} s')
        gif(sw, 'anim-sweep.gif', 10, 576); add('anim-sweep.gif', 'animation', 'sweep (6 s)', 'Rainbow gradient whose hues move with time; redrawn every frame.')
        K.save(grid(sw[::10][:6], swl[::10][:6], 3, 360, 'sweep every 1 s'), 'anim-sweep-strip.png'); add('anim-sweep-strip.png', 'animation', 'sweep frame strip', '')
        await setup(pbase + ";S.pat='SMPTEbars';S.pdir='diagonal ↘';S.pspd=1")
        sc = []; scl = []
        await ev("()=>{window.__now=100000;lastStep=window.__now}")
        for k in range(0, 61):
            if k: await ev("()=>__step(6)")
            sc.append(await cv()); scl.append(f'{k / 10:.1f} s')
        gif(sc, 'anim-scroll.gif', 10, 576); add('anim-scroll.gif', 'animation', 'Scroll: SMPTEbars, diagonal ↘, speed 1 (6 s)', 'Speed = Scroll speed x 0.2 x the wall\'s shorter side in px per second; the image wraps around.')
        K.save(grid(sc[::12][:6], scl[::12][:6], 3, 360, 'Scroll diagonal ↘ every 1.2 s'), 'anim-scroll-strip.png'); add('anim-scroll-strip.png', 'animation', 'Scroll frame strip', '')
        await b.close()
    assert not errs, errs
    idx = OUT / 'index.json'
    old = json.loads(idx.read_text()) if idx.exists() else []
    names = {s['file'] for s in SHOTS}
    idx.write_text(json.dumps([s for s in old if s['file'] not in names] + SHOTS, indent=1, ensure_ascii=False))
    print(f'[ok] {len(SHOTS)} canvas renders and animations in {OUT}')

if __name__ == '__main__':
    asyncio.run(main())
