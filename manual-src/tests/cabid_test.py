# Cabinet IDs (Engineering › Cabinet IDs): each tile's address from the data wiring, the "cabinet IDs" test pattern,
# the printable sheet (a map and a list per wall), stickers on the label sheet and the binder pages
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, json, os, re, subprocess, tempfile
from playwright.async_api import async_playwright
APP = TS_APP_URL
OUT = os.environ.get('CABID_OUT') or tempfile.mkdtemp(prefix='cabid')
SHOT = os.environ.get('CABID_SHOT')
def txt(path, first=None, last=None):
    a = ['pdftotext', '-layout'] + (['-f', str(first)] if first else []) + (['-l', str(last)] if last else []) + [path, '-']
    return subprocess.run(a, capture_output=True, text=True).stdout
def npages(path):
    return len(re.findall(rb'/Type\s*/Page[^s]', open(path, 'rb').read()))
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # nothing wired yet: no IDs, the panel says why, the sheet refuses
        r = await pg.evaluate("()=>({ids:cabIds().flat().length,stat:document.querySelector('#cidStat').textContent,any:cidAny()})")
        print('empty', r); ok &= r['ids'] == 0 and 'processor' in r['stat'] and not r['any']
        # two walls, 2 ports per processor, snake: IDs run processor 1 port 1 tile 1, 2, ... in data order
        r = await pg.evaluate("""()=>{S.cols=8;S.rows=5;S.name='Main';storeWall();S.proc='NovaStar VX1000 Pro';applySpec();S.pports=2;S.wmode='Snake';S.ret=false;storeWall();
          addWall(false);S.name='Side';S.cols=4;S.rows=4;S.ox=1600;S.oy=0;S.wmode='Snake';storeWall();S.showData=false;sync();
          const pl=portPlan(),ids=cabIds(),f=x=>({id:x.id,s:x.s,ps:x.ps,k:x.k,p:x.p,col:x.col,row:x.row});
          return{ports:pl.map(w=>w.map(x=>x.tiles.length)),n:ids.map(x=>x.length),a:ids[0].slice(0,2).map(f),last:f(ids[1][ids[1].length-1]),
           order:ids.flat().every((x,i,a)=>!i||a[i-1].p<x.p||(a[i-1].p==x.p&&a[i-1].k+1==x.k)),stat:document.querySelector('#cidStat').textContent}}""")
        print('ids', json.dumps(r)); ok &= r['n'] == [40, 16] and r['order'] and r['a'][0]['id'] == '1:P1:01' and r['a'][1]['id'] == '1:P1:02'
        np = sum(len(x) for x in r['ports']); last = r['last']
        ok &= last['p'] == np and last['s'] == (np - 1) // 2 + 1 and last['ps'] == (np - 1) % 2 + 1 and last['id'] == f"{last['s']}:P{last['ps']}:{last['k']:02d}"
        ok &= r['stat'] == f'56 tiles have an ID, on {np} ports.'
        # port-wide style: the port number on the canvas badges and cable labels
        r = await pg.evaluate("()=>{const s=document.querySelector('select[data-k=cidFmt]');s.value=s.options[1].value;applyKey(s);sync();const a=cabIds();return[a[0][0].id,a[1][a[1].length-1].id]}")
        print('fmt', r); ok &= r[0] == 'P1-01' and re.fullmatch(rf'P{np}-\d\d', r[1]) is not None
        await pg.evaluate("()=>{S.cidFmt=CIDFMT[0];sync()}")
        # Show on this wall picks the pattern; it draws without the tile label overlays and nothing throws
        r = await pg.evaluate("()=>{selWall(0);document.querySelector('[data-a=cidShow]').click();render();return{pat:walls[0].pat,other:walls[1].pat,list:PAT_LIST.includes('cabinet IDs')}}")
        print('pattern', r); ok &= r['pat'] == 'cabinet IDs' and r['other'] != 'cabinet IDs' and r['list']
        # the pattern really paints the wall: port 1's fill colour at the middle of the first tile's left edge area
        r = await pg.evaluate("""()=>{render();const w=walls[0],x=cabIds()[0][0].q,d=M.getContext('2d').getImageData(w.ox+x.x+Math.round(x.w*.15),w.oy+x.y+Math.round(x.h*.3),1,1).data;return[d[0],d[1],d[2]]}""")
        print('pixel', r); ok &= r == [0x0f, 0x3a, 0x45]
        if SHOT:
            await pg.evaluate("()=>{const d=document.querySelector('#cidStat').closest('details');d.open=true;d.closest('details:not(.subd)')&&(d.closest('details:not(.subd)').open=true);sync()}")
            await pg.wait_for_timeout(400); await pg.screenshot(path=SHOT)
        # the sheet: a map page and a list page per wall
        async with pg.expect_download() as d: await pg.evaluate("()=>cidPDF()")
        dl = await d.value; f = os.path.join(OUT, dl.suggested_filename); await dl.save_as(f); n = npages(f); print('sheet', dl.suggested_filename, n)
        ok &= '-cabinet-ids-' in dl.suggested_filename and n == 4
        t = txt(f); ok &= 'Main: cabinet IDs' in t and 'Side: cabinet IDs in data order' in t and '1:P1:01' in t and '40 of 40 tiles' in t
        # stickers: one per tile on the label sheet (Avery 5163 = 10 per sheet)
        async with pg.expect_download() as d: await pg.evaluate("()=>{S.cidStk=true;cidPDF()}")
        dl = await d.value; f2 = os.path.join(OUT, 'stk-' + dl.suggested_filename); await dl.save_as(f2); n2 = npages(f2); print('stickers', n2)
        ok &= n2 == 4 + 6 and 'Main · C1 R' in txt(f2, 5, 5)
        # the binder gets a Cabinet IDs section after the wall pages
        async with pg.expect_download() as d: await pg.evaluate("()=>{S.cidStk=false;exportPDF(true)}")
        dl = await d.value; f3 = os.path.join(OUT, dl.suggested_filename); await dl.save_as(f3); t2 = txt(f3, 2, 2)
        toc = {m.group(1).strip(): int(m.group(2)) for m in re.finditer(r'^\s*(\S[^\n]*?)\s{2,}[ .]*(\d+)\s*$', t2, re.M)}; print('toc', toc)
        ok &= toc.get('Cabinet IDs') == toc.get('LED walls') + 2 and toc.get('Pull sheet') == toc['Cabinet IDs'] + 4 and 'Main: cabinet IDs' in txt(f3, toc['Cabinet IDs'], toc['Cabinet IDs'])
        # saved and opened again keeps the style and the pattern
        r = await pg.evaluate("()=>{S.cidFmt=CIDFMT[1];const o=JSON.parse(JSON.stringify(stateObj()));S.cidFmt=CIDFMT[0];applyCore(o);sync();return{f:S.cidFmt,p:walls[0].pat}}")
        print('save', r); ok &= r == {'f': 'Port - tile (P12-07, as on the cable labels)', 'p': 'cabinet IDs'}
        # Spanish: the panel is translated
        r = await pg.evaluate("()=>['Cabinet IDs','ID style','Save cabinet ID sheet','Show on this wall','{0} tiles have an ID, on {1} ports.'].filter(k=>!TR[k])")
        r2 = await pg.evaluate("()=>{setLang('es');sync();const t=document.querySelector('#cidStat').textContent;setLang('en');sync();return t}")
        print('es', r2); ok &= r2.startswith('56 paneles tienen ID')
        print('missing TR', r); ok &= not r
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
