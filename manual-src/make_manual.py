# Builds TileSmith-Manual.pdf from the current app.
# Lists (patterns, processors, video formats, wiring patterns, presets, CSV columns) are read from app/index.html,
# and screenshots are taken from the running app, so the manual always matches the build it ships with.
# Run: python3 make_manual.py   (fails if a pattern, fit mode or video format has no description here)
import asyncio, json, html, pathlib, datetime, base64, os
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get('TILESMITH_ROOT', HERE.parent / 'tilesmith-desktop'))   # the app folder (next to manual-src)
APP = 'file://' + str(ROOT / 'app' / 'index.html')
OUT = pathlib.Path(os.environ.get('MANUAL_OUT', ROOT / 'TileSmith-Manual.pdf'))  # MANUAL_OUT: preview somewhere else
SHOTS = pathlib.Path(os.environ.get('MANUAL_SHOTS', HERE / 'shots')); SHOTS.mkdir(exist_ok=True)
VERSION = json.loads((ROOT / 'package.json').read_text())['version'].rsplit('.0', 1)[0]
TODAY = datetime.date.today().strftime('%B %-d, %Y')
E = html.escape

PATTERN_DESC = {
 'tileshade': 'Pixel map. Every tile is a light or dark shade of one colour (set it with <b>Tile-shade color</b>), with corner-to-corner diagonals, a centre circle, the wall name and resolution in the middle, the canvas position of the first tile\'s top-left corner in a see-through dark box, and a footer with the wall name, position, columns, rows, cabinet count, resolution and aspect ratio. This is the default pattern.',
 'tileshade-clean': 'The same pixel map without the name, size and position boxes on the wall; that information is only in the footer.',
 'tileshade-cycle': 'The tileshade layout with every tile stepping through red, green and blue. Each colour holds for a second, then the next one slides in from the left over 1.5 seconds. Each tile starts at a different point in the sequence, so a tile never shows the same colour as the tiles above, below, left or right of it. Good for spotting dead pixels, colour mismatches and swapped tiles. Tile-shade color is not used.',
 'SMPTEbars': 'Classic SMPTE colour bars, drawn by TileSmith at 1920 × 1080. Image fit and Scroll apply.',
 'ramp': '16-step greyscale from black to white, left to right.',
 'sweep': 'Moving rainbow with a light-to-dark vertical fade (animated).',
 'white': 'Full-field white.', 'red': 'Full-field red.', 'green': 'Full-field green.', 'blue': 'Full-field blue.',
 'black': 'Full-field black.', 'gray50': 'Full-field 50% grey.',
 'smptescroll': 'SMPTE bars image. Picking it switches Scroll to diagonal if Scroll was off.',
 'disguise test pattern 16:9': 'Built-in 1920 × 1080 image with grid, circles, greyscale steps and colour references.',
 'disguise test pattern 4:3': 'Built-in 1024 × 768 version of the same image.',
 'branded test pattern 16:9': 'Built-in 1920 × 1080 colour bars with a black centre box. Put your own text or logo in the box with <b>Center box</b>.',
 'branded test pattern 4:3': 'Built-in 1024 × 768 version with the same centre box.',
 'custom': 'Your own image: click <b>Upload test pattern</b>. Images keep their full size up to 8192 px. Image fit and Scroll apply.',
 'pixel1': 'Single-pixel checkerboard (every other pixel on). Good for checking pixel mapping and receiving-card setup.',
 'circles': 'Circles and crosshairs for checking geometry and aspect ratio.',
 'gradH': 'Smooth black-to-white gradient, left to right.', 'gradV': 'Smooth black-to-white gradient, top to bottom.',
 'rgbramp': 'Four ramps from black to red, green, blue and white.',
 'zone': 'Zone plate (concentric rings) for spotting scaling and moiré.',
 'cycle': 'Full-field colour that changes every 1.5 seconds (animated).',
}
FIT_DESC = {
 'Stretch to wall': 'Fills the wall exactly. The image is stretched if its shape differs from the wall.',
 'Fit inside wall': 'Shows the whole image without stretching; black bars fill the gaps.',
 'Fill wall (crops edges)': 'Fills the wall without stretching; the edges that do not fit are cut off.',
 'Original size on canvas': 'No scaling. The image sits at the top-left corner of the master canvas and each wall shows the part of the image underneath it, like content coming from a media server. Use this when your image was made at canvas resolution.',
 'Original size on wall': 'No scaling. The image starts at the wall\'s own top-left corner.',
}
FILL_DESC = {
 'Fewest ports': 'Each port gets a rectangle of tiles, sized to use as few ports as possible. The pattern repeats inside every rectangle, like NovaLCT\'s quick connection.',
 'Whole rows or columns': 'Each port takes complete rows (complete columns when vertical). If a port cannot drive a whole line, the line is split evenly between ports.',
 'One continuous path': 'One path runs through the whole wall and is cut wherever a port is full, so a port can start partway along a line.',
 'Horizontal': 'Each port takes a horizontal band: complete rows across the whole wall, as many as it can drive, whichever way the pattern runs. With a vertical pattern the path snakes up and down inside each band. If a port cannot drive a whole row, each row is split evenly between ports.',
 'Vertical': 'Each port takes a vertical band: complete columns down the whole wall, as many as it can drive, whichever way the pattern runs. With a horizontal pattern the path snakes back and forth inside each band. If a port cannot drive a whole column, each column is split evenly between ports.',
}
PFILL_DESC = {
 'Fewest circuits': 'Each circuit gets a rectangle of tiles, sized to use as few circuits as possible. The pattern repeats inside every rectangle.',
 'Whole rows or columns': 'Each circuit takes complete rows (complete columns when vertical). If a circuit cannot power a whole line, the line is split evenly between circuits.',
 'One continuous path': 'One path runs through the whole wall and is cut wherever a circuit is full, so a circuit can start partway along a line.',
 'Horizontal': 'Each circuit takes a horizontal band: complete rows across the whole wall, as many as it can power, whichever way the pattern runs. If a circuit cannot power a whole row, each row is split evenly between circuits.',
 'Vertical': 'Each circuit takes a vertical band: complete columns down the whole wall, as many as it can power, whichever way the pattern runs. If a circuit cannot power a whole column, each column is split evenly between circuits.',
}
# Licence texts of the Spout and Syphon parts that ship in the desktop app (repeated in the manual, as their licences ask)
TX_LICENSES = [
 ('Spout SDK: SpoutDX (Simplified BSD licence)', 'Included in the Windows build (SpoutDX.dll, Spout SDK 2.007.017). https://github.com/leadedge/Spout2', """SpoutSDK is released under the Simplified BSD licence.

Copyright (C) 2014-2022. Lynn Jarvis. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""),
 ('Syphon Framework (BSD license)', 'Included in the Mac build (Syphon.framework 5). https://github.com/Syphon/Syphon-Framework', """Copyright 2010 bangnoise (Tom Butterworth) & vade (Anton Marini). All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of the Syphon Project nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""),
 ('node-syphon (MIT License)', 'Included in the Mac build (syphon.node from node-syphon 1.5.5). https://github.com/benoitlahoz/node-syphon', """MIT License

Copyright (c) 2023 Benoît Lahoz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""),
]

# Pretends to be the Windows (or Mac) desktop app with Spout (or Syphon) built in, so the screenshots show the
# Start Spout button and the Spout / Syphon options as the desktop app draws them. Nothing is loaded or sent.
DESK_MOCK = r"""
(()=>{const plat=window.__PLAT;
const fsm={existsSync:p=>/SpoutDX\.dll$|syphon\.node$|Syphon\.framework$/.test(p),readFileSync(){throw Error('nofile')},writeFileSync(){},mkdirSync(){},readdirSync:()=>[],unlinkSync(){}};
const pathm={join:(...a)=>a.join(plat=='win32'?'\\':'/'),dirname:p=>p.replace(/[\\/][^\\/]*$/,''),basename:p=>p.replace(/^.*[\\/]/,'')};
class MetalServer{constructor(n){this._n=n}publishImageData(){}dispose(){}get hasClients(){return true}get name(){return this._n}}
const lib={func(n){return(...a)=>/GetName/.test(n)?'TileSmith':/Heap/.test(n)?{p:1}:true}};
window.process={platform:plat,versions:{electron:'44.0.0'},resourcesPath:plat=='win32'?'C:\\res':'/App/Contents/Resources',cwd:()=>plat=='win32'?'C:\\proj':'/proj',env:{}};
window.Buffer={from:(ab,o,l)=>new Uint8Array(ab,o,l)};
window.require=m=>{if(m=='fs')return fsm;if(m=='path')return pathm;if(m=='os')return{homedir:()=>'/home/x'};if(m=='koffi')return{load:()=>lib,struct(){}};
 if(m=='electron')return{ipcRenderer:{send(){}},shell:{openPath(){},openExternal(){},showItemInFolder(){}}};if(/syphon\.node$/.test(m))return{MetalServer};throw Error('no module '+m)};
})();
"""

async def shots_and_data():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1500, 'height': 900}, device_scale_factor=2, color_scheme='dark')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(1200)
        ev = pg.evaluate
        data = await ev("""()=>({pats:PAT_LIST,fits:PFIT,fills:WFILL,pfills:PFILL,half:Object.entries(HALF).map(([k,v])=>({full:k,half:v[0],split:v[1],f:P[k],h:P[v[0]]})),scroll:[...document.querySelectorAll('select[data-k=pdir] option')].map(o=>o.value),
          procs:Object.entries(PROC).filter(([k,m])=>m).map(([k,m])=>({name:k,brand:m.brand,ports:m.ports,px:m.px,hz:m.hz,bpc:m.bpc,note:m.note})),
          codecs:Object.entries(VCODEC).map(([k,v])=>({name:k,ext:v.ext,enc:v.enc,note:v.note})),
          res:Object.entries(R),presets:Object.entries(P).filter(([k,v])=>v),
          csv:csv().split('\\n')[0],
          wp:WPAT.map(([c,d])=>({c,d,snake:wpatSvg(c,d,true),linear:wpatSvg(c,d,false)})),
          fps:[...document.querySelectorAll('select[data-k=ndiFps] option')].map(o=>o.value),shfps:[...document.querySelectorAll('select[data-k=shFps] option')].map(o=>o.value),
          dvdSrc:[...document.querySelectorAll('select[data-k=dvdSrc] option')].map(o=>o.value)})""")
        async def shot(name, clip=None, el=None):
            path = SHOTS / f'{name}.png'
            if el: await pg.locator(el).first.screenshot(path=str(path))
            else: await pg.screenshot(path=str(path), clip=clip)
            return path
        from PIL import Image
        def crop(name, maxh):
            f = SHOTS / f'{name}.png'; im = Image.open(f)
            if im.height > maxh * 2: im.crop((0, 0, im.width, maxh * 2)).save(f)
        async def sect(title, name, maxh=560):
            loc = pg.locator(f'xpath=//details[summary[contains(normalize-space(.), "{title}")]]').first
            await loc.evaluate("d=>{for(let e=d;e;e=e.parentElement&&e.parentElement.closest('details'))e.open=true}")
            await loc.scroll_into_view_if_needed(); await pg.wait_for_timeout(150)
            await loc.screenshot(path=str(SHOTS / f'{name}.png')); crop(name, maxh)
        VP = {'x': 350, 'y': 80, 'width': 840, 'height': 640}
        # overview: two walls on a 1080p canvas, data paths on
        await ev("""()=>{S.name='Main';S.cols=6;S.rows=4;S.ox=0;S.oy=0;S.pat='tileshade';storeWall();showAll();addWall(false);S.name='Side';S.cols=4;S.rows=3;S.ox=1200;S.oy=300;storeWall();showAll();
           S.proc='NovaStar VX1000 Pro';applySpec();walls.forEach(w=>{w.wmode='Snake'});S.wmode='Snake';storeWall();sync();fit()}""")
        await pg.wait_for_timeout(500); await shot('overview')
        await sect('Canvas', 'sec_canvas', 330); await sect('LED walls', 'sec_walls'); await sect('Size of LED Wall', 'sec_size')
        await ev("()=>{document.querySelector('#wireBox').closest('details').open=false}"); await sect('LED processor', 'sec_proc'); await sect('Data wiring', 'sec_wiring')
        await shot('engineering', el='#right'); crop('engineering', 560)
        # wiring close-up: one 10 x 5 wall
        await ev("""()=>{selWall(1);delWall();S.cols=10;S.rows=5;S.ox=0;S.oy=0;S.ids=true;storeWall();showAll();sync();fit()}"""); await pg.wait_for_timeout(400)
        await shot('wiring', VP)
        await ev("()=>{S.wmode='None';S.proc='None';S.pdist=true;S.pmode='Snake';S.ids=false;storeWall();sync()}"); await pg.wait_for_timeout(400)
        await shot('power', VP)
        await ev("()=>{document.querySelector('#pwireBox').closest('details').open=false}"); await sect('Power', 'sec_power'); await sect('Power wiring', 'sec_pwiring')
        await ev("()=>{S.pmode='None';S.pdist=false;S.ids=true;storeWall();sync()}")
        # branded pattern with centre box text
        await ev("""()=>{S.pat='branded test pattern 16:9';S.boxMode='Text';S.boxText='YOUR SHOW NAME';S.ids=false;S.cols=10;S.rows=6;storeWall();showAll();sync();fit()}"""); await pg.wait_for_timeout(500)
        await shot('branded', VP); await sect('Test pattern', 'sec_pattern')
        # original size on canvas across two walls
        await ev("""()=>{S.pat='disguise test pattern 16:9';S.pfit='Original size on canvas';S.cols=5;S.rows=4;S.ox=0;S.oy=0;storeWall();showAll();addWall(true);S.ox=1152;S.oy=330;S.cols=4;S.rows=4;storeWall();showAll();sync();fit()}""")
        await pg.wait_for_timeout(600); await shot('fit_canvas', VP)
        await ev("()=>{selWall(1);delWall();S.pat='tileshade';S.pfit='Stretch to wall';S.ids=true;S.cols=6;S.rows=4;storeWall();showAll();sync();fit()}")
        # build in progress
        await ev("()=>{reset();S.play=true;for(let i=0;i<60*28;i++)step(1/60);S.play=false;forceRen=true}"); await pg.wait_for_timeout(500)
        await shot('build', VP); await ev("()=>{showAll()}")
        # DVD bounce
        await ev("()=>{S.dvdOn=true;S.dvdSize=24;S.pat='SMPTEbars';S.ids=false;storeWall();sync()}"); await pg.wait_for_timeout(1500)
        await shot('dvd', VP); await sect('DVD screensaver', 'sec_dvd'); await sect('Build options', 'sec_anim', 380)
        await ev("()=>{S.dvdOn=false;S.ids=true;S.pat='tileshade';storeWall();sync()}")
        await sect('NDI® options', 'sec_ndi')
        await sect('Video export', 'sec_video'); await sect('Technician', 'sec_tech')
        await sect('Tile model', 'sec_tile'); await sect('Tile borders', 'sec_borders')
        # half tiles: a Carbon CB5 wall with half panels along the top and two in the bottom row
        await ev("""()=>{S.preset='ROE Carbon CB5';applyPreset();S.cols=6;S.rows=3;S.ox=0;S.oy=0;S.pat='tileshade';S.half=[];S.lay={s:'h',uc:6,ur:6,p:[[0,1,1,1],[1,0,1,2],[2,0,1,2],[3,0,1,2],[4,0,1,2],[5,1,1,1],[0,2,1,2],[1,2,1,2],[2,2,2,1],[2,3,1,1],[3,3,1,1],[4,2,1,2],[5,2,1,2],[0,4,1,2],[1,4,1,2],[2,4,1,2],[3,4,1,2],[4,4,1,2],[5,4,1,2]]};storeWall();showAll();sync();const r=vp.getBoundingClientRect(),w=walls[cur];V.z=Math.min(r.width,r.height,600)/Math.max(wW(w),wH(w))*.95;V.x=(r.width-wW(w)*V.z)/2;V.y=(r.height-wH(w)*V.z)/2;forceRen=true}"""); await pg.wait_for_timeout(500)
        hc = await ev("(()=>{const r=vp.getBoundingClientRect(),w=walls[cur];return {x:r.left+V.x-8,y:r.top+V.y-8,width:wW(w)*V.z+16,height:wH(w)*V.z+16}})()")
        await shot('half', hc)
        await ev("""()=>{S.cols=8;S.rows=3;S.half=[];S.lay={};S.gone=[[0,0],[1,0],[6,0],[7,0],[0,1],[7,1]];storeWall();showAll();sync();const r=vp.getBoundingClientRect(),w=walls[cur];V.z=Math.min(r.width,r.height,600)/Math.max(wW(w),wH(w))*.95;V.x=(r.width-wW(w)*V.z)/2;V.y=(r.height-wH(w)*V.z)/2;forceRen=true}"""); await pg.wait_for_timeout(500)
        hc = await ev("(()=>{const r=vp.getBoundingClientRect(),w=walls[cur];return {x:r.left+V.x-8,y:r.top+V.y-8,width:wW(w)*V.z+16,height:wH(w)*V.z+16}})()")
        await shot('gone', hc); await sect('Tile model', 'sec_half')
        await ev("()=>{S.preset='Unilumin UpadIV 2.6';applyPreset();S.half=[];S.lay={};S.gone=[];S.cols=6;S.rows=4;storeWall();showAll();sync();fit()}")
        assert not errs, errs
        # the desktop app's own top bar and Spout / Syphon options (stand-in for Electron on Windows and Mac; nothing is sent)
        for plat, name in (('win32', 'sec_tx'), ('darwin', 'sec_sy')):
            c2 = await b.new_context(viewport={'width': 1500, 'height': 900}, device_scale_factor=2, color_scheme='dark')
            q = await c2.new_page(); e2 = []; q.on('pageerror', lambda e: e2.append(str(e)))
            await q.add_init_script(f'window.__PLAT={json.dumps(plat)};' + DESK_MOCK)
            await q.goto(APP); await q.wait_for_timeout(900)
            if plat == 'win32':
                await q.locator('#bar').screenshot(path=str(SHOTS / 'toolbar.png'))
                await q.evaluate("()=>toggleShare()"); await q.wait_for_timeout(1300)
            loc = q.locator(f'xpath=//details[summary[contains(normalize-space(.), "{"Spout options" if plat == "win32" else "Syphon options"}")]]').first
            await loc.evaluate("d=>{for(let e=d;e;e=e.parentElement&&e.parentElement.closest('details'))e.open=true}")
            await loc.scroll_into_view_if_needed(); await q.wait_for_timeout(150)
            await loc.screenshot(path=str(SHOTS / f'{name}.png')); crop(name, 470)
            assert not e2, e2
            await c2.close()
        await b.close()
        return data

def img(name, cap='', w='100%'):
    b64 = base64.b64encode((SHOTS / f'{name}.png').read_bytes()).decode()
    return f'<figure style="width:{w}"><img src="data:image/png;base64,{b64}">' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'

def table(head, rows, cls=''):
    return f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'

def build_html(d):
    missing = [p for p in d['pats'] if p not in PATTERN_DESC] + [f for f in d['fits'] if f not in FIT_DESC] + [f for f in d['fills'] if f not in FILL_DESC] + [f for f in d['pfills'] if f not in PFILL_DESC]
    assert not missing, f'manual is missing descriptions for: {missing}'
    pats = table(['Pattern', 'What it shows'], [[f'<b>{E(p)}</b>', PATTERN_DESC[p]] for p in d['pats']])
    fits = table(['Image fit', 'What it does'], [[f'<b>{E(f)}</b>', FIT_DESC[f]] for f in d['fits']])
    fills = table(['Data wiring preference', 'How tiles are shared between ports'], [[f'<b>{E(f)}</b>', FILL_DESC[f]] for f in d['fills']])
    pfills = table(['Wiring preference', 'How tiles are shared between circuits'], [[f'<b>{E(f)}</b>', PFILL_DESC[f]] for f in d['pfills']])
    procs = table(['Processor', 'Ports', 'Pixels per port (spec)', 'Notes'],
                  [[f'<b>{E(x["name"])}</b>', x['ports'], (f'{x["px"]:,} at {x["hz"]} Hz, {x["bpc"]}-bit' if x['px'] else 'enter from your system spec'), E(x['note'])] for x in d['procs']], 'small')
    codecs = table(['Format', 'File', 'ffmpeg encoder', 'Best for'], [[f'<b>{E(c["name"])}</b>', '.' + c['ext'], c['enc'], E(c['note'])] for c in d['codecs']])
    res = ', '.join(f'{E(k)} ({v[0]} × {v[1]})' for k, v in d['res'])
    presets = table(['Preset', 'Tile (px)', 'Size (mm)', 'Pitch', 'Weight', 'Max W'],
                    [[E(k), f'{v[2]} × {v[3]}', f'{v[0]} × {v[1]}', f'{v[4]} mm', f'{v[5]} kg', v[6]] for k, v in d['presets']], 'small')
    wp = lambda kind: '<div class="wp">' + ''.join(f'<div><div class="ico">{x[kind]}</div><span>{E(x["c"])}<br>{E(x["d"].lower())}</span></div>' for x in d['wp']) + '</div>'
    csvcols = ', '.join(f'<code>{E(c)}</code>' for c in d['csv'].split(','))
    halftab = table(['Model', 'Half tile', 'Half'], [[E(x['full']), E(x['half']) + (f" ({x['h'][0]}×{x['h'][1]} mm, {x['h'][2]}×{x['h'][3]} px)" if x['h'] else ''), 'top / bottom' if x['split'] == 'h' else 'left / right'] for x in d['half']], 'small')
    tx_lic = ''.join(f'<div class="lic"><b>{E(n)}</b><br><span>{E(w)}</span><pre>{E(t)}</pre></div>' for n, w, t in TX_LICENSES)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>TileSmith {VERSION} User Manual</title><style>
@page{{size:Letter;margin:18mm 17mm 20mm}}
:root{{--ac:#0e7c86;--am:#c27c00;--ink:#16202a;--mu:#5b6b7a;--ln:#d7dee5}}
body{{font-family:Inter,'DejaVu Sans',sans-serif;color:var(--ink);font-size:10.2pt;line-height:1.5;margin:0}}
h1{{font-size:21pt;margin:0 0 6pt;letter-spacing:-.01em;break-after:avoid}} h2{{font-size:14pt;margin:18pt 0 6pt;color:var(--ac);break-after:avoid}} h3{{font-size:11pt;margin:12pt 0 4pt;break-after:avoid}}
section.chap{{break-before:auto;margin-top:16pt}} .toc{{break-before:page;break-after:page}} section.first{{break-before:page}} p{{margin:0 0 7pt}} ul,ol{{margin:0 0 8pt;padding-left:18pt}} li{{margin:0 0 3pt}}
figure{{margin:6pt 0 10pt;break-inside:avoid}} figure img{{width:auto;max-width:100%;max-height:118mm;border:1px solid var(--ln);border-radius:4px;display:block;margin:0 auto}} .side figure img,.cols figure img{{max-height:105mm}} figcaption{{font-size:8.6pt;color:var(--mu);margin-top:3pt}}
table{{width:100%;border-collapse:collapse;margin:4pt 0 10pt;font-size:9.2pt}} th{{text-align:left;background:#eef3f6;border-bottom:1.5px solid var(--ln);padding:4pt 6pt}} td{{border-bottom:1px solid var(--ln);padding:4pt 6pt;vertical-align:top}}
table.small{{font-size:8.4pt}} tr{{break-inside:avoid}} code{{font-family:'DejaVu Sans Mono',monospace;font-size:8.6pt;background:#f1f4f6;padding:0 3px;border-radius:3px}}
.note{{border-left:3px solid var(--am);background:#fff8ea;padding:6pt 9pt;margin:6pt 0 10pt;break-inside:avoid}} .key{{font-weight:600;color:var(--ac)}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:14pt;align-items:start}} .side{{display:grid;grid-template-columns:1fr 42%;gap:14pt;align-items:start}}
.wp{{display:grid;grid-template-columns:repeat(4,1fr);gap:6pt;margin:4pt 0 10pt;break-inside:avoid}} .wp>div{{border:1px solid var(--ln);border-radius:5px;padding:5pt;text-align:center;font-size:8pt;color:var(--mu)}} .ico{{color:var(--ink)}} .ico svg{{width:70px;height:53px}}
.cover{{height:236mm;display:flex;flex-direction:column;justify-content:center}} .cover .mark{{width:64px;height:64px;margin-bottom:18pt}} .cover h1{{font-size:34pt;margin:0}} .cover .sub{{font-size:15pt;color:var(--mu);margin:4pt 0 24pt}}
.lic{{margin:4pt 0 10pt;font-size:8.4pt;break-inside:avoid}} .lic span{{color:var(--mu)}} .lic pre{{white-space:pre-wrap;font-family:Inter,'DejaVu Sans',sans-serif;font-size:7.6pt;color:#3b4855;margin:3pt 0 0;line-height:1.35}}
.toc ol{{columns:2;column-gap:22pt;padding-left:16pt}} .toc li{{margin-bottom:4pt}}
</style></head><body>
<div class="cover"><svg class="mark" viewBox="0 0 10 10"><rect width="10" height="10" rx="2" fill="#0f1720"/><g fill="#22a0ac"><rect x="1.5" y="1.5" width="2.2" height="2.2"/><rect x="6.3" y="1.5" width="2.2" height="2.2"/><rect x="3.9" y="3.9" width="2.2" height="2.2"/><rect x="1.5" y="6.3" width="2.2" height="2.2"/></g><rect x="6.3" y="6.3" width="2.2" height="2.2" fill="#ffb300"/></svg>
<h1>TileSmith</h1><div class="sub">LED Wall Pixel Map &amp; Test Pattern Generator · User Manual</div>
<p><b>Version {VERSION}</b> · {TODAY}</p><p>Concept and development: Callum Davenport-Lambton · tilesmithapp@gmail.com</p>
<p style="color:var(--mu);margin-top:30pt;max-width:120mm">Pixel mapping, LED engineering, NDI®, Spout and Syphon output and an animated technician who builds the wall, tile by tile.</p><p style="color:var(--mu);font-size:8.5pt;margin-top:40pt">NDI® is a registered trademark of Vizrt NDI AB. <a href="https://ndi.video/">ndi.video</a></p></div>

<section class="chap toc"><h1>Contents</h1><ol>
<li>What TileSmith does</li><li>Installing and first launch</li><li>Quick start</li><li>The screen</li><li>Canvas</li><li>LED walls</li><li>Tile model</li><li>Test patterns</li><li>Tile borders and overlays</li><li>LED processor</li><li>Data wiring</li><li>Power and power wiring</li><li>Engineering panel</li><li>Technician and crew</li><li>Animation options</li><li>NDI®, Spout and Syphon output</li><li>Video export</li><li>Other exports</li><li>Saving your work</li><li>Keeping CPU use low</li><li>Mobile app (Android and iOS)</li><li>Troubleshooting</li></ol></section>

<section class="chap first"><h1>1. What TileSmith does</h1>
<p>TileSmith lays out LED walls on a master canvas, fills them with test patterns and pixel maps, works out processor ports, data paths and power, and sends the canvas live over <b>NDI®</b> to your media server or processor. An animated LED technician can build each wall tile by tile, which you can show live or record as a video.</p>
<ul><li>Several LED walls on one canvas, each with its own tile model, size, position and test pattern.</li>
<li>Processor-aware engineering: tiles per port and data paths (P# to R#), plus tiles per circuit and power runs on Socapex.</li>
<li>Live NDI® output, plus Spout (Windows) or Syphon (Mac) to other apps on the same computer (desktop app); HAP, MP4 and ProRes video export, PNG, CSV, spec sheet and Resolume Advanced Output XML.</li>
<li>Runs fully offline. Everything you set up is saved automatically.</li></ul>
<div class="note">The desktop app (Windows or Mac) is needed for NDI®, Spout and Syphon output and video export. The web version does everything else.</div>

<h1 style="margin-top:22pt">2. Installing and first launch</h1>
<p>Build instructions come with the source as <b>BUILD-WINDOWS.txt</b> and <b>BUILD-MAC.txt</b>. In short:</p>
<ol><li>On the build computer, install <b>Node.js</b> (LTS) and the free <b>NDI® SDK</b> (ndi.video/for-developers/ndi-sdk). The build copies the NDI® runtime and its license notices from the SDK into TileSmith, so computers that <i>run</i> TileSmith need nothing NDI® installed.</li>
<li>For video export, add ffmpeg: on Windows, the gyan.dev "full" build's <code>ffmpeg.exe</code> goes in the project's <code>bin</code> folder; on Mac, install it with Homebrew.</li>
<li>In the project folder run <code>npm run clean</code>, <code>npm install</code>, then <code>npm run dist</code> (Windows) or <code>npm run dist:mac</code> (Mac). Spout (Windows) and Syphon (Mac) come with the project in its <code>bin</code> folder and are packed in automatically; there is nothing extra to download or install.</li>
<li>Windows gives you <b>TileSmith-Portable.exe</b>, a single file you can copy anywhere. Mac gives you a .dmg containing a universal app.</li>
<li>The Android and iOS apps are built from the project's <code>mobile</code> folder with Android Studio or Xcode: see <b>BUILD-ANDROID.txt</b> and <b>BUILD-IOS.txt</b>, and chapter 21.</li></ol>
<p>The window title and the header show the version (<b>v{VERSION}</b>), so you can confirm you are running the latest build.</p></section>

<section class="chap"><h1>3. Quick start</h1><ol>
<li><span class="key">Canvas</span>: pick the canvas size your media server outputs, for example 1080p.</li>
<li><span class="key">Size of LED Wall</span> and <span class="key">Tile model</span>: set columns and rows and choose your tile preset.</li>
<li><span class="key">Test pattern</span>: choose a pattern, or click <b>Next pattern</b> in the top bar to step through them. <b>tileshade</b> is a classic pixel map.</li>
<li><span class="key">Engineering › LED processor</span>: choose your processor to see tiles per port, then pick a pattern under <span class="key">Data wiring</span>.</li>
<li><span class="key">Engineering › Power</span>: tick <b>Power distribution</b> to see tiles per circuit, then pick a pattern under <span class="key">Power wiring</span>.</li>
<li>Click <b>Start NDI®</b> in the top bar (desktop app) and pick <i>TileSmith-LED-Out</i> in your receiver. For an app on the same computer, click <b>Start Spout</b> (Windows) or <b>Start Syphon</b> (Mac) and pick <i>TileSmith</i>.</li>
<li>Click <b>Start build</b> to watch the technician build the wall, or <b>Instant skip</b> to show it finished.</li></ol>
{img('overview', 'The TileSmith window: settings on the left, actions along the top, the master canvas in the middle and the engineering panel on the right.')}</section>

<section class="chap"><h1>4. The screen</h1>
<p><b>Left panel</b> holds every setting, in collapsible sections, in this order: Canvas (with LED walls, Tile model, Size of LED Wall and Wall position submenus), Test pattern (with a Tile borders &amp; overlays submenu), Engineering (with LED processor and Power submenus; Data wiring is a submenu inside LED processor and Power wiring a submenu inside Power), Animation Options (with DVD screensaver, Build options, Video export and NDI® options submenus, plus Spout options on Windows or Syphon options on Mac; Technician is a submenu inside Build options), and Label printing options (below Animation Options; it appears only once data or power wiring is defined). Click a heading or submenu to open or close it. Data wiring appears once a processor is chosen; the power options and Power wiring appear once <b>Power distribution</b> is ticked. Sections marked with a wall name edit the selected wall. <b>Top bar</b> holds the actions. <b>Viewport</b> in the middle shows the master canvas exactly as it is sent over NDI®. <b>Engineering</b> on the right shows totals for the whole canvas and for each wall.</p>
{img('toolbar', 'Top bar of the Windows app. The Mac app shows Start Syphon in place of Start Spout; the web version has neither.')}
{table(['Button', 'What it does'], [
 ['ⓘ Info', 'Credits, contact, Ko-fi link, the NDI®, Spout and Syphon notices and <b>Reset saved settings</b>.'],
 ['Play / Pause', 'Pauses or resumes the build animation.'],
 ['Start build', 'Clears the walls and starts the technicians building from the first tile.'],
 ['Instant skip', 'Shows every wall fully built.'],
 ['Center canvas', 'Centres the canvas in the viewport without changing the zoom.'],
 ['Show entire canvas', 'Zooms so the whole canvas fits in the viewport.'],
 ['New Project', 'First button in the top bar. Asks first, then erases every wall, wiring, half tile, pattern and setting (including output, label and video options) and starts from a blank canvas. <b>Undo</b> brings it back.'],
 ['Undo ▾', 'Lists the last 20 changes, newest first. Click one to go back to just before it. <b>Ctrl+Z</b> (<b>Cmd+Z</b> on a Mac) undoes one step, <b>Ctrl+Y</b> or <b>Ctrl+Shift+Z</b> redoes it. Moving the view, playing the animation and exporting are not changes.'],
 ['Next pattern', 'Moves the selected wall to the next test pattern in the list, and back to the first after the last. <i>custom</i> is skipped until you upload an image.'],
 ['Start NDI®', 'Starts sending the canvas as an NDI® source (desktop app). While it runs the button is green and reads <b>Stop NDI®</b>; click it again to stop. Settings are in Animation Options › NDI® options.'],
 ['Start Spout / Start Syphon', '<b>Start Spout</b> on Windows, <b>Start Syphon</b> on Mac: shares the canvas with other apps on the same computer, straight from the graphics card. Green and <b>Stop …</b> while live. Shown only in a desktop app built with Spout or Syphon. Settings are in Animation Options › Spout options or Syphon options.'],
 ['Export PNG', 'Saves the canvas as a PNG image at full resolution.'],
 ['Export CSV', 'Saves a patching sheet with one row per tile.'],
 ['Spec sheet', 'Opens a printable spec sheet with every engineering figure.'],
 ['Resolume XML ▾', 'Drop-down: pick <b>One slice per LED wall</b> or <b>One slice per tile</b> to save an Advanced Output preset for Resolume Arena.'],
 ['Export video', 'Records the build to a video file (desktop app). Click again to stop and discard.']])}
<h3>Moving around the viewport</h3><ul><li>Next to the zoom level, the top bar shows how many frames per second the canvas is drawing, or <i>still</i> when nothing is moving.</li>
<li><b>Scroll wheel</b> zooms around the pointer. Zoom all the way out and the whole canvas, and any wall placed outside it, is centred in view, however small the window. <b>Drag empty space</b> pans. <b>Show entire canvas</b> brings the canvas back into view and <b>Center canvas</b> centres it at the current zoom.</li>
<li>In a small window the top bar stays on one row; scroll it sideways to reach the rest of the buttons.</li>
<li><b>Click a wall</b> to select it. <b>Drag a wall</b> to move it (see LED walls).</li></ul></section>

<section class="chap"><h1>5. Canvas</h1><div class="side"><div>
<p>The <b>Canvas</b> section also holds the <b>LED walls</b>, <b>Tile model</b>, <b>Size of LED Wall</b> and <b>Wall position</b> submenus described in the next chapters.</p>
<p>The master canvas is the full raster TileSmith outputs over NDI® and in exports. Type a <b>Width</b> and <b>Height</b>, or click a preset: {res}.</p>
<p><b>Fit canvas to walls</b> shrinks the canvas to the area your walls use, so no empty pixels are sent. This also lowers CPU use for NDI®.</p>
<p>The cyan outline in the viewport is the edge of the canvas, and each wall has an amber outline (solid on the selected wall when there are several). Anything outside the walls is sent as black.</p></div>{img('sec_canvas')}</div>

<h1 style="margin-top:18pt">6. LED walls</h1><div class="side"><div>
<p>The <b>LED walls</b> list shows each wall with its size, position, pattern and build start. Click one to select it. <b>Add wall</b> places a new wall beside the others, <b>Duplicate</b> copies the selected wall, <b>Remove</b> deletes it.</p>
<p><b>Wall name</b> appears in the list, the engineering panel, exports and on the tileshade pattern.</p>
<p><b>Tech starts at</b> picks the corner the technician starts from. <b>Tile placement</b> builds a row at a time (horizontal) or a column at a time (vertical).</p></div>{img('sec_walls')}</div>
<h3>Positioning walls</h3><p>Under <b>Wall position</b>, type <b>Offset X</b> and <b>Offset Y</b> in canvas pixels, or use the alignment buttons. In the viewport you can <b>drag a wall</b>: it snaps to the canvas edges and to other walls, keeping a <b>2 px gap</b> between walls. Hold <b>Alt</b> while dragging to place it freely. Pink guide lines show what it is snapping to.</p>
<div class="side"><div><h3>Size of LED Wall</h3><p>Set <b>Columns</b> and <b>Rows</b> of tiles (up to 64 each), or click a quick size such as 6×4 or 16×9. The wall's pixel size is columns × tile width by rows × tile height.</p></div>{img('sec_size')}</div>
<h3>Removing tiles</h3><div class="side"><div><p>For a wall that is not a rectangle, click <b>Remove tiles</b> in the Size of LED Wall submenu, then click tiles in the viewport to take them out. Click a removed tile to put it back, or press and drag to do the same to every tile you cross. <b>Restore all tiles</b> puts every tile back. While you are removing tiles, the viewport marks removed tiles with a red ✕ (this never appears in the output).</p>
<p>A removed tile is black in the output and left out everywhere else: the build animation skips it, and the engineering panel, spec sheet, CSV and Resolume per-tile slices leave it out. Tile IDs keep their grid numbers, so the remaining tiles keep their names. Data and power wiring skip removed tiles, and Snake and Linear join neighbouring ports or circuits that now fit on one. Removing tiles works with any model. On a wall with half tiles, Remove tiles takes out whole tiles, and clicking an empty space puts a tile back (a full tile if its whole cell is empty, otherwise a half tile).</p></div>{img('gone', 'A ROE Carbon CB5 wall with the top corners stepped in.')}</div></section>

<section class="chap"><h1>7. Tile model</h1>
<div class="side"><div><p>Presets are grouped by manufacturer. Pick a <b>Preset</b> to fill in the tile's pixels, size, pitch, depth, weight and maximum watts, or edit any field (the preset then shows <i>Custom</i>). <b>Density</b> and <b>Typical (40%)</b> power are worked out for you. These figures drive the engineering panel, port capacity and power circuits.</p>
<p>The ROE list covers every current ROE Visual series (Amber, Black Marble, Black Pearl, Black Quartz, Carbon, Carbon MkII, Carbon Full Spectrum, Coral, Denali, Diamond, Graphite, Jasper, Jet, Meru, Obsidian, Ruby, Sierra, Topaz, Vanish, Vanish ST, Vanish Air and Vanish Acoustics) and is grouped by series in the preset menu. The figures are the ones ROE prints on its product pages for one panel (size, pixels, pitch, weight and maximum power; ROE says they are for reference and actual values may vary), and each model that has a half panel has the half-tile controls. Corner pieces such as the Graphite right-angle panels are not listed. YES TECH figures come from the manufacturer's spec sheets, which give power per square metre: <b>Max W</b> is the higher figure times the cabinet area, rounded up. Check them against your exact model and brightness version before planning power.</p></div>{img('sec_tile')}</div>
{presets}
<h3>Half tiles</h3>
<p>Some models also come as a half tile, so a wall can step in or out, or shift, by half a tile. When the wall's model has a half version, the <b>Size of LED Wall</b> submenu shows the half-tile controls. <b>Convert bottom row to half tiles</b> and <b>Convert top row to half tiles</b> turn the whole row into half tiles in one click (the bottom row keeps its top half, the top row keeps its bottom half; the button then reads <i>Restore … row to full tiles</i> and puts full tiles back). For anything else click <b>Mark half tiles</b>; a red <b>STOP MARKING HALF TILES</b> button then appears at the top of the viewport (Esc does the same). Click in the viewport:</p>
<ul><li>Click one half of a full tile to keep just that half; the other half becomes an empty space.</li>
<li>Click an empty half space to put a half tile there.</li>
<li>Click the line between two half tiles to join them into one full tile. Halves above each other make an upright tile, which can also sit across two rows, half a tile lower than its neighbours. For ROE Carbon panels, two halves side by side join into a full panel on its side, to match ROE's frame options.</li>
<li>Click a half tile to take it out.</li></ul>
<p>Press and drag to repeat the first click's action across tiles. While marking, empty half spaces show a red ✕ in the viewport (never in the output). <b>Clear half tiles</b> goes back to a plain grid of full tiles. A wall with half tiles is only as big as its real tiles: patterns (circles, gradients, borders, text) scale to that area, the tile shading stays on the tile grid, and the wall's size, position, snapping and spec sheet use it. Tiles never move on the canvas when you convert or restore a row; the wall's position is the top-left corner of its real tiles. The button is hidden for models without a half version and for the half models themselves; pick a half model as the preset to build a whole wall from half tiles.</p>
<div class="side"><div>{halftab}<p>Each tile is drawn where it really sits: a half tile fills half a cell, a full tile on its side spans two columns. Tile IDs are numbered across the top row first and half tiles end in ½; the build animation carries each tile at its own size; and the engineering panel, spec sheet, CSV (column <code>Tile</code>) and Resolume per-tile slices use each tile's own size, pixels, weight and watts. The layout is kept if you switch to a model without a half version and comes back when you switch back.</p>
<p>Ports and circuits count every tile by its own pixels and watts and show their load in pixels or watts. On a wall with half tiles, Snake and Linear follow the pattern across the half-tile grid and start a new port or circuit wherever the next tile would overload it; the Data wiring preference and the power Wiring preference do not apply.</p></div>{img('sec_half')}</div>
{img('half', 'A ROE Carbon CB5 wall: the top row steps in by half a tile at each end, and the middle has a panel on its side over two half panels.', '70%')}</section>

<section class="chap"><h1>8. Test patterns</h1>
<p>Each wall has its own pattern. Choose it from <b>Test pattern</b>, or click <b>Next pattern</b> in the top bar to step the selected wall through the list in this order. <b>Tile-shade color</b> appears right under the pattern list when tileshade or tileshade-clean is chosen. <b>Tile position arrows</b> (an option for every pattern, on by default) labels every tile with its row counted up from the bottom (↑) and its column counted from the left (→), so ↑1 →1 is the bottom-left tile. The marker sits low on the left of each tile and moves up or down on any tile where it would cover the tile labels, the wall's name and size boxes or the footer. Only lit tiles show the pattern, so during a build it appears tile by tile.</p>{pats}
<h3>Scroll</h3><p><b>Scroll</b> moves any pattern across the wall ({', '.join(E(s) for s in d['scroll'])}); <b>Scroll speed</b> sets how fast. Tile borders and labels stay still while the pattern moves underneath.</p>
<h3>Image fit</h3><p>For image patterns (SMPTEbars, smptescroll, the built-in images and your own upload), <b>Image fit</b> decides how the image meets the wall:</p>{fits}
{img('fit_canvas', '<b>Original size on canvas</b>: two walls each show their own part of one 1920 × 1080 image, with nothing scaled.')}
<h3>Centre box on the branded patterns</h3><p>With a <b>branded test pattern</b> selected, <b>Center box</b> puts your <b>Text</b> (with a colour) or a <b>Logo</b> (upload PNG, SVG or JPG) in the black box. Text shrinks to fit; logos keep their shape, even when the pattern is stretched.</p>
<div class="cols">{img('branded', 'Branded test pattern with text in the centre box.')}{img('sec_pattern', 'Test pattern settings.')}</div>
<p><b>Tile-shade color</b> sets the colour used by the tileshade pattern.</p></section>

<section class="chap"><h1>9. Tile borders and overlays</h1><div class="side"><div>
<p>These settings are a submenu inside <b>Test pattern</b>.</p>
<p><b>Border color</b> and <b>Thickness</b> set the outline drawn around each tile, with small corner marks.</p>
<p><b>Tile IDs</b> labels each tile, for example <i>T07 [C1:R2]</i> (with the wall number when there are several walls). <b>Pixel address ranges</b> shows each tile's X and Y pixel range. <b>Millimeter marks</b> shows the tile's physical size.</p></div>{img('sec_borders')}</div></section>

<section class="chap"><h1>10. LED processor</h1>
<p>These settings are the <b>LED processor</b> submenu inside <b>Engineering</b>. Choose the processor (or sending card) that drives your walls. TileSmith then shows how many tiles each port can drive and enables data wiring. With <b>None</b>, the data and port options are hidden.</p>
<ul><li><b>Frame rate</b> and <b>Bit depth</b> adjust the pixels per port the way each manufacturer specifies (for example, NovaStar halves capacity at 10-bit; Brompton scales with frame rate and bit depth).</li>
<li><b>Pixels per port</b> and <b>Ports per processor / card</b> can be edited for your exact system; <b>Reset to spec</b> restores the published figures.</li>
<li><b>Ultra Low Latency</b> (Brompton) halves port capacity.</li>
<li><b>Return lines (R#) use their own ports</b> counts a return port for every primary port.</li>
<li><b>Show data paths</b> draws the wiring on the canvas.</li></ul>
{procs}
<div class="note">The engineering panel says how many processors (or sending cards) the canvas needs, using both the port count and the processor's maximum pixel load.</div>{img('sec_proc', '', '50%')}</section>

<section class="chap"><h1>11. Data wiring</h1>
<p><b>Data wiring</b> is a submenu inside <b>LED processor</b>. It appears once a processor is chosen and edits the selected wall. Pick a <b>Pattern</b>: <b>Snake</b> turns back at the end of each line; <b>Linear</b> starts every line from the same side; <b>Manual</b> lets you click or drag across the tiles in order. Then pick the start corner and direction: the same 8 choices as NovaLCT. In the picker, green is the first tile and red the last.</p>
<h3>Snake patterns</h3>{wp('snake')}<h3>Linear patterns</h3>{wp('linear')}
<h3>Data wiring preference</h3><p><b>Data wiring preference</b> decides how the wall is shared between ports; the pattern then runs inside each port's share. <b>Horizontal</b> and <b>Vertical</b> keep each port to bands of whole rows or whole columns, whichever direction the pattern runs.</p>{fills}
{img('wiring', 'Snake from the top-left, horizontal, Fewest ports: four ports, each snaking through its own block. P# marks where data enters, R# where it ends.')}
<p>Data paths are solid lines with arrows and P#/R# markers; power runs are dashed lines marked with a lightning bolt. When a wall shows both, data runs left of each tile's centre and power right of it, in white on a black casing.</p>
<h3>Manual wiring</h3><ol><li>Set Pattern to <b>Manual</b> and click <b>Wire tiles</b>.</li><li>Click tiles in the viewport in data order, or press on a tile and drag across the others. A fast drag fills in every tile it crosses; dragging back over the path takes tiles off again. Pressing on the last tile of the path carries on from there. A port stops accepting tiles when it is full.</li><li><b>New port</b> starts the next port, <b>Undo</b> removes the last tile, <b>Clear</b> starts again. Click <b>Stop wiring</b> when done.</li></ol>
<p>Below the controls TileSmith lists every port (for example <i>P1→R1: 15/17</i>), flags ports over capacity in red, and warns about unwired tiles.</p></section>

<section class="chap"><h1>12. Power and power wiring</h1><div class="side"><div>
<p>Power works like the LED processor. The settings are the <b>Power</b> submenu inside <b>Engineering</b>, and nothing about circuits is shown until you tick <b>Power distribution</b>. Power is planned on Socapex cables, 6 circuits per cable.</p>
<p><b>Circuit voltage</b> and <b>Breaker (A)</b> set the size of one circuit. With <b>Load circuits to 80%</b> on (the usual rule for continuous loads), only 80% of it is used. Tiles per circuit is the usable watts divided by the tile model's <b>Max watts</b>, rounded down. For example, 120 V × 20 A × 80% = 1,920 W, which powers 12 tiles of 150 W.</p>
<p><b>Show power runs on the canvas</b> draws each circuit as a dashed line in its own colour, with a lightning bolt and the circuit number at the first tile and a small square at the last. Circuits are numbered in order across the canvas: 1 to 6 are S1-1 to S1-6, 7 is S2-1, and so on.</p>
<p>When a wall shows both data and power paths, data runs to the left of each tile's centre and power to the right (and a little lower), so the two never sit on top of each other, and power is drawn white on a black casing so it stands out from the coloured data paths (a circuit over capacity stays red). With only one shown, it runs through the tile centres in its usual colours.</p></div>{img('sec_power')}</div>
<h3>Distribution cable type</h3><p>Pick the <b>Distribution cable</b> your power distribution unit uses. <b>Socapex</b> carries 6 circuits: TileSmith numbers them cable-circuit: <i>1-1</i> to <i>1-6</i> on the first cable, then <i>2-1</i> and so on. The labels carry no letter for the cable type. A <b>NEMA L14-30</b> carries 2 circuits (legs X and Y) and an <b>L21-30</b> carries 3 (legs X, Y and Z), numbered <i>1-X</i>, <i>1-Y</i>, <i>2-X</i> … (and <i>1-X</i>, <i>1-Y</i>, <i>1-Z</i> for an L21-30). TileSmith counts the cables needed and the spare circuits left over. Circuit numbers continue from one wall to the next. TileSmith does not assign phases: the distribution unit decides which phase each circuit or cable lands on, so the load is shown per cable.</p>
<h3>powerCON to Edison</h3><p>Choose <b>powerCON to Edison (1 circuit per cable)</b> when there is no power distribution unit and every circuit is its own powerCON cable with a standard Edison plug on the wall end, plugged straight into wall power. Choosing it sets the circuit to <b>120 V</b> and <b>15 A</b> (change them if your plugs are 20 A or your mains differ). Circuits are numbered <i>1</i>, <i>2</i>, <i>3</i> … with no cable-circuit pair, and the engineering panel shows <b>Edison plugs needed</b> and the <b>Peak load per plug</b>. To check the room, enter <b>Edison plugs per wall circuit</b> (how many plugs share one breaker in the wall; 0 turns the check off) and the <b>Wall circuit breaker (A)</b>. The panel then lists the wall circuits needed and the load on each, and says when one is over its usable amps (the 80% rule applies if it is ticked). Plugs are grouped in order: with 3 plugs per wall circuit, plugs 1 to 3 are wall circuit 1, plugs 4 to 6 are wall circuit 2, and so on. Plug your tiles in that order, or enter the groups as they really are in the room.</p>
<h3>Power wiring</h3><p><b>Power wiring</b> is a submenu inside <b>Power</b>. It appears once Power distribution is ticked and edits the selected wall. It works like data wiring: pick <b>Snake</b>, <b>Linear</b> or <b>Manual</b>, then the start corner and direction from the same 8 choices. <b>Wiring preference</b> decides how the wall is shared between circuits, with the same choices as the data wiring preference.</p>
{pfills}
<p><b>Power link limit</b> caps tiles per circuit at the most tiles your tile model allows on one power daisy chain (see the manufacturer's spec), even when the breaker could take more. 0 means no limit.</p>
{img('power', 'Socapex power runs on a 10 × 5 wall of 150 W tiles at 120 V 20 A. Each circuit powers up to 12 tiles.', '80%')}
<div class="side"><div><h3>Manual power wiring</h3><ol><li>Set Pattern to <b>Manual</b> and click <b>Wire tiles</b>.</li><li>Click tiles in the viewport in power-link order, or press on a tile and drag across the others, the same way as data wiring. A circuit stops accepting tiles when it is full.</li><li><b>New circuit</b> starts the next circuit, <b>Undo</b> removes the last tile, <b>Clear</b> starts again. Click <b>Stop wiring</b> when done.</li></ol>
<p>Below the controls TileSmith lists every circuit (for example <i>1-2: 12/12</i>), flags circuits over capacity in red and counts tiles without power.</p></div>{img('sec_pwiring')}</div></section>

<section class="chap"><h1>13. Engineering panel</h1><div class="side"><div>
<p>The right-hand panel has an <b>Entire canvas</b> section and one section per wall. Click a heading to fold it away.</p>
<ul><li>Canvas size, aspect, pixels, tile count, LED pixels, area (m² and sq ft), weight (kg and lbs).</li>
<li>Peak and typical power, and the peak current at the circuit voltage once Power distribution is ticked.</li>
<li>With Power distribution ticked: circuit size, tiles per circuit, circuits used, the fewest circuits possible, cables and spare circuits, peak load per cable, circuits over capacity and tiles without power.</li>
<li>With a processor: pixels per port, tiles per port, ports used (with returns), processors or cards needed, and any ports over capacity.</li></ul>
<p><b>Spec sheet</b> in the top bar opens the same figures as a printable page.</p></div>{img('engineering')}</div></section>

<section class="chap"><h1>14. Technician and crew</h1><div class="side"><div>
<p>These settings are the <b>Technician</b> submenu inside <b>Animation Options › Build options</b>.</p>
<p>Choose the <b>Hard hat</b> and <b>Vest</b> colours, and the <b>Vest logo text</b> or an uploaded logo.</p>
<p>Turn on <b>Crew details & name tags</b> to name each technician and set skin and hair colour. Add a <b>Face photo</b> to put a real face on a technician. <b>Add crew member</b> grows the crew; <b>Reset to defaults</b> restores it.</p>
<p>With several walls, technicians rotate so the same person is never on every wall at once, and each wall builds at a slightly different rate.</p></div>{img('sec_tech')}</div></section>

<section class="chap"><h1>15. Animation options</h1>
<p><b>Start build</b> clears the walls; technicians walk on, carry each tile to its place, latch it and walk off. Only built tiles light up, in NDI® and in exports. Use <b>Play / Pause</b> to pause and <b>Instant skip</b> to finish.</p>
<p>Under <b>Animation Options › Build options</b>: <b>Loop build continuously</b> restarts the build after <b>Pause before restart</b> seconds; <b>Speed</b> runs the build from 0.25× to 5×.</p>
<div class="cols">{img('build', 'A wall partway through its build.')}{img('sec_anim', 'Build options, with the Technician submenu.')}</div>
<h3>DVD screensaver</h3><p>In the <b>DVD screensaver</b> submenu, tick <b>Bounce a logo around the screen</b> to bounce a logo like the classic DVD screensaver. It shows on every lit tile and is included in NDI® and video export.</p>
<ul><li><b>Logo</b>: {', '.join(E(x) for x in d['dvdSrc'])}. Upload a PNG with a transparent background for the best result.</li>
<li><b>Bounce inside</b>: <b>Each LED wall</b> gives every wall its own logo; <b>Whole canvas</b> bounces one logo across the canvas, visible wherever it crosses a wall.</li>
<li><b>Logo size</b> (percent of the wall's shorter side) and <b>Bounce speed</b>.</li>
<li><b>Corner hit chance</b>: how often the logo lands exactly in a corner. At 100% about 45 of every 100 bounces are corners, at 50% about 22, and at 0% the logo is steered so it never touches a corner. The value shows the expected share of bounces, and the line underneath counts real corner hits as it runs.</li>
<li><b>Change color on each bounce</b> recolours the logo at every bounce. Turn it off to keep your logo's own colours.</li></ul>
<h3>Perfect loop video</h3><p>Tick <b>Perfect loop</b> to make the bounce repeat exactly: after <b>Loop length</b> seconds the logo is back where it started, moving the same way and in the same colour, so the video can play on repeat with no visible seam. <b>Include corner hits</b> gives two exact corner hits per loop; untick it and the logo never touches a corner. The corner hit chance slider is not used in this mode. TileSmith picks the nearest speed and angle that close the loop, so the speed can differ a little from Bounce speed; the line underneath shows the real speed, bounces and corner hits per loop. A short loop on a very wide wall can force a fast logo, so use a longer loop to slow it down.</p>
<p><b>Export loop video</b> (desktop app) renders exactly one loop, frame by frame at 60 fps, in the Format chosen under Video export, and saves it next to your other videos as <code>tilesmith-dvd-loop-…</code>. The walls are shown fully built, and moving patterns and Scroll are held still so the loop is seamless. Click the button again to cancel.</p>
{img('dvd', 'DVD screensaver over SMPTE bars.', '75%')}</section>

<section class="chap"><h1>16. NDI®, Spout and Syphon output</h1><h2>NDI®</h2><div class="side"><div>
<p>In the desktop app, click <b>Start NDI®</b> in the top bar (or in the <b>NDI® options</b> submenu inside <b>Animation Options</b>). The button turns green and reads <b>Stop NDI®</b> while NDI® is live; click it again to stop. The canvas is sent as an NDI® source named after <b>NDI® source name</b> (default <i>TileSmith-LED-Out</i>). Pick it in Resolume, vMix, OBS, NDI® Studio Monitor or an NDI® decoder. If NDI® cannot start, the reason appears in a message at the bottom of the window.</p>
<ul><li><b>NDI® source name</b>: change it before you start; a new name applies the next time NDI® starts.</li>
<li><b>Frame rate</b>: {', '.join(d['fps'])}. Lower rates use less CPU. Applies right away.</li>
<li><b>Save CPU while the picture is still</b>: when nothing moves, sends about 4 frames a second instead of the full rate. Most receivers hold the last frame; leave it off if yours flags a low frame rate.</li>
<li>The status line in NDI® options shows the source name, the actual frames per second, the resolution and the time each frame takes: <b>render</b> (building the frame), <b>read</b> (reading the canvas back, including drawing its pixels) and <b>send</b> (NDI® compressing and sending it). If the frame rate drops, these show which part is slow.</li></ul>
<p>NDI® keeps running at full speed when the window is minimised or behind other windows, and the computer will not nap the app while NDI® output or a recording runs. The NDI® runtime is built into TileSmith, so nothing needs installing: the status line says <i>built-in NDI® runtime</i>. A build made without the NDI® SDK falls back to an NDI® Runtime or NDI® Tools installed on the computer and says <i>installed NDI® Runtime</i>. If other computers cannot see the source, allow TileSmith through the firewall (Windows: Private networks; Mac: allow Local Network the first time you start NDI®).</p></div>{img('sec_ndi')}</div>

<h2>Spout (Windows) and Syphon (Mac)</h2><div class="side"><div>
<p>Spout and Syphon share the master canvas with other apps on the <b>same computer</b> through the graphics card: no network, no compression and very little CPU. Spout exists only on Windows and Syphon only on Mac, so the Windows app has <b>Start Spout</b> and <b>Spout options</b>, and the Mac app has <b>Start Syphon</b> and <b>Syphon options</b>. Use NDI® to reach other computers; NDI®, Spout or Syphon and video export can all run at the same time.</p>
<p>Click <b>Start Spout</b> or <b>Start Syphon</b> in the top bar (or in its options submenu inside <b>Animation Options</b>). The button turns green and reads <b>Stop Spout</b> or <b>Stop Syphon</b> while it is live; click it again to stop. Then pick <i>TileSmith</i> in the receiving app.</p>
<ul><li><b>Spout sender name</b> / <b>Syphon server name</b> (default <i>TileSmith</i>): change it before you start; a new name applies the next time output starts. If another Spout sender already uses the name, Spout adds _1, _2 and so on; the status line shows the real name.</li>
<li><b>Frame rate when NDI® is off</b>: {', '.join(d['shfps'])}. Applies right away. While NDI® runs, Spout and Syphon send at the NDI® frame rate, so every output shows the same frames.</li>
<li><b>Save CPU while the picture is still</b> (on by default): a still picture is sent about 4 times a second instead of at the full rate. Spout and Syphon receivers keep showing the last frame, so it is safe to leave on.</li>
<li><b>Graphics card</b> (Spout only): Spout passes the picture through the graphics card, so the receiving app must use the <b>same card</b> as TileSmith's sender. <b>Automatic</b> (the default) uses the high-performance card, which is where Resolume and most media servers run. If the receiver lists TileSmith but shows black, pick the card the receiver runs on; changing it while Spout runs restarts the sender on that card.</li>
<li>The status line shows the name, the frames sent each second, the resolution, the time each frame takes to send and, for Spout, the graphics card in use. Syphon says <i>no app receiving yet</i> until an app connects; TileSmith only sends Syphon frames while at least one app is receiving. If the canvas size changes, the output follows it.</li></ul>
<p>The button and the options appear in a desktop app built with Spout or Syphon. Both come with the project (<code>bin\\spout</code> and <code>bin/mac/syphon</code>) and are built in automatically; a copy built without them hides the button and says so in the options. The web version shows one combined Spout / Syphon options submenu for reference and never has the button. Spout needs nothing installed (no Visual C++ runtime).</p></div>{img('sec_tx', 'Spout options in the Windows app while Spout is running.')}</div>
{table(['Receiving app', 'Windows (Spout)', 'Mac (Syphon)'], [
 ['Resolume Arena / Avenue', 'Sources › Spout › TileSmith', 'Sources › Syphon › TileSmith'],
 ['TouchDesigner', 'Syphon Spout In TOP', 'Syphon Spout In TOP'],
 ['OBS Studio', 'free Spout2 plugin, then a <i>Spout2 Capture</i> source', '<i>Syphon Client</i> source'],
 ['MadMapper, Millumin, VDMX', 'MadMapper: Spout input', 'Syphon input; some list the app as <i>TileSmith Helper (Renderer)</i>, which is TileSmith']])}
<div class="side"><div><div class="note">On a laptop with two graphics chips (for example Intel and NVIDIA), the receiver must be on the same chip as TileSmith's Spout sender, or it shows black. Leave <b>Graphics card</b> on <i>Automatic</i> (the fast chip) and make sure the receiver uses the fast chip too (Windows: Settings › System › Display › Graphics, <i>High performance</i>), or pick the receiver's chip in the list. Spout needs DirectX 11; if it cannot start, update the graphics driver. Spout keeps a log at <code>%APPDATA%\\TileSmith\\spout-log.txt</code>.</div></div>{img('sec_sy', 'Syphon options in the Mac app.')}</div>
<h3>NDI® licensing and trademarks</h3><p>NDI® is a registered trademark of Vizrt NDI AB. Learn more about NDI® at <a href="https://ndi.video/">https://ndi.video/</a>; the full NDI® Tools (Studio Monitor, Webcam, Screen Capture and more) are at <a href="https://ndi.video/tools/">https://ndi.video/tools/</a>.</p>
<p>The desktop app includes the NDI® runtime library from the NDI® SDK (Processing.NDI.Lib.x64.dll on Windows, libndi.dylib on Mac), © Vizrt NDI AB, distributed under the NDI® SDK License Agreement (<a href="https://ndi.link/ndisdk_license">ndi.link/ndisdk_license</a>). The runtime's third-party license notices ship with TileSmith; open them with <b>ⓘ Info › View NDI® license notices</b>. NDI® Tools are not included with TileSmith.</p>
<h3>TileSmith licence and copyright</h3><p>Copyright © 2026 Callum Davenport-Lambton. The TileSmith program is free software under the <b>GNU General Public License v3 or later</b> (file <code>LICENSE</code>): you may use, study, change and share it, provided you keep the copyright notice and share your source under the same licence. It comes without any warranty. The <b>animated technician</b>, meaning his character design, artwork, animations, the TileSmith name and the logo, is <b>not</b> under the GPL: all rights are reserved by the author (file <code>COPYRIGHT-AND-ARTWORK.txt</code>). The customisation options in the program (hat, vest, logo text, crew names) may be used freely. The NDI® runtime, Spout, Syphon and ffmpeg keep their own licences, and TileSmith has the author's permission to load the NDI® runtime.</p><h3>Spout and Syphon licences</h3><p>Spout output uses SpoutDX from the Spout SDK by Lynn Jarvis (<a href="https://spout.zeal.co/">spout.zeal.co</a>). Syphon output uses the Syphon framework by Tom Butterworth and Anton Marini (<a href="https://syphon.github.io/">syphon.github.io</a>) and node-syphon by Benoît Lahoz. Their licence texts ship inside TileSmith (open them with <b>ⓘ Info › View Spout / Syphon licences</b>) and are repeated here.</p>
{tx_lic}</section>
<section class="chap"><h1>17. Video export</h1>
<p>These settings are the <b>Video export</b> submenu inside <b>Animation Options</b>.</p>
<p><b>Export video</b> (desktop app) records a 60 fps video: the <b>Blank intro</b> (seconds of empty canvas), the whole live build, then the <b>Final hold</b> on the finished wall. The length follows the tile count and Speed; with several walls the slowest wall sets it. The estimate is shown under the settings. Files go to <code>Videos\\TileSmith</code> (Windows) or <code>Movies/TileSmith</code> (Mac) and the folder opens when done. Click the button again while recording to cancel.</p>
{codecs}
<p>For HAP, <b>HAP type</b> picks <code>hap</code>, <code>hap_alpha</code> or <code>hap_q</code> (higher quality). All formats are tagged BT.709 so colours match the canvas. Video export needs ffmpeg with the matching encoder (see Installing).</p>{img('sec_video', '', '50%')}</section>

<section class="chap"><h1>18. Other exports</h1>
<ul><li><b>Export PNG</b>: the full master canvas as an image.</li>
<li><b>Export CSV</b>: one row per tile with these columns: {csvcols}. Tile says full, half (with its side) or full on its side; removed tiles have no row. Port and PortPos come from the data wiring; Circuit, CircuitPos and PowerCable from the power wiring.</li>
<li><b>Spec sheet</b>: printable engineering summary for the canvas and each wall. In the mobile app it is saved as an HTML file; open it in a browser to print it or save it as a PDF.</li>
<li><b>Print labels</b>: cable labels for both ends of every data and power cable; see <b>Cable labels</b> below.</li>
<li><b>Resolume XML</b>: an Advanced Output preset whose composition matches the canvas, with one slice per wall or per tile (pick one from the <b>Resolume XML ▾</b> drop-down). On the desktop app it saves straight into <code>Documents/Resolume Arena/Presets/Advanced Output</code> when that folder exists. In Arena, open Output › Advanced Output, choose the preset, then assign the screen to your real output.</li></ul>

<h2>Cable labels</h2>
<p>When data wiring or power wiring is defined, a <b>Label printing options</b> section appears below Animation Options (it stays hidden until at least one data port or power circuit exists). It prints a label for <b>both ends of every cable</b>, so each cable can be found at the processor or distribution box and at the tile, and the two ends of one cable can be matched. Each label is a <b>wrap-around strip</b>: you wrap it around the cable and it sticks to itself, so the text is printed on <b>both sides</b> and can be read whichever way the cable is turned.</p>
<ul><li><b>Data cables</b>: the primary cable of each port is labelled <b>P1, P2 …</b> on a <b>completely green</b> label; when <b>Return</b> (backup) cables are on in LED processor, each port also gets an <b>R1, R2 …</b> cable on a <b>completely red</b> label. The <i>processor end</i> label names the processor port and the first (or, for R, the last) tile it connects to; the <i>tile end</i> label names the tile input (<b>DATA IN</b> or <b>DATA OUT (return)</b>) and where the cable comes from. Tile numbers are the T01, T02 … numbers on the canvas, with column and row.</li>
<li><b>Power cables</b>: with <b>Cable and circuit labels</b> (the default) each Socapex, L14-30 or L21-30 cable gets a label pair (for example <b>2</b>: cable 2 of 4, circuits 1-6 used, walls and load; the <i>distro end</i> and the <i>fan-out end</i> or <i>wall end</i>), plus a pair for every circuit (<b>2-3</b>: cable 2 of 4, circuit 3 of 6, voltage, breaker, tile count and load; or <b>2-X</b>: leg X). With <b>powerCON to Edison</b> there is only one label pair per circuit, numbered <b>1</b>, <b>2</b>, <b>3</b> …: the <i>Edison plug end</i> (with its wall circuit when you entered one) and the <i>powerCON end</i> on the first tile's <b>POWER IN</b>; the Power labels choice is hidden. The <i>source end</i> label goes on the distribution end and the <i>tile end</i> label on the first tile's <b>POWER IN</b>. <b>Circuit labels only</b> and <b>Cable labels only</b> print one kind. There is no phase on the labels; the flag is the wall's Tile-shade colour and carries the wall name.</li>
<li><b>Wall mark</b>: when the raster has more than one LED wall, a block in that wall's <b>Tile-shade color</b> (the colour set under Test pattern) sits on the label, with the wall name, so cables of different walls are told apart at a glance.</li>
<li>Every label says <b>1/2</b> or <b>2/2</b>, DATA or POWER, and the cable name in very large type.</li></ul>
<p><b>Options</b>: <b>Cables to label</b> (data and power, data only or power only; shown only when both exist); <b>Label sheet</b> (Avery 5160, 30 per US Letter sheet; Avery 5163, 10 per US Letter sheet, which suits wrap-around labels best; Avery L7160, 21 per A4 sheet; a 100 × 30 mm wrap-around strip roll; a 62 × 29 mm label roll; or a custom roll size in mm, one label per page); <b>Wrap layout</b>: <i>Two identical panels</i> (the same text on both halves, with the colour flags at the outer ends, so it reads on either face), <i>Flag fold-over</i> (the second half is upside down, for a label folded in half over the cable like a flag, so both faces read upright), or <i>Text in the middle, colour on the ends</i> (the name and text in the centre and only the big colour flags on the two end tails); <b>Colour flag style</b>: <i>Big end blocks</i> (full-height coloured blocks), <i>Top and bottom bars</i> (a bar along the top for primary or return and one along the bottom for the wall) or <i>Big corner squares</i> (large squares with a letter in the corners); <b>Wall mark</b>: <i>Wall-shade block + name</i> (only when there is more than one wall), <i>Always show wall mark</i>, or <i>Wall tint + block</i> (also tints the whole label background with a light version of the wall's colour); <b>Colour flags</b> (turn all flags and wall marks off for black-and-white printing); <b>Copies of each end</b> (1 to 4); <b>Start at label no.</b> (skips labels already used on a part-used sheet); <b>Also label the tile-to-tile links</b> (adds a label pair for every jumper between neighbouring tiles, such as P1-4 or S1-2-7); <b>Keep the two ends of a cable in one row</b> (sheets only: a cable's pair never splits across rows, so on a 3-across sheet the third cell of a row may stay empty).</p>
<p>Click <b>Print labels</b>. In the desktop app a preview page opens and the print window appears; choose your printer, set the scale to <b>100%</b> (turn off <i>fit to page</i>) and load the label sheet. In the mobile app <b>Save label sheet</b> saves the sheet as a web page through the share sheet; open it in a browser and print it at 100%. If the browser blocks pop-up windows, the labels are shown in a preview inside the page instead. The line under the options shows how many cables, labels and pages will print. Wrap the label around the cable so the two ends overlap and stick together; allow the strip to be at least as long as the cable's circumference plus a small overlap.</p>

<h1 style="margin-top:20pt">19. Saving your work</h1>
<p>Everything (canvas, walls, tile models, patterns, uploads, wiring, crew, options) is saved automatically and restored next time you open TileSmith. The desktop app keeps it in <code>%APPDATA%\\TileSmith\\state.json</code> (Windows) or <code>~/Library/Application Support/TileSmith/state.json</code> (Mac). To start fresh, open <b>ⓘ Info</b> and click <b>Reset saved settings</b>.</p>

<h1 style="margin-top:20pt">20. Keeping CPU use low</h1><ul>
<li>Use <b>Fit canvas to walls</b> so NDI® does not encode empty canvas.</li>
<li>Pick the lowest NDI® <b>Frame rate</b> your show needs; 30 needs roughly half the work of 60.</li>
<li>Tick <b>Save CPU while the picture is still</b> if your receivers are happy holding the last frame.</li>
<li>For an app on the same computer, Spout (Windows) or Syphon (Mac) costs far less CPU than NDI®, because the picture is not compressed. NDI®, Spout, Syphon and video export share one read of the canvas per frame, so running them together adds little.</li>
<li>Animated patterns (sweep), Scroll, the build and the DVD screensaver redraw every frame. cycle redraws only when its colour changes and tileshade-cycle only while its colours slide; still pictures are redrawn only a few times a second.</li></ul>

<h1 style="margin-top:20pt">21. Mobile app (Android and iOS)</h1>
<p>The Android and iOS apps run the same TileSmith page as the desktop app, so canvas, walls, tile models, patterns, engineering, wiring, power and the build animation all work the same way, and everything is saved automatically on the device. They are built from the <code>mobile</code> folder (see <b>BUILD-ANDROID.txt</b> and <b>BUILD-IOS.txt</b>); a Kotlin version of the Android app for Google AI Studio is in the <code>android-aistudio</code> folder. Tablets give the most room; on a phone the panels stack under each other. The mobile app has its own manual, <b>TileSmith-Mobile-Manual.pdf</b>.</p>
<ul><li><b>Saving files</b>: Export PNG, Export CSV, Spec sheet and Resolume XML open the share sheet, where you pick where the file goes: Files, Google Drive, iCloud, AirDrop, Quick Share, e-mail and so on. Closing the sheet cancels the save (TileSmith says <i>Not saved</i>).</li>
<li><b>Spec sheet</b> is saved as an HTML file; open it in a browser to print it or save it as a PDF.</li>
<li><b>Export video</b> records an H.264 MP4 with the device's own encoder, in real time: the Blank intro, the live build and the Final hold, the same as on the desktop. The screen stays on while it records; keep TileSmith open until it says <i>Saved</i>, then pick where the video goes ("Save Video" puts it in Photos on iPhone and iPad). HAP, ProRes and the DVD screensaver's <b>Export loop video</b> are desktop only.</li>
<li><b>NDI®, Spout and Syphon</b> are not in the mobile app yet, so their buttons and submenus are hidden, along with their notices in ⓘ Info.</li>
<li><b>Touch</b>: two fingers pinch to zoom and drag to pan the viewport. One finger drags a wall, wires tiles, marks half tiles and removes tiles, just like the mouse. Links (Ko-fi, ndi.video …) open in the system browser.</li></ul></section>

<section class="chap"><h1>22. Troubleshooting</h1>{table(['Problem', 'What to do'], [
 ['"NDI® runtime not found"', 'TileSmith was built without the NDI® SDK. Install the NDI® SDK on the build computer and rebuild, or install the NDI® Runtime (ndi.link/NDIRedistV6, or NDIRedistV6Apple on Mac) or NDI® Tools on this computer, then open TileSmith again.'],
 ['Receivers cannot see the NDI® source', 'Allow TileSmith through the firewall on private networks (Windows) or allow Local Network access (Mac). Make sure both computers are on the same network.'],
 ['"No ffmpeg with the … encoder found"', 'Windows: put the gyan.dev "full" ffmpeg.exe in the bin folder and rebuild. Mac: install ffmpeg with Homebrew (see BUILD-MAC.txt).'],
 ['The app looks like an older version', 'Check the version in the window title. Rebuild with npm run clean, npm install, npm run dist, and run the new TileSmith-Portable.exe.'],
 ['A wall will not move where I drag it', 'Walls snap to edges and each other. Hold Alt while dragging to place freely, or type the offset.'],
 ['Data wiring shows ports over capacity', 'Check the processor, frame rate and bit depth, or use Reset to spec. In Manual wiring, start a New port.'],
 ['Power options are missing', 'Tick Power distribution under Engineering › Power. While it is off, the power options and Power wiring are hidden.'],
 ['"One tile draws more than a circuit can supply"', 'Check the Breaker (A) and Circuit voltage, and the tile model\'s Max watts.'],
 ['NDI® frame rate is low', 'Read the timings in the NDI® status line. A large <b>read</b> or <b>send</b> time means the canvas is big: use Fit canvas to walls or a lower frame rate. With Save CPU on, a still picture is sent about 4 times a second on purpose. Plug a laptop into power and use a high-performance power mode.'],
 ['No Start Spout / Start Syphon button', 'That copy was built without Spout or Syphon (the options submenu says so). Rebuild from a fresh copy of the project: bin\\spout (Windows) and bin/mac/syphon (Mac) come in the zip, and the build prints [ok] Spout (or Syphon) output will be built into TileSmith. The web version never has the button.'],
 ['The receiver lists TileSmith (Spout) but shows black', 'The receiver is on a different graphics card from the TileSmith sender (common on laptops with two graphics chips). Spout options › Graphics card: pick the card the receiver runs on (the status line shows the card TileSmith uses), or leave it on Automatic and set the receiver to High performance in Windows Settings › System › Display › Graphics.'],
 ['"Spout could not send frames" or "could not start DirectX 11"', 'Pick another card under Spout options › Graphics card and update the graphics driver. Spout needs DirectX 11; it does not work over Remote Desktop or in most virtual machines. Details are in %APPDATA%\\TileSmith\\spout-log.txt.'],
 ['"Syphon failed to load" or macOS says syphon.node or Syphon cannot be opened', 'The files were blocked by the download quarantine. Run xattr -cr /Applications/TileSmith.app in Terminal and open TileSmith again (the build clears it automatically).'],
 ['A receiver does not list TileSmith', 'Spout and Syphon only reach apps on the same computer. Start it in TileSmith first, check the name in the options, and refresh the receiver\'s source list. Two senders cannot share a name.'],
 ['Mobile: Export video says the device cannot record MP4', 'Update the system: on Android update "Android System WebView" and Chrome from Google Play (Android 7 cannot get a new enough version); on iPhone and iPad update iOS / iPadOS.'],
 ['Mobile: a save does nothing', 'Pick an app in the share sheet (Files, Drive …). Closing the sheet cancels the save.'],
 ['Image looks soft or stretched', 'Change Image fit. Use Original size on canvas or on wall for pixel-exact images.'],
 ['Settings are wrong after testing', 'ⓘ Info › Reset saved settings.']])}
<p>Build problems (npm warnings, vulnerabilities, PowerShell script errors, signing) are covered in the TROUBLESHOOTING sections of BUILD-WINDOWS.txt, BUILD-MAC.txt, BUILD-ANDROID.txt and BUILD-IOS.txt.</p></section>
</body></html>"""

async def main():
    data = await shots_and_data()
    page_html = build_html(data)
    (SHOTS.parent / 'manual.html').write_text(page_html, encoding='utf-8')
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.set_content(page_html, wait_until='load'); await pg.wait_for_timeout(500)
        foot = f'<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#7a8896;width:100%;padding:0 17mm;display:flex;justify-content:space-between"><span>TileSmith v{VERSION} · User Manual</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
        await pg.pdf(path=str(OUT), format='Letter', print_background=True, display_header_footer=True, header_template='<div></div>', footer_template=foot,
                     margin={'top': '18mm', 'bottom': '20mm', 'left': '17mm', 'right': '17mm'})
        await b.close()
    print('wrote', OUT, OUT.stat().st_size // 1024, 'KB')

asyncio.run(main())
