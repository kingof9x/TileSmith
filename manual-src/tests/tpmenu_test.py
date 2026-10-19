# Test pattern submenu in both the canvas menu and Animation Options: one set of controls follows the submenu that is opened
import asyncio
from playwright.async_api import async_playwright
async def main():
    ok=True
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':1000}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        where="()=>document.querySelector('#tpCtl').closest('.tpSlot').dataset.tp"
        ok=ok and await pg.evaluate("()=>document.querySelectorAll('.tpSlot').length")==2
        await pg.click("#left>details>summary:has-text('Animation Options')")
        await pg.click("details.subd>summary:has-text('Test pattern') >> nth=1"); await pg.wait_for_timeout(200)
        w=await pg.evaluate(where); print('after opening Animation Options › Test pattern:',w); ok=ok and w=='anim'
        await pg.select_option("[data-tp=anim] select[data-k=pat]",'SMPTEbars'); await pg.wait_for_timeout(100)
        ok=ok and await pg.evaluate("()=>S.pat=='SMPTEbars'&&walls[cur].pat=='SMPTEbars'")
        await pg.click("#left>details>summary:has-text('Canvases')"); await pg.click("[data-cvs='0']")
        await pg.click("details.subd>summary:has-text('Test pattern') >> nth=0"); await pg.wait_for_timeout(200)
        w=await pg.evaluate(where); print('after opening the canvas one:',w); ok=ok and w=='cv'
        v=await pg.evaluate("()=>[document.querySelector('[data-tp=cv] select[data-k=pat]').value,getComputedStyle(document.querySelector('[data-tp=anim]').parentNode.querySelector('.tpAway')).display]"); print(v); ok=ok and v==['SMPTEbars','block']
        ok=ok and not errs; print(errs); print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
