import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1100})
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{S.cols=8;S.rows=6;S.pdist=true;S.showPow=true;S.pmode='Snake';storeWall();sync()}")
        for i in range(8):
            await pg.evaluate(f"()=>document.querySelector('[data-pp=\"{i}\"]').click()")
            r=await pg.evaluate("()=>{const t=powerPlan()[0][0].tiles;const cs=new Set(t.map(x=>x[0])),rs=new Set(t.map(x=>x[1]));return[S.pwdir,cs.size,rs.size,t[0].join()]}")
            V=r[0]=='Vertical'
            assert (r[1]<r[2]) if V else (r[2]<r[1]), (i,r)
        print('ALL OK')
        await b.close()
asyncio.run(main())
