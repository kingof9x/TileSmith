import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1100}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.select_option('[data-brand]','Owl Vision'); await pg.select_option('[data-k=preset]','Owl Vision Black Owl 3.9 500×1000')
        await pg.evaluate("()=>{S.cols=4;S.rows=16;storeWall();sync();info()}")
        r=await pg.evaluate("()=>({proc:[...document.querySelectorAll('[data-k=proc] option')].map(o=>o.value),rows:wallRows(walls[cur]).slice(0,14).map(x=>x[0]),tiles:tileRows().map(x=>x[0]),half:getComputedStyle(document.querySelector('#halfBox')).display,warn:[...document.querySelectorAll('#right tr.warn')].map(t=>t.textContent.slice(0,40))})")
        print(r)
        assert all(x in('None','Custom') or x.startswith('NovaStar') for x in r['proc']) and 'Receiving card' in r['tiles'] and r['half']!='none' and any('HANGING' in w for w in r['warn'])
        await pg.select_option('[data-k=preset]','Owl Vision Pilot 2.6')
        r=await pg.evaluate("()=>[S.preset,tileRows().find(x=>x[0]=='Receiving card')]"); print(r)
        assert not errs,errs; print('ALL OK'); await b.close()
asyncio.run(main())
