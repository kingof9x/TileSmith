import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':1100})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        async def setm(v): await pg.evaluate('(b)=>{const e=document.querySelector("[data-k=preset]");e.value=b;e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))}',v)
        r=await pg.evaluate("()=>[...document.querySelector('[data-brand]').options].map(o=>o.text)"); print(r)
        assert r[:6]==['ROE','Absen','Unilumin','INFiLED','YES TECH','Owl Vision'],r
        for br,n in [('Absen',7),('Unilumin',4),('INFiLED',17),('YES TECH',17),('Owl Vision',2)]:
            await pg.evaluate('(b)=>{const e=document.querySelector("[data-brand]");e.value=b;e.dispatchEvent(new Event("change",{bubbles:true}))}',br); await pg.wait_for_timeout(200)
            m=await pg.evaluate("()=>[document.querySelector('[data-brand]').value,S.preset,document.querySelectorAll('[data-k=preset] option').length]")
            print(m); assert m[0]==br and m[1].startswith(br) and m[2]>=n,(br,m)
        await pg.evaluate('()=>brandPick("INFiLED")')
        await setm('INFiLED Deep Black DB3.4 Pro'); await pg.wait_for_timeout(200)
        t=await pg.evaluate("()=>document.querySelector('#right tr.warn')&&document.querySelector('#right tr.warn').textContent")
        print(t); assert t and 'MISSING DATA' in t
        await setm('INFiLED AR4.8'); await pg.wait_for_timeout(200)
        assert await pg.evaluate("()=>!document.querySelector('#right tr.warn')")
        await pg.evaluate('()=>{const e=document.querySelector("[data-brand]");e.value="ROE";e.dispatchEvent(new Event("change",{bubbles:true}))}'); await pg.wait_for_timeout(200)
        assert await pg.evaluate("()=>S.preset.startsWith('ROE')")
        assert not errs,errs
        print('ALL OK'); await b.close()
asyncio.run(main())
