# Send a canvas to a display: the output window gets the canvas pixel for pixel (device pixels, no smoothing), follows redraws,
# closes with Esc, and the picker / notes follow the chosen display. The display list is faked (desktop app supplies it).
import asyncio
from playwright.async_api import async_playwright
async def main():
    ok=True
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1400,'height':900}); pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        await pg.evaluate("""()=>{window.__outTest=true;DISP=[{id:1,label:'Laptop',bounds:{x:0,y:0,width:1536,height:864},scale:1.25,px:[1920,1080],main:true},{id:2,label:'HDMI',bounds:{x:1536,y:0,width:1920,height:1080},scale:1,px:[1920,1080],main:false}];
          S.ids=true;S.cols=6;S.rows=4;storeWall();showAll();sync();document.querySelectorAll('#left>details').forEach(d=>d.open=true);document.querySelector('[data-cvd="0"]').open=true;cvUI()}""")
        opts=await pg.evaluate("()=>[...document.querySelectorAll('#outSel option')].map(o=>o.textContent)"); print(opts); ok=ok and len(opts)==3 and 'HDMI' in opts[2]
        async with pg.expect_popup() as pop: await pg.select_option('#outSel','2')
        win=await pop.value; await pg.wait_for_timeout(900)
        note=await pg.evaluate("()=>document.querySelector('#outNote').textContent"); print(note); ok=ok and 'fills this display exactly' in note
        # every pixel of the output equals the canvas
        r=await pg.evaluate("""()=>{const o=OUTW.get(CVS[cc]);forceRen=true;tick(performance.now());outDraw(CVS[cc],true);const a=mc.getImageData(0,0,M.width,M.height).data,b=o.x.getImageData(0,0,o.cv.width,o.cv.height).data;
          let diff=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i])diff++;return[o.cv.width,o.cv.height,o.cv.style.width,diff]}""")
        print(r); ok=ok and r[0]==1920 and r[1]==1080 and r[3]==0
        # scaled display: CSS size compensates so 1 canvas px = 1 device px
        r=await pg.evaluate("()=>{const o=OUTW.get(CVS[cc]);Object.defineProperty(o.win,'devicePixelRatio',{value:1.25,configurable:true});outDraw(CVS[cc],true);return[o.cv.style.width,o.cv.style.height]}"); print(r); ok=ok and r==['1536px','864px']
        # a change on the canvas reaches the output
        r=await pg.evaluate("""()=>{const o=OUTW.get(CVS[cc]);S.pat='red';storeWall();sync();forceRen=true;tick(performance.now());const q=o.x.getImageData(200,200,1,1).data;return[...q]}"""); print('after pattern change',r); ok=ok and r[0]>200 and r[1]<40
        # Esc closes it
        await pg.evaluate("()=>{const o=OUTW.get(CVS[cc]);o.win.dispatchEvent(new o.win.KeyboardEvent('keydown',{key:'Escape'}))}"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>[OUTW.size,document.querySelector('#outSel').value]"); print(r); ok=ok and r==[0,'']
        ok=ok and not errs; print('errs',errs); print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
