"""Export PDF (raster + spec sheet + cable labels), removed buttons, SMPTEbars image / smptescroll migration. Prints ALL OK."""
import asyncio, re
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    def chk(c, name=''):
        nonlocal ok
        if not c: print('FAILED', name)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = pg.evaluate
        bar = await ev("()=>[...document.querySelectorAll('#bar [data-a]')].map(e=>e.dataset.a)")
        chk('pdf' in bar and 'csv' not in bar and 'spec' not in bar and bar.index('pdf') == bar.index('png') + 1, 'bar ' + str(bar))
        chk('smptescroll' not in await ev("()=>PAT_LIST.concat(PATS)") and 'SMPTEbars' in await ev("()=>PAT_LIST"), 'pattern list')
        chk(await ev("()=>isImgPat('SMPTEbars')"), 'smpte is image pattern')
        # no wiring -> raster + spec only
        async with pg.expect_download() as d: await pg.click('#bar [data-a=pdf]')
        f = await d.value; path = await f.path(); data = open(path, 'rb').read()
        print(f.suggested_filename, len(data))
        chk(f.suggested_filename.endswith('.pdf') and data.startswith(b'%PDF-1.4') and data.rstrip().endswith(b'%%EOF'), 'pdf header')
        n0 = len(re.findall(rb'/Type /Page /', data)); chk(n0 >= 2, 'pages ' + str(n0))
        chk(b'DCTDecode' in data and b'LED Wall Spec' in data, 'raster + spec text')
        # wire data + power -> labels pages appear
        await ev("""()=>{S.cols=12;S.rows=8;S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.pdist=true;S.showPow=true;storeWall();sync();showAll()}""")
        await pg.wait_for_timeout(300)
        has = await ev("()=>lblHas()"); print(has)
        async with pg.expect_download() as d: await pg.click('#bar [data-a=pdf]')
        f = await d.value; data2 = open(await f.path(), 'rb').read(); n1 = len(re.findall(rb'/Type /Page /', data2))
        exp = await ev("()=>labelPages(labelList()).length"); print('pages', n1, 'label pages', exp)
        chk(has['on'] and exp >= 1 and n1 - exp >= n0, 'label pages added ' + str((n0, n1, exp)))
        chk(b'PROCESSOR END' in data2 or b'1/2' in data2, 'label text')
        # structure check: xref offsets point at "N 0 obj"
        sx = int(re.search(rb'startxref\n(\d+)', data2).group(1)); tbl = data2[sx:].split(b'\n')
        cnt = int(tbl[1].split()[1]); bad = 0
        for i in range(1, cnt):
            o = int(tbl[2 + i].split()[0]); 
            if not data2[o:].startswith(f'{i} 0 obj'.encode()): bad += 1
        chk(bad == 0, 'xref offsets ' + str(bad))
        # old saves with smptescroll load as SMPTEbars
        await ev("""()=>{const o=stateObj();o.walls[0].pat='smptescroll';o.S.pat='smptescroll';applyState(o)}""")
        chk(await ev("()=>walls[0].pat")=='SMPTEbars', 'migration')
        chk(not [e for e in errs if 'favicon' not in e], str(errs)); await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
