# Technician character style: the dropdown offers Classic and Character pack, Classic draws through a whole build,
# the choice is saved, and a project that picked the removed Cartoon style falls back to Classic.
import asyncio, sys
from playwright.async_api import async_playwright
APP = '/home/claude/tilesmith-desktop/app/index.html'
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
        chk(opts == ['Classic', 'Character pack'], f'dropdown lists the styles {opts}')
        chk(await pg.evaluate("()=>S.tstyle") == 'Classic', 'default is Classic')
        await pg.evaluate("()=>{S.cols=4;S.rows=3;storeWall();showAll();sync();fit();reset();S.play=true}")
        seen = set()
        for i in range(40):
            await pg.evaluate("()=>{for(let k=0;k<20;k++)step(1/60);forceRen=true}"); await pg.wait_for_timeout(30); seen.add(await pg.evaluate("()=>sims[0].ph"))
        chk(len(seen) >= 3, f'Classic build phases ran {sorted(seen)}')
        chk(await pg.evaluate("()=>typeof workerCartoon") == 'undefined', 'Cartoon drawing code is gone')
        await pg.evaluate("()=>{S.tstyle='Character pack'}")
        o = await pg.evaluate("()=>stateObj()")
        chk(o['S'].get('tstyle') == 'Character pack', 'style is part of the saved state')
        await pg.evaluate("(o)=>{S.tstyle='Classic';applyState(o)}", o)
        chk(await pg.evaluate("()=>S.tstyle") == 'Character pack', 'style restored when state is loaded')
        o['S']['tstyle'] = 'Cartoon'
        await pg.evaluate("(o)=>applyState(o)", o)
        chk(await pg.evaluate("()=>S.tstyle") == 'Classic', 'a project with the removed Cartoon style opens as Classic')
        await pg.evaluate("()=>{S.tstyle='Character pack';S.tpack='';reset();for(let k=0;k<200;k++)step(1/60);forceRen=true}")
        chk(await pg.evaluate("()=>{let n=0;const o=workerPack;window.workerPack=function(){n++;return o.apply(this,arguments)};drawTech(document.createElement('canvas').getContext('2d'),100,100,100,{th:1,mv:0,m:crew[0],ix:0,hands:null});return n}") == 1, 'Character pack with no pack chosen draws the built-in Khalid')
        chk(not errs, f'no page errors {errs[:2]}')
        await b.close(); print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
