# Power, Fewest circuits: fewest circuits, even tiles per circuit, short snake runs (no long jumps), direction honoured
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        ok=True
        for cols,rows,t,d,exp in [(8,6,16,'Horizontal',[16]*3),(8,6,16,'Vertical',[12]*4),(10,6,16,'Horizontal',[15]*4),(7,5,16,'Horizontal',None),(12,4,10,'Horizontal',None)]:
            r=await pg.evaluate("""([c,r,t,d])=>{const w={cols:c,rows:r,pcorner:'Top-left',pwdir:d,pmode:'Snake',pfill:'Fewest circuits'};
              const ch=autoChains({cols:c,rows:r,wcorner:'Top-left',wdir:d,wmode:'Snake',wfill:WFILL[0],pw:1},t);
              const jump=Math.max(...ch.map(x=>Math.max(0,...x.slice(1).map((p,i)=>Math.abs(p[0]-x[i][0])+Math.abs(p[1]-x[i][1]))))),n=ch.map(x=>x.length);return{n,jump,min:Math.ceil(c*r/t)}}""",[cols,rows,t,d])
            good=r['jump']==1 and max(r['n'])<=t and (exp is None or r['n']==exp) and len(r['n'])<=r['min']+1
            print(cols,rows,t,d,r,'ok' if good else 'BAD'); ok=ok and good
        print('ALL OK' if ok and not errs else 'SOME FAILED '+str(errs)); await b.close()
asyncio.run(main())
