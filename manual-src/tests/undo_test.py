"""Undo/redo (20 steps, menu, Ctrl+Z), centre/show-all buttons, New Project. Prints ALL OK."""
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = lambda js, *a: pg.evaluate(js, *a)
        async def setk(k, v):
            await pg.evaluate("([k,v])=>{const e=document.querySelector('[data-k='+k+']');e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}", [k, v])
        async def tap(a):
            await pg.evaluate("(a)=>document.querySelector('[data-a='+a+']').click()", a)
        # idle: no phantom history
        await pg.wait_for_timeout(1500)
        r = await ev("()=>UN.st.length"); print('IDLE', r); ok = ok and bool(r == 0)
        # typing 3 digits in Columns merges into one step; a select and a button are separate steps
        await setk('cols', '9'); await pg.wait_for_timeout(100)
        await setk('pat', 'circles'); await pg.wait_for_timeout(100)
        await tap('wadd'); await pg.wait_for_timeout(200)
        r = await ev("()=>({n:UN.st.map(x=>x.label),walls:walls.length,cols:walls[0].cols})"); print('STEPS', r); ok = ok and bool(len(r['n']) == 3 and r['walls'] == 2)
        # menu lists newest first, Ctrl+Z undoes one, Ctrl+Y redoes
        await pg.click('[data-a=undom]'); await pg.wait_for_timeout(100)
        items = await ev("()=>[...document.querySelectorAll('#undom button')].map(b=>b.textContent)"); print('MENU', items); ok = ok and bool(len(items) == 3 and items[0].startswith('1.'))
        await pg.keyboard.press('Escape'); await pg.mouse.click(700, 500)
        await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(200)
        r = await ev("()=>({walls:walls.length,pat:S.pat,st:UN.st.length,rd:UN.rd.length})"); print('CTRL+Z', r); ok = ok and bool(r['walls'] == 1 and r['st'] == 2 and r['rd'] == 1)
        await pg.keyboard.press('Control+y'); await pg.wait_for_timeout(200)
        r = await ev("()=>({walls:walls.length,st:UN.st.length,rd:UN.rd.length})"); print('CTRL+Y', r); ok = ok and bool(r['walls'] == 2 and r['rd'] == 0)
        # go back several steps from the menu
        await pg.click('[data-a=undom]'); await pg.click('#undom button[data-v="3"]'); await pg.wait_for_timeout(200)
        r = await ev("()=>({walls:walls.length,cols:S.cols,pat:S.pat,st:UN.st.length})"); print('MENU x3', r); ok = ok and bool(r['walls'] == 1 and r['cols'] == 6 and r['st'] == 0)
        # 20 step cap
        await ev("()=>{for(let i=0;i<30;i++){S.cols=2+(i%5)+i;sync();unCheck('c'+i)}}")
        r = await ev("()=>UN.st.length"); print('CAP', r); ok = ok and bool(r == 20)
        # wall drag is one step
        await ev("()=>{S.cols=6;S.rows=4;sync();fit();UN.st=[];UN.rd=[];unBase()}")
        box = await pg.evaluate("()=>{const r=vp.getBoundingClientRect(),w=walls[0];return[r.left+V.x+(w.ox+wW(w)/2)*V.z,r.top+V.y+(w.oy+wH(w)/2)*V.z]}")
        await pg.mouse.move(*box); await pg.mouse.down(); await pg.mouse.move(box[0]+100, box[1]+60, steps=6); await pg.mouse.move(box[0]+200, box[1]+120, steps=6); await pg.mouse.up(); await pg.wait_for_timeout(200)
        r = await ev("()=>({st:UN.st.map(x=>x.label),ox:S.ox,oy:S.oy})"); print('DRAG', r); ok = ok and bool(len(r['st']) == 1 and r['st'][0].startswith('Moved') and bool(r['ox'] or r['oy']))
        await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(200)
        r = await ev("()=>[S.ox,S.oy]"); print('DRAG UNDO', r); ok = ok and bool(r == [0, 0])
        # centre / show entire canvas
        await ev("()=>{V.z=0.2;V.x=5;V.y=5}"); await pg.click('[data-a=ctr]'); await pg.wait_for_timeout(100)
        r = await ev("()=>{const q=vp.getBoundingClientRect();return{z:V.z,cx:V.x+S.cw*V.z/2-q.width/2,cy:V.y+S.ch*V.z/2-q.height/2}}"); print('CENTRE', r); ok = ok and bool(r['z'] == 0.2 and abs(r['cx']) < 1 and abs(r['cy']) < 1)
        await pg.click('[data-a=fit]'); await pg.wait_for_timeout(100)
        r = await ev("()=>V.z>0.2&&Math.abs(V.z-fitZ())<1e-6"); print('SHOW ALL', r); ok = ok and bool(r)
        # new canvas: asks first, wipes, undo brings it back
        await ev("()=>{S.cols=11;S.pat='circles';S.ndiName='MyNdi';addWall(false);sync();unCheck('setup')}")
        await pg.click('[data-a=newc]'); await pg.wait_for_timeout(100)
        vis = await ev("()=>!!document.querySelector('#newc')"); ok = ok and bool(vis)
        await pg.click('#newc button[data-n="0"]'); r = await ev("()=>walls.length"); ok = ok and bool(r == 2)
        await pg.click('[data-a=newc]'); await pg.click('#newc button[data-n="1"]'); await pg.wait_for_timeout(300)
        r = await ev("()=>({walls:walls.length,cols:S.cols,pat:S.pat,ndi:S.ndiName,last:UN.st[UN.st.length-1].label})"); print('NEW', r); ok = ok and bool(r['walls'] == 1 and r['cols'] == 6 and r['ndi'] == 'TileSmith-LED-Out' and r['last'] == 'New Project')
        await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(300)
        r = await ev("()=>({walls:walls.length,cols:walls[0].cols,ndi:S.ndiName})"); print('NEW UNDO', r); ok = ok and bool(r['walls'] == 2 and r['ndi'] == 'MyNdi')
        print('errors', errs); ok = ok and bool(not errs)
        await b.close()
    print('ALL OK' if ok else 'PROBLEMS')
asyncio.run(main())
