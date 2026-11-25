# Left panel sub menus open one at a time; double-clicking a sub menu header keeps the others open (power users)
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio
from playwright.async_api import async_playwright
async def main():
    ok=True
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':1000}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(TS_APP_URL); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        # open sub menus (direct children of the menu) in a top-level menu
        # tag the top-level menus and their direct sub menus so plain CSS selectors can reach them
        names=await pg.evaluate("""()=>{const t=[...document.querySelectorAll('#left>details')].find(d=>d.firstElementChild.textContent.includes('Animation Options'));t.id='tAnim';
          t.querySelector(':scope>summary').id='tAnimS';return [...t.querySelectorAll(':scope>.sec>details.subd')].map((d,i)=>{d.dataset.ts=i;return d.firstElementChild.textContent.trim()})}""")
        top='#tAnim'; await pg.click('#tAnimS')
        print('Animation Options sub menus:',names); ok=ok and len(names)>=3
        sub=lambda n: f"#tAnim details[data-ts='{names.index(n)}']"
        isopen=lambda n: pg.evaluate(f"()=>document.querySelector(\"{sub(n)}\").open")
        a,c,d=names[0],names[1],names[2]
        await pg.click(sub(a)+">summary"); await pg.wait_for_timeout(400)
        await pg.click(sub(c)+">summary"); await pg.wait_for_timeout(400)
        v=[await isopen(a),await isopen(c)]; print('single click second:',v); ok=ok and v==[False,True]
        await pg.dblclick(sub(d)+">summary"); await pg.wait_for_timeout(400)
        v=[await isopen(a),await isopen(c),await isopen(d)]; print('double click third:',v); ok=ok and v==[False,True,True]
        await pg.dblclick(sub(a)+">summary"); await pg.wait_for_timeout(400)
        v=[await isopen(a),await isopen(c),await isopen(d)]; print('double click first:',v); ok=ok and v==[True,True,True]
        await pg.click(sub(c)+">summary"); await pg.wait_for_timeout(400)
        v=[await isopen(a),await isopen(c),await isopen(d)]; print('single click closes only that one:',v); ok=ok and v==[True,False,True]
        await pg.click(sub(c)+">summary"); await pg.wait_for_timeout(400)
        v=[await isopen(a),await isopen(c),await isopen(d)]; print('single click opens it alone again:',v); ok=ok and v==[False,True,False]
        # top-level menus stay open together
        await pg.click("#left>details>summary:has-text('Canvases')"); await pg.wait_for_timeout(200)
        v=await pg.evaluate(f"()=>[document.querySelector(\"{top}\").open,[...document.querySelectorAll('#left>details')].find(d=>d.firstElementChild.textContent.includes('Canvases')).open]"); print('top-level both open:',v); ok=ok and v==[True,True]
        # nested sub menu: opening one inside a sub menu keeps its parent open
        if not await pg.evaluate("()=>document.querySelector('#cvList>details').open"): await pg.click("[data-cvs='0']"); await pg.wait_for_timeout(400)
        await pg.click("details.subd>summary:has-text('LED walls')"); await pg.wait_for_timeout(400)
        await pg.click("details.subd>summary:has-text('Tile model')"); await pg.click("details.subd>summary:text-is('Tile details')"); await pg.wait_for_timeout(300)
        v=await pg.evaluate("()=>[...document.querySelectorAll('details.subd')].filter(d=>d.open).map(d=>d.firstElementChild.textContent.trim())"); print('open subs:',v)
        ok=ok and any(x.startswith('Tile model') for x in v) and 'Tile details' in v and 'Canvas 1' in ' '.join(v) and 'LED walls' not in v
        # canvases: one canvas sub menu at a time, double-click keeps both open
        await pg.click("[data-a=cvadd]"); await pg.wait_for_timeout(500)
        cv=lambda: pg.evaluate("()=>[...document.querySelectorAll('#cvList>details')].map(d=>d.open)+'|'+CVS.map(c=>!!c.open)")
        v=await cv(); print('after adding a canvas:',v)
        await pg.click("[data-cvs='0']"); await pg.wait_for_timeout(500); v=await cv(); print('canvas 1 clicked:',v); ok=ok and v=='true,false|true,false'
        await pg.click("[data-cvs='1']"); await pg.wait_for_timeout(500); v=await cv(); print('canvas 2 clicked:',v); ok=ok and v=='false,true|false,true'
        await pg.dblclick("[data-cvs='0']"); await pg.wait_for_timeout(500); v=await cv(); print('canvas 1 double-clicked:',v); ok=ok and v=='true,true|true,true'
        # double-click the lower canvas while the upper one holds the controls: the list moves under the pointer, still a double-click
        await pg.click("[data-cvs='1']"); await pg.wait_for_timeout(500); await pg.click("[data-cvs='0']"); await pg.wait_for_timeout(500)
        await pg.dblclick("[data-cvs='1']"); await pg.wait_for_timeout(500); v=await cv(); n=await pg.evaluate("()=>[CVS.length,cc]")
        print('canvas 2 double-clicked from below:',v,n); ok=ok and v=='true,true|true,true' and n==[2,1]
        ok=ok and not errs; print(errs); print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
