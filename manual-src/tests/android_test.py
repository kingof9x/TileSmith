"""Tests webview-bridge.js with a mocked Kotlin TileSmithAndroid interface (synchronous calls returning "" or an error,
share result delivered later through window.__tsmDone like the Kotlin code does)."""
import asyncio, json, base64, pathlib, subprocess, sys
from playwright.async_api import async_playwright
SP = pathlib.Path(__file__).parent
OUT = SP / 'aout'
subprocess.run(['node', '/home/claude/tilesmith-desktop/android-aistudio/prepare-assets.js', str(OUT)], check=True)
APP = (OUT / 'tilesmith' / 'index.html').as_uri()
MOCK = r"""
(()=>{const calls=window.__calls=[],files=window.__files={};
window.TileSmithAndroid={
 writeChunk(name,b64,append){if(typeof name!='string'||typeof b64!='string'||typeof append!='boolean')return 'bad args';
   if(window.__failWrite)return 'disk full';if(!append||!files[name])files[name]=[];files[name].push(b64);calls.push(['write',name,b64.length,append]);return ''},
 deleteFile(name){delete files[name];calls.push(['delete',name]);return ''},
 shareFile(name,mime,id){calls.push(['share',name,mime,id]);if(!files[name])return 'file not found: '+name;
   setTimeout(()=>window.__tsmDone(id,!window.__cancel),30);return ''},
 openUrl(u){calls.push(['url',u]);return ''},
 keepAwake(on){calls.push(['awake',on]);return ''}};
})();
"""
def size(files, path): return sum(len(base64.b64decode(x)) for x in files.get(path, []))
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, has_touch=True)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.add_init_script(MOCK)
        await pg.goto(APP); await pg.wait_for_timeout(800)
        vis = await pg.evaluate("""()=>({cls:document.documentElement.className,MOBILE,plat:TSM.platform,
            ndi:getComputedStyle(document.querySelector('#bar [data-a=ndi]')).display,sh:getComputedStyle(document.querySelector('#shBtn')).display})""")
        print('VIS', vis); ok &= vis['MOBILE'] and 'mobile-android' in vis['cls'] and vis['ndi'] == 'none' and vis['sh'] == 'none'
        await pg.click('#bar [data-a=png]'); await pg.wait_for_timeout(1200)
        await pg.click('#bar [data-a=pdf]'); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#bar [data-a=rxmlm]').scrollIntoView({inline:'center'})"); await pg.wait_for_timeout(300); await pg.click('#bar [data-a=rxmlm]'); await pg.click('#rxmlm [data-v="One slice per tile"]'); await pg.wait_for_timeout(700)
        r = await pg.evaluate("()=>({calls:__calls.filter(c=>c[0]=='share'),toast:document.querySelector('#toast').textContent})")
        print('SHARES', r)
        files = await pg.evaluate('__files')
        png = base64.b64decode(''.join(files['tilesmith-canvas.png']))
        pk = [k for k in files if k.endswith('.pdf')]; pdfb = base64.b64decode(''.join(files[pk[0]])) if pk else b''
        mimes = {c[1]: c[2] for c in r['calls']}
        print('png', len(png), png[:4], 'mimes', mimes)
        ok &= png.startswith(b'\x89PNG') and pdfb.startswith(b'%PDF-1.4') and mimes.get(pk[0]) == 'application/pdf' and mimes.get('tilesmith-canvas.png') == 'image/png' and len(r['calls']) == 3 and r['toast'].startswith('Saved')
        # a big file crosses in pieces (chunking)
        await pg.evaluate("__calls.length=0")
        r = await pg.evaluate("""async()=>{const n=2500000,a=new Uint8Array(n);for(let i=0;i<n;i++)a[i]=(i*7)&255;
            const ok=await TSM.saveFile(new Blob([a],{type:'application/octet-stream'}),'big:/file.bin');return{ok,writes:__calls.filter(c=>c[0]=='write').map(c=>[c[1],c[3]])}}""")
        files = await pg.evaluate('__files'); big = base64.b64decode(''.join(files['big-file.bin']))
        good = len(big) == 2500000 and all(big[i] == (i * 7) & 255 for i in range(0, 2500000, 9973))
        print('BIG', r['ok'], len(r['writes']), r['writes'][:4], 'bytes ok', good)
        ok &= r['ok'] is True and len(r['writes']) == 4 and r['writes'][0][1] is False and all(w[1] for w in r['writes'][1:]) and good
        # share sheet closed without picking an app
        await pg.evaluate("window.__cancel=true;__calls.length=0"); await pg.click('#bar [data-a=pdf]'); await pg.wait_for_timeout(400)
        t = await pg.evaluate("document.querySelector('#toast').textContent"); print('CANCEL toast', t); ok &= t.startswith('Not saved')
        await pg.evaluate("window.__cancel=false")
        # write failure
        await pg.evaluate("window.__failWrite=true"); await pg.click('#bar [data-a=pdf]'); await pg.wait_for_timeout(400)
        t = await pg.evaluate("document.querySelector('#toast').textContent"); print('FAIL toast', t); ok &= 'disk full' in t
        await pg.evaluate("window.__failWrite=false")
        # links: Ko-fi, the ndi.video links are hidden on mobile, mail link
        await pg.evaluate("__calls.length=0;document.querySelector('#bar [data-a=about]').click()"); await pg.wait_for_timeout(200)
        await pg.click('#kofi')
        await pg.evaluate("[...document.querySelectorAll('#about a')].filter(a=>/^mailto:/.test(a.getAttribute('href')||'')).forEach(a=>a.click())")
        links = await pg.evaluate("__calls"); print('LINKS', links); ok &= any(c[0] == 'url' and 'ko-fi.com' in c[1] for c in links)
        await pg.evaluate("showAbout(0)")
        # video: MediaRecorder -> streamed file -> share; then a cancelled recording
        await pg.evaluate("()=>{S.x=0;S.ox=0;S.cols=2;S.rows=2;S.speed=5;S.vIntro=1;S.vHold=1;storeWall();showAll();sync();__calls.length=0;if(!MediaRecorder.isTypeSupported('video/mp4'))window.mrType=()=>'video/webm'}")
        await pg.evaluate("document.querySelector('[data-a=rec]').click()")
        for i in range(40):
            await pg.wait_for_timeout(500)
            st = await pg.evaluate("document.querySelector('#vexps').textContent")
            if st.startswith('Saved') or 'Could not' in st or 'failed' in st: break
        r = await pg.evaluate("()=>({st:document.querySelector('#vexps').textContent,calls:__calls.filter(c=>c[0]!='write'),writes:__calls.filter(c=>c[0]=='write').length})")
        print('REC', r); files = await pg.evaluate('__files'); vids = [k for k in files if k.endswith('.mp4')]; print('video', vids, [size(files, k) for k in vids])
        ok &= r['st'].startswith('Saved') and any(c[0] == 'share' and c[2] == 'video/mp4' for c in r['calls']) and ['awake', True] in r['calls'] and ['awake', False] in r['calls'] and r['writes'] >= 2
        await pg.evaluate("__calls.length=0"); await pg.evaluate("document.querySelector('[data-a=rec]').click()"); await pg.wait_for_timeout(1800); await pg.evaluate("document.querySelector('[data-a=rec]').click()"); await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>({st:document.querySelector('#vexps').textContent,calls:__calls.filter(c=>c[0]!='write')})"); print('REC CANCEL', r)
        ok &= r['st'] == 'Recording cancelled' and not any(c[0] == 'share' for c in r['calls']) and any(c[0] == 'delete' for c in r['calls'])
        print('errors', errs); ok &= not errs
        await ctx.close()
        # without the Kotlin interface the page stays the plain web version
        ctx = await b.new_context(); pg = await ctx.new_page(); await pg.goto(APP); await pg.wait_for_timeout(600)
        r = await pg.evaluate("({MOBILE,cap:!!window.Capacitor,tsm:!!window.TSM})"); print('PLAIN', r); ok &= not r['MOBILE'] and not r['cap'] and not r['tsm']
        await ctx.close(); await b.close()
    print('ALL OK' if ok else 'PROBLEMS'); return ok
if __name__ == '__main__': sys.exit(0 if asyncio.run(main()) else 1)
