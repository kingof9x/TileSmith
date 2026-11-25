# Technician character style: the dropdown offers Classic, Hand-drawn and Backlit, each one draws through a whole build,
# the choice is saved, and a project that picked a removed style (Cartoon, Character pack) falls back to Classic.
# (Character packs were removed; their test charpack_test.py went with them.)
import asyncio, sys, os
from playwright.async_api import async_playwright
APP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tilesmith-desktop', 'app', 'index.html'))
STYLES = ['Classic', 'Hand-drawn', 'Backlit']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        ok = True
        def chk(c, m):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ') + m); ok = ok and c
        opts = await pg.evaluate("()=>[...document.querySelector('[data-k=tstyle]').options].map(o=>o.value)")
        chk(opts == STYLES, f'dropdown lists the styles {opts}')
        chk(await pg.evaluate("()=>S.tstyle") == 'Classic', 'default is Classic')
        for st in STYLES:
            await pg.evaluate("st=>{S.tstyle=st;S.cols=4;S.rows=3;storeWall();showAll();sync();fit();reset();S.play=true}", st)
            seen = set()
            for i in range(40):
                await pg.evaluate("()=>{for(let k=0;k<20;k++)step(1/60);forceRen=true;render()}"); seen.add(await pg.evaluate("()=>sims[0].ph"))
            chk(len(seen) >= 3, f'{st}: build phases ran and drew {sorted(seen)}')
        chk(await pg.evaluate("()=>typeof workerCartoon=='undefined'&&typeof workerPack=='undefined'"), 'Cartoon and Character pack drawing code is gone')
        await pg.evaluate("()=>{S.tstyle='Backlit'}")
        o = await pg.evaluate("()=>stateObj()")
        chk(o['S'].get('tstyle') == 'Backlit', 'style is part of the saved state')
        await pg.evaluate("(o)=>{S.tstyle='Classic';applyState(o)}", o)
        chk(await pg.evaluate("()=>S.tstyle") == 'Backlit', 'style restored when state is loaded')
        for gone in ['Cartoon', 'Character pack']:
            o['S']['tstyle'] = gone
            await pg.evaluate("(o)=>applyState(o)", o)
            chk(await pg.evaluate("()=>S.tstyle") == 'Classic', f'a project with the removed {gone} style opens as Classic')
        chk(not errs, f'no page errors {errs[:2]}')
        await b.close(); print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
