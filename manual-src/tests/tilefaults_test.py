"""Tile faults, Random mix: one random tile gets a random fault, never the same one twice in a row, every fault turns up,
several random tiles get different faults, and the status line names the faults. Prints ALL OK."""
import asyncio, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TILESMITH_ROOT') or os.path.dirname(os.path.dirname(HERE))
APP = 'file://' + os.path.join(ROOT, 'tilesmith-desktop', 'app', 'index.html')
async def main():
    ok = True
    def chk(c, name=''):
        nonlocal ok
        if not c: print('FAILED', name)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {})); pg = await b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = pg.evaluate
        async def setk(k, v):
            await ev("([k,v])=>{const e=document.querySelector('[data-k='+k+']');e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}", [k, v])
        async def tap(a): await ev("(a)=>document.querySelector('#glBox [data-a='+a+']').click()", a)
        await setk('glType', 'Random mix'); await setk('glPick', 'Random'); await setk('glN', '1'); await pg.wait_for_timeout(100)
        # one random tile, started and stopped 60 times through the Start button
        seen = []
        for i in range(60):
            await tap('glgo'); await pg.wait_for_timeout(20)
            r = await ev("()=>({on:S.glOn,f:glList(S).map(f=>GLT[f.t]),st:document.querySelector('#glStat').textContent})")
            chk(r['on'] and len(r['f']) == 1, f'run {i}: one faulty tile'); seen += r['f']
            if i == 0: print('STATUS', r['st']); chk(('Faults: ' + r['f'][0]) in r['st'], 'status names the fault')
            await tap('glgo'); await pg.wait_for_timeout(20)
        kinds = sorted(set(seen)); print('SEEN', len(kinds), 'kinds;', seen.count('Dead tile'), 'x Dead tile in', len(seen))
        chk(len(kinds) >= 10, 'random fault varies'); chk(seen.count('Dead tile') < 20, 'not stuck on Dead tile')
        chk(all(a != b for a, b in zip(seen, seen[1:])), 'never the same fault twice in a row')
        # twelve random tiles: twelve different faults
        await setk('glN', '12'); await tap('glgo'); await pg.wait_for_timeout(50)
        f = await ev("()=>glList(S).map(f=>GLT[f.t])"); print('TWELVE', f); chk(len(f) == 12 and len(set(f)) == 12, '12 tiles, 12 faults')
        await tap('glgo')
        # picked tiles in Random mix: consecutive picks differ too
        r = await ev("()=>{const a=[];for(let i=0;i<30;i++)a.push(glRT());return a}"); chk(all(x != y for x, y in zip(r, r[1:])), 'picked tiles vary')
        chk(not errs, 'no page errors: ' + '; '.join(errs[:3]))
        await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
