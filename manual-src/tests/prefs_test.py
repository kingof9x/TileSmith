# Preferences: UI font picker (JetBrains Mono default, OpenDyslexic, Current) at the bottom of the
# Info popup, saved and restored; Engineering data toggle button (desktop only, hidden on mobile where
# the accordion caret already does the job), left-justified against Info/Report a bug on the right;
# and the mobile layout no longer clips the Engineering data panel to a short scrollable box.
import asyncio, sys
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ok=True
        def chk(c,msg):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ')+msg);ok=ok and c

        # --- desktop: font picker + Engineering data toggle ---
        pg=await b.new_page(viewport={'width':1400,'height':900})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html');await pg.evaluate("()=>localStorage.clear()");await pg.reload();await pg.wait_for_timeout(1000)

        chk(await pg.evaluate("()=>S.font")=='JetBrains Mono','font defaults to JetBrains Mono')
        fam=await pg.evaluate("()=>getComputedStyle(document.body).fontFamily")
        chk('JetBrains Mono' in fam,f'JetBrains Mono is actually applied to the page {fam}')

        await pg.click('[data-a=about]');await pg.wait_for_timeout(300)
        chk(await pg.evaluate("()=>!!document.querySelector('select[data-k=font]')"),'About popup has a UI font dropdown')
        opts=await pg.evaluate("()=>[...document.querySelector('select[data-k=font]').options].map(o=>o.value)")
        chk(set(opts)=={'JetBrains Mono','OpenDyslexic','Current'},f'dropdown offers JetBrains Mono, OpenDyslexic and Current {opts}')
        sel=await pg.eval_on_selector('select[data-k=font]',"e=>e.getBoundingClientRect()")
        dlg=await pg.eval_on_selector('#about .dlg',"e=>e.getBoundingClientRect()")
        chk(sel['bottom']>dlg['top']+(dlg['bottom']-dlg['top'])*0.5,'font picker sits in the lower half of the popup')

        await pg.select_option('select[data-k=font]','OpenDyslexic');await pg.wait_for_timeout(200)
        fam2=await pg.evaluate("()=>getComputedStyle(document.body).fontFamily")
        chk('OpenDyslexic' in fam2,f'switching to OpenDyslexic changes the applied font {fam2}')
        await pg.click('#cls');await pg.wait_for_timeout(200)

        # Engineering data toggle: right-justified, Info/Report a bug left-justified, same row
        eng=await pg.eval_on_selector('[data-a=engtog]',"e=>e.getBoundingClientRect()")
        info=await pg.eval_on_selector('[data-a=about]',"e=>e.getBoundingClientRect()")
        bug=await pg.eval_on_selector('[data-a=bugrpt]',"e=>e.getBoundingClientRect()")
        bar=await pg.eval_on_selector('#bar',"e=>e.getBoundingClientRect()")
        chk(abs(eng['top']-info['top'])<2,'Engineering data sits on the same row as Info')
        chk(eng['right']>bar['right']-10,'Engineering data is right-justified in its row')
        chk(info['left']<bar['left']+10 and info['right']<bug['right']<eng['left'],'Info and Report a bug are left-justified, before Engineering data')
        chk(await pg.evaluate("()=>document.querySelector('[data-a=engtog]').textContent")=='Hide Engineering Data','button reads Hide Engineering Data while the panel is shown')
        chk(await pg.evaluate("()=>document.querySelector('[data-a=engtog]').classList.contains('tgon')"),'Engineering data button is highlighted while the panel is shown')

        await pg.click('[data-a=engtog]');await pg.wait_for_timeout(200)
        chk(await pg.evaluate("()=>getComputedStyle(document.getElementById('right')).display")=='none','clicking it hides the Engineering data panel completely')
        chk(not await pg.evaluate("()=>document.querySelector('[data-a=engtog]').classList.contains('tgon')"),'button un-highlights once hidden')
        chk(await pg.evaluate("()=>document.querySelector('[data-a=engtog]').textContent")=='Show Engineering Data','button reads Show Engineering Data once hidden')

        await pg.reload();await pg.wait_for_timeout(1000)
        chk(await pg.evaluate("()=>S.font")=='OpenDyslexic','font choice is saved and restored after reload')
        chk(await pg.evaluate("()=>getComputedStyle(document.getElementById('right')).display")=='none','hidden Engineering data panel stays hidden after reload')
        await pg.close()

        # --- mobile: Engineering data button hidden, panel not clipped when opened ---
        pg2=await b.new_page(viewport={'width':420,'height':850})
        errs2=[];pg2.on('pageerror',lambda e:errs2.append(str(e)))
        await pg2.goto('file:///home/claude/tilesmith-desktop/app/index.html');await pg2.evaluate("()=>localStorage.clear()");await pg2.reload();await pg2.wait_for_timeout(1000)
        chk(await pg2.evaluate("()=>getComputedStyle(document.querySelector('[data-a=engtog]')).display")=='none','Engineering data button is hidden on mobile (the accordion caret does its job)')

        await pg2.click('#engD summary');await pg2.wait_for_timeout(300)
        dims=await pg2.evaluate("""()=>{const e=document.getElementById('right');const b=e.getBoundingClientRect();return {h:b.height,scrollH:e.scrollHeight}}""")
        chk(abs(dims['h']-dims['scrollH'])<2,f'opened Engineering data is not clipped to a short scrollable box {dims}')
        left=await pg2.eval_on_selector('#left',"e=>({h:e.getBoundingClientRect().height,scrollH:e.scrollHeight})")
        chk(abs(left['h']-left['scrollH'])<2,f'settings panel sizes to its own content, no leftover blank space {left}')
        await pg2.close()

        chk(not errs and not errs2,f'no page errors {errs[:3]}{errs2[:3]}')
        await b.close();print('ALL OK' if ok else 'FAILED');sys.exit(0 if ok else 1)
asyncio.run(m())
