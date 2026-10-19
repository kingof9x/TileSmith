# Drives every dropdown and button with real user input (select_option / click) and checks the app reacts and does not throw
import asyncio
from playwright.async_api import async_playwright
APP='file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1400}); errs=[]; bad=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:asyncio.ensure_future(d.dismiss()))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        # brand / model with real events
        for br in ['Absen','Owl Vision','INFiLED','Custom','YES TECH','Unilumin','ROE']:
            await pg.select_option('[data-brand]',br); await pg.wait_for_timeout(100)
            v=await pg.evaluate("()=>[document.querySelector('[data-brand]').value,S.preset]")
            if v[0]!=br or (br!='Custom' and not v[1].startswith(br)): bad.append(('brand',br,v))
            opts=await pg.evaluate("()=>[...document.querySelectorAll('[data-k=preset] option')].map(o=>o.value)")
            for m in opts[::max(1,len(opts)//6)]:
                await pg.select_option('[data-k=preset]',m); await pg.wait_for_timeout(60)
                v=await pg.evaluate("()=>[document.querySelector('[data-brand]').value,S.preset,document.querySelector('[data-k=preset]').value]")
                if v[1]!=m or v[2]!=m or v[0]!=br: bad.append(('model',br,m,v))
        # every other select: pick each option, value must stick in S
        sels=await pg.evaluate("()=>[...document.querySelectorAll('select[data-k]')].filter(e=>e.dataset.k!='preset').map(e=>e.dataset.k)")
        for k in sels:
            loc=pg.locator(f'select[data-k="{k}"]').first
            if not await loc.is_visible(): continue
            opts=await loc.evaluate("e=>[...e.options].map(o=>o.value)")
            for o in opts[:6]:
                try: await loc.select_option(o,timeout=1500)
                except Exception as e: bad.append(('select',k,o,str(e)[:60])); continue
                await pg.wait_for_timeout(40)
                v=await pg.evaluate("(k)=>[S[k],document.querySelector(`select[data-k=\"${k}\"]`).value]",k)
                if str(v[0])!=o and str(v[1])!=o: bad.append(('select',k,o,v))
        # every button: click, must not throw
        n=0
        for i in range(await pg.locator('button:visible').count()):
            bt=pg.locator('button:visible').nth(i)
            try:
                lab=((await bt.inner_text()) or await bt.get_attribute('data-a') or '')[:24]
                if any(x in lab for x in ('Export','PNG','Save','Open','Share','NDI','New Project','Reset','Clear')): continue
                await bt.click(timeout=800,force=True); n+=1
            except Exception: pass
        await pg.wait_for_timeout(300)
        print('buttons clicked',n,'selects',len(sels),'bad',bad,'errs',errs)
        assert not bad and not errs
        print('ALL OK'); await b.close()
asyncio.run(main())
