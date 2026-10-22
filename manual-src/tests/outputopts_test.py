# Output options: its own section after Animation Options with display takeover first, then NDI and Spout/Syphon;
# one button per extra display with a canvas picker (displays simulated here, the test browser has one screen).
import asyncio, sys
from playwright.async_api import async_playwright
FAKE="""()=>{window.__outTest=true;DISP=dispSort([{id:'a',label:'Built-in',bounds:{x:0,y:0,width:1440,height:900},px:[2880,1800],scale:2,main:true,primary:true},
 {id:'b',label:'LED processor',bounds:{x:1440,y:0,width:1920,height:1080},px:[1920,1080],scale:1,main:false,primary:false},
 {id:'c',label:'Confidence monitor',bounds:{x:3360,y:0,width:1920,height:1080},px:[1920,1080],scale:1,main:false,primary:false},
 {id:'d',label:'Side screen',bounds:{x:5280,y:0,width:1280,height:720},px:[1280,720],scale:1,main:false,primary:false}]);SD={};outUI()}"""
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1500,'height':1100})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html');await pg.evaluate("()=>localStorage.clear()");await pg.reload();await pg.wait_for_timeout(900)
        sec=pg.locator("xpath=//aside[@id='left']/details[summary[normalize-space(.)='Output options']]")
        ok=True
        def chk(c,m):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ')+m);ok=ok and c
        tops=await pg.evaluate("()=>[...document.querySelectorAll('#left > details > summary')].map(s=>s.textContent.trim())")
        chk(tops[:5]==['Canvases','Engineering','Animation Options','Output options','Label printing options'],f'sections {tops}')
        subs=await pg.evaluate("()=>{const d=[...document.querySelectorAll('#left > details')].find(x=>x.querySelector('summary').textContent.trim()=='Output options');return [d.querySelector('.sec').firstElementChild.id,...[...d.querySelectorAll('.sec details>summary')].map(s=>s.textContent.trim())]}")
        chk(subs[0]=='dispBox' and subs[1].startswith('NDI') and 'Spout' in subs[2],f'takeover first, then NDI and Spout/Syphon {subs}')
        anim=await pg.evaluate("()=>{const d=[...document.querySelectorAll('#left > details')].find(x=>x.querySelector('summary').textContent.trim()=='Animation Options');return [...d.querySelectorAll('summary')].map(s=>s.textContent.trim())}")
        chk(not any(a.startswith('NDI') or 'Spout' in a for a in anim),'NDI and Spout/Syphon no longer in Animation Options')
        chk(await pg.evaluate("()=>!!document.querySelector('[data-a=dispfind]')||/desktop app/.test(document.getElementById('dispNote').textContent)"),'without displays it offers Find displays or explains what is needed')
        await pg.evaluate("()=>{const d=[...document.querySelectorAll('#left > details')].find(x=>x.querySelector('summary').textContent.trim()=='Output options');d.open=true;d.querySelectorAll('details').forEach(x=>x.open=true)}")
        await pg.wait_for_timeout(300);pass
        # with three extra displays and two canvases (simulated, since this test browser has one screen)
        await pg.evaluate("()=>{cvAdd(false);switchTo(0)}");await pg.evaluate(FAKE);await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{const d=[...document.querySelectorAll('#left > details')].find(x=>x.querySelector('summary').textContent.trim()=='Output options');d.open=true;d.querySelectorAll('details').forEach(x=>x.open=true)}")
        pass
        # take over display 3 with canvas 2
        await pg.select_option('[data-dispcv="c"]',await pg.evaluate("()=>String(CVS[1].id)"))
        async with pg.expect_popup() as pi:
            await pg.click('[data-a=dispon][data-v="c"]')
        pop=await pi.value;await pg.wait_for_timeout(900)
        pass
        btns=await pg.evaluate("()=>[...document.querySelectorAll('#dispRows button')].map(b=>b.textContent)")
        chk(btns==['Take over Display 2','Release Display 3','Take over Display 4'],f'one button per extra display {btns}')
        outs=await pg.evaluate("()=>[...OUTW].map(([c,o])=>c.name+' -> '+o.d.label)")
        chk(outs==['Canvas 2 -> Confidence monitor'],f'chosen canvas goes to the chosen display {outs}')
        pc=await pop.evaluate("()=>{const c=document.querySelector('canvas');return [c.width,c.height]}")
        chk(pc==[1920,1080],f'output draws the canvas pixel for pixel {pc}')
        chk(await pg.evaluate("()=>document.getElementById('outSel').value=='' && CVS[cc].name=='Canvas 1'"),'Canvases menu shows Canvas 1 is not on a display')
        pass
        await pg.click('[data-a=dispoff][data-v="c"]');await pg.wait_for_timeout(300)
        chk(await pg.evaluate("()=>OUTW.size")==0,'Release closes the output')
        chk(not errs,f'no page errors {errs[:3]}')
        await b.close();print('ALL OK' if ok else 'FAILED');sys.exit(0 if ok else 1)
asyncio.run(m())
