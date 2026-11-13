# Show binder (Export binder): cover, contents, canvas, a page per wall, pull sheet, spec sheet, labels
import asyncio, json, os, re, subprocess, tempfile
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
OUT = os.environ.get('BINDER_OUT') or tempfile.mkdtemp(prefix='binder')
def txt(path, first=None, last=None):
    a = ['pdftotext', '-layout'] + (['-f', str(first)] if first else []) + (['-l', str(last)] if last else []) + [path, '-']
    return subprocess.run(a, capture_output=True, text=True).stdout
def npages(path):
    from pypdf import PdfReader
    return len(PdfReader(path).pages)
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        await pg.evaluate("""()=>{S.cw=3840;S.ch=2160;S.cols=12;S.rows=6;S.name='Main';storeWall();addWall(false);S.name='Side';S.cols=8;S.rows=5;S.ox=2500;S.oy=0;storeWall();sync();
          S.proc='NovaStar VX1000 Pro';applySpec();S.pdist=true;S.pdt='Socapex (6 circuits per cable)';walls.forEach(w=>{w.wmode='Snake';w.pmode='Snake'});loadWall(0);
          S.bShow='Spring Tour 2027';S.bVenue='Hall B';S.bDate='2027-03-14';S.spT=5;S.spC=1;S.showData=false;sync()}""")
        # pull sheet without cable lengths: home runs without a length; tiles + spares
        r = await pg.evaluate("()=>pullItems()"); print('items', json.dumps(r))
        vid = dict((x[0], x) for x in r[0][1]); t = sum(x[1] for k, x in vid.items() if k.endswith('tile'))
        ok &= r[0][0] == 'Video' and t == 72 + 40 and all(x[2] == -(-x[1] * 5 // 100) for k, x in vid.items() if k.endswith('tile'))
        ok &= any('length not set' in x[0] for x in r[1][1]) and 'NovaStar VX1000 Pro' in vid
        # with cable lengths: cables by length, totals match cabRuns
        r = await pg.evaluate("()=>{S.cabOn=true;sync();const it=pullItems(),R=cabRuns(),n=R.filter(x=>x.kind!='p').reduce((a,x)=>a+x.cab.length,0);return{it,n}}")
        dat = r['it'][1][1]; print('data', dat); ok &= sum(x[1] for x in dat if x[0].startswith('Data cable')) == r['n'] and all(x[2] == 1 for x in dat if x[0].startswith('Data cable'))
        # export the binder
        async with pg.expect_download() as d: await pg.click('[data-a=binder]:visible')
        dl = await d.value; f = os.path.join(OUT, dl.suggested_filename); await dl.save_as(f); n = npages(f); print('file', dl.suggested_filename, n, 'pages')
        ok &= dl.suggested_filename.startswith('Spring_Tour_2027-binder-')
        t1, t2 = txt(f, 1, 1), txt(f, 2, 2); print(t2)
        ok &= 'Spring Tour 2027' in t1 and 'Hall B' in t1 and '2 LED walls' in t1 and 'Contents' in t2
        toc = {m.group(1).strip(): int(m.group(2)) for m in re.finditer(r'^\s*(\S[^\n]*?)\s{2,}[ .]*(\d+)\s*$', t2, re.M)}; print('toc', toc)
        ok &= toc.get('Canvas') == 3 and toc.get('LED walls') == 4 and toc.get('Pull sheet') == 6
        ok &= 'Main' in txt(f, 4, 4) and 'Side' in txt(f, 5, 5)
        ps = txt(f, 6, 6); print(ps[:1500]); ok &= 'pull sheet' in ps and 'NEED' in ps and 'PULLED' in ps and 'Pulled by' in ps
        ok &= 'LED Wall Spec' in txt(f, toc['Spec sheet'], toc['Spec sheet'])
        # the plain Export PDF is unchanged: no cover, no pull sheet
        async with pg.expect_download() as d: await pg.evaluate("()=>exportPDF()")
        dl = await d.value; g = os.path.join(OUT, dl.suggested_filename); await dl.save_as(g); t = txt(g); print('plain', dl.suggested_filename, npages(g))
        ok &= 'pull sheet' not in t and 'Contents' not in t and npages(g) == n - 5
        # paths toggles restored after the binder
        r = await pg.evaluate("()=>[S.showData,S.showPow]"); ok &= r == [False, True] or r[0] is False; print('toggles', r)
        # settings saved with the project
        r = await pg.evaluate("()=>{const o=stateObj();return[o.S.bShow,o.S.spT,o.S.spC]}"); ok &= r == ['Spring Tour 2027', 5, 1]
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
