# Report a bug / feedback: button sits bottom-right of the bar next to Info, captures a
# screenshot, lets the user mark it up, downloads the PNG and opens a pre-filled mailto: email.
import asyncio, sys
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        pg=await b.new_page(viewport={'width':1400,'height':900},permissions=['camera'])
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html');await pg.evaluate("()=>localStorage.clear()");await pg.reload();await pg.wait_for_timeout(900)
        ok=True
        def chk(c,msg):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ')+msg);ok=ok and c
        bar=await pg.eval_on_selector('#bar',"e=>e.getBoundingClientRect()")
        about=await pg.eval_on_selector('[data-a=about]',"e=>e.getBoundingClientRect()")
        bug=await pg.eval_on_selector('[data-a=bugrpt]',"e=>e.getBoundingClientRect()")
        chk(bug['right']>bar['right']-20,f"button sits at the right edge of the bar {bug} vs bar {bar}")
        chk(bug['right']>about['right'] and abs(bug['top']-about['top'])<2,f'Report a bug / feedback sits next to Info, same row {about} {bug}')
        chk(await pg.evaluate("()=>document.querySelector('[data-a=bugrpt]').textContent")=='Report a bug / feedback','button label')
        vp=await pg.eval_on_selector('#vp',"e=>e.getBoundingClientRect()")
        chk(bar['bottom']<=vp['top']+1,'button bar (and so the new button) sits above the viewport')
        # open it
        await pg.click('[data-a=bugrpt]');await pg.wait_for_timeout(700)
        chk(await pg.evaluate("()=>document.getElementById('bugrpt').classList.contains('on')"),'dialog opens on click')
        dims=await pg.evaluate("()=>({w:document.getElementById('bugCv').width,h:document.getElementById('bugCv').height})")
        chk(dims['w']>0 and dims['h']>0,f'a screenshot is captured into the canvas {dims}')
        # draw a stroke (markup)
        box=await pg.eval_on_selector('#bugCv',"e=>e.getBoundingClientRect()")
        cx,cy=box['x']+box['width']/2,box['y']+box['height']/2
        await pg.mouse.move(cx-40,cy-20);await pg.mouse.down();await pg.mouse.move(cx+40,cy+20,steps=5);await pg.mouse.up();await pg.wait_for_timeout(200)
        chk(await pg.evaluate("()=>bugStrokes.length")==1,'a markup stroke is recorded')
        await pg.click('#bugUndo');await pg.wait_for_timeout(100)
        chk(await pg.evaluate("()=>bugStrokes.length")==0,'Undo removes the stroke')
        await pg.mouse.move(cx-40,cy-20);await pg.mouse.down();await pg.mouse.move(cx+40,cy+20,steps=5);await pg.mouse.up();await pg.wait_for_timeout(200)
        await pg.click('#bugClear');await pg.wait_for_timeout(100)
        chk(await pg.evaluate("()=>bugStrokes.length")==0,'Clear markup removes all strokes')
        await pg.fill('#bugDesc','Test bug: the viewport flickers when zooming.')
        # send: download + mailto, dialog closes
        async with pg.expect_download() as dli:
            await pg.click('#bugSend')
        dl=await dli.value
        chk(dl.suggested_filename.startswith('tilesmith-bugreport-') and dl.suggested_filename.endswith('.png'),f'downloads a PNG named for the report {dl.suggested_filename}')
        await pg.wait_for_timeout(300)
        chk(not await pg.evaluate("()=>document.getElementById('bugrpt').classList.contains('on')"),'dialog closes after sending')
        # Escape also closes it
        await pg.click('[data-a=bugrpt]');await pg.wait_for_timeout(700)
        await pg.keyboard.press('Escape');await pg.wait_for_timeout(100)
        chk(not await pg.evaluate("()=>document.getElementById('bugrpt').classList.contains('on')"),'Escape closes the dialog')
        chk(not errs,f'no page errors {errs[:3]}')
        await b.close();print('ALL OK' if ok else 'FAILED');sys.exit(0 if ok else 1)
asyncio.run(m())
