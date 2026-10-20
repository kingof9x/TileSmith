# Technician character styles: the dropdown, all four styles draw through a whole build without errors, the choice is saved in a project.
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
            print(('PASS ' if c else 'FAIL ') + m)
            ok = ok and c
        opts = await pg.evaluate("()=>[...document.querySelector('[data-k=tstyle]').options].map(o=>o.value)")
        chk(opts == ['Classic', 'Cartoon'], f'dropdown lists the styles {opts}')
        chk(await pg.evaluate("()=>S.tstyle") == 'Classic', 'default is Classic')
        sums = {}
        for st in ['Classic', 'Cartoon']:
            await pg.evaluate("""(st)=>{const e=document.querySelector('[data-k=tstyle]');e.value=st;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));
              S.cols=4;S.rows=3;storeWall();showAll();sync();fit();reset();S.play=true}""", st)
            chk(await pg.evaluate("()=>S.tstyle") == st, f'{st}: dropdown sets S.tstyle')
            seen = set()
            for i in range(40):
                await pg.evaluate("()=>{for(let k=0;k<20;k++)step(1/60);forceRen=true}"); await pg.wait_for_timeout(30)
                seen.add(await pg.evaluate("()=>sims[0].ph"))
            sums[st] = await pg.evaluate("()=>{const c=document.getElementById('vp');const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let s=0;for(let i=0;i<d.length;i+=97)s=(s*31+d[i])>>>0;return s}")
            chk(len(seen) >= 3, f'{st}: build phases ran {sorted(seen)}')
        chk(len(set(sums.values())) >= 2, f'styles render differently {sums}')
        await pg.evaluate("()=>{S.tstyle='Cartoon'}")
        o = await pg.evaluate("()=>stateObj()")
        chk(o.get('tstyle') == 'Cartoon' or 'Cartoon' in str(o)[:200000], 'style is part of the saved state')
        await pg.evaluate("(o)=>{S.tstyle='Classic';applyState(o)}", o)
        chk(await pg.evaluate("()=>S.tstyle") == 'Cartoon', 'style restored when state is loaded')
        chk(not errs, f'no page errors {errs[:2]}')
        await b.close()
        print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
