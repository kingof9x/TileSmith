"""NovaStar controllers added Nov 2026 (MCTRL4K and the rest): each is in the Processor list, ports / pixels per port
follow the spec sheet at 8-bit and 10-bit, and picking MCTRL4K wires a wall. Prints ALL OK."""
import asyncio, os
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
# name: (ports, px per port at 60 Hz 8-bit, at 60 Hz 10-bit, max)
NEW = {'NovaStar MCTRL300': (2, 650000, 325000, 2304000), 'NovaStar MCTRL600': (4, 650000, 325000, 2304000),
       'NovaStar MCTRL660': (4, 650000, 325000, 2304000), 'NovaStar MCTRL660 PRO': (6, 650000, 325000, 2304000),
       'NovaStar MCTRL700': (6, 650000, 325000, 2304000), 'NovaStar MCTRL R5': (8, 650000, 325000, 4147200),
       'NovaStar MCTRL4K': (16, 650000, 320000, 8800000), 'NovaStar MX20': (6, 659722, 329861, 3900000),
       'NovaStar MX30': (10, 659722, 329861, 6500000), 'NovaStar NovaPro UHD Jr': (16, 650000, 320000, 10400000),
       'NovaStar VX16s': (16, 650000, 325000, 10400000), 'NovaStar VX600': (6, 650000, 325000, 3900000),
       'NovaStar VX600 Pro': (6, 650000, 325000, 3900000)}
async def main():
    ok = True
    def chk(c, name):
        nonlocal ok
        if not c: print('FAILED', name)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        opts = await pg.evaluate("()=>[...document.querySelectorAll('select[data-k=proc] option')].map(o=>o.value||o.textContent)")
        grp = await pg.evaluate("()=>[...document.querySelectorAll('select[data-k=proc] optgroup')].map(g=>g.label)")
        chk(grp.count('NovaStar') == 1, 'one NovaStar group ' + str(grp))
        for k, (ports, p8, p10, mx) in NEW.items():
            chk(k in opts, k + ' in the Processor list')
            r = await pg.evaluate("""k=>{const m=PROC[k];S.fps=60;S.bpc=8;const a=specPx(m);S.bpc=10;const c=specPx(m);S.bpc=8;
              return [m.brand,m.ports,a,c,m.max,procFam(k),!!m.note]}""", k)
            chk(r == ['NovaStar', ports, p8, p10, mx, 'novastar', True], k + ' ' + str(r))
        # pick MCTRL4K on a 24 x 12 wall of the default tile and wire it
        r = await pg.evaluate("""()=>{S.cols=24;S.rows=12;S.fps=60;S.bpc=8;S.proc='NovaStar MCTRL4K';applySpec();S.wmode='Snake';storeWall();sync();
          return [S.ppx,S.pports,document.querySelector('[data-k=proc]').value,document.querySelector('#pnote').textContent]}""")
        await pg.wait_for_timeout(400)
        chk(r[0] == 650000 and r[1] == 16 and r[2] == 'NovaStar MCTRL4K' and '16 × 1G' in r[3], 'MCTRL4K applied ' + str(r))
        out = os.environ.get('SHOT')
        if out: await pg.screenshot(path=out)
        chk(not errs, 'page errors ' + str(errs))
        await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
