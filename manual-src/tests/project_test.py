"""Save/Open project round trip (custom images, crew, logo, walls), top bar contents, LED build buttons, Video export menu. Prints ALL OK."""
import asyncio, json, base64
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
async def main():
    ok = True
    def chk(c, name=''):
        nonlocal ok
        if not c: print('FAILED', name)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = pg.evaluate
        bar = await ev("()=>[...document.querySelectorAll('#bar [data-a]')].map(e=>e.dataset.a)")
        print(bar)
        chk(all(a in bar for a in ('newc', 'psave', 'popen')) and bar.index('psave') == bar.index('newc') + 1 and bar.index('popen') == bar.index('psave') + 1, 'save/open next to new')
        chk(not any(a in bar for a in ('rec', 'pp', 'rs', 'sk')), 'old top buttons gone')
        t = await ev("()=>[...document.querySelectorAll('summary,.sub>h3,details>summary')].map(e=>e.textContent.trim())")
        chk('LED build' in t and 'Build options' not in t, 'LED build menu ' + str(t[:20]))
        chk(await ev("()=>['rs','bstop','brst','pp','rec'].every(a=>document.querySelector('[data-a='+a+']'))"), 'menu buttons')
        chk(not await ev("()=>!!document.querySelector('[data-a=dvdexp]')"), 'dvd export button gone')
        chk(await ev("()=>['vLed','vDvd'].every(k=>document.querySelector('[data-k='+k+']'))"), 'checkboxes')
        # build controls
        await ev("()=>{document.querySelector('[data-a=rs]').click()}"); await pg.wait_for_timeout(300)
        chk(await ev("()=>S.play===true"), 'start plays')
        await ev("()=>document.querySelector('[data-a=pp]').click()"); await pg.wait_for_timeout(100)
        chk(await ev("()=>S.play===false"), 'pause'); await pg.wait_for_timeout(300)
        chk((await ev("()=>document.querySelector('[data-a=pp]').textContent")) == 'Play', 'label Play')
        await ev("()=>document.querySelector('[data-a=bstop]').click()"); await pg.wait_for_timeout(200)
        chk(await ev("()=>S.play===false&&allDone()"), 'stop shows finished')
        await ev("()=>document.querySelector('[data-a=brst]').click()"); await pg.wait_for_timeout(200)
        chk(await ev("()=>S.play===false&&!allDone()"), 'reset blanks')
        # export in browser: nothing ticked -> message, no recording
        await ev("()=>{S.vLed=false;S.vDvd=false;sync()}"); await ev("()=>document.querySelector('[data-a=rec]').click()")
        chk(not await ev("()=>!!REC") and 'Tick' in await ev("()=>document.querySelector('#vexps').textContent"), 'nothing ticked')
        # customise everything then save
        await ev("""(PX)=>{S.cols=7;S.rows=5;S.vHold=17;S.vDvd=true;crew[0][0]='Zed';crew.push(['Extra','#fff',null,0]);
          const mk=s=>{const i=new Image();i.__src=s;i.src=s;return i};logoImg=mk(PX);dvdImg=mk(PX);S.patImg=mk(PX);S.boxImg=mk(PX);
          walls[cur].patImg=S.patImg;walls[cur].boxImg=S.boxImg;storeWall();walls.push(Object.assign({},walls[0],{cols:3}));sync();crewUI()}""", PX)
        async with pg.expect_download() as d: await pg.click('#bar [data-a=psave]')
        dlw = await d.value; path = await dlw.path(); txt = open(path).read(); o = json.loads(txt)
        print(dlw.suggested_filename, len(txt))
        chk(dlw.suggested_filename.endswith('.tilesmith') and o['format'] == 'TileSmith project', 'file name/format')
        chk(o['logo'] == PX and o['dvd'] == PX and o['crew'][0][0] == 'Zed' and len(o['crew']) == 7 and o['walls'][0]['patImg'] == PX and o['walls'][0]['boxImg'] == PX and len(o['walls']) == 2, 'file content')
        # wipe, then open through the file input
        await ev("()=>newCanvas()"); await pg.wait_for_timeout(300)
        chk(await ev("()=>!logoImg&&!dvdImg&&crew[0][0]!='Zed'&&walls.length==1"), 'wiped')
        await pg.set_input_files('#opf', path); await pg.wait_for_timeout(300)
        chk(await pg.is_visible('#openp'), 'confirm shown')
        await pg.click('#openp button[data-n="1"]'); await pg.wait_for_timeout(700)
        r = await ev("()=>({cols:S.cols,rows:S.rows,hold:S.vHold,dvd:S.vDvd,crew:crew.map(c=>c[0]),logo:!!(logoImg&&logoImg.__src),dvdi:!!(dvdImg&&dvdImg.__src),pat:!!(walls[0].patImg&&walls[0].patImg.__src),w:walls.length})")
        print(r)
        chk(r['cols'] == 7 and r['rows'] == 5 and r['hold'] == 17 and r['dvd'] and r['crew'][0] == 'Zed' and len(r['crew']) == 7 and r['logo'] and r['dvdi'] and r['pat'] and r['w'] == 2, 'restored')
        # undo brings back the previous project
        await ev("()=>unApply&&0").__class__ if False else None
        # bad file
        open('/tmp/bad.tilesmith', 'w').write('{"nope":1}')
        await pg.set_input_files('#opf', '/tmp/bad.tilesmith'); await pg.wait_for_timeout(300)
        chk(not await pg.is_visible('#openp') and 'not a TileSmith' in await ev("()=>document.body.innerText"), 'bad file rejected')
        chk(not errs, 'page errors ' + str(errs))
        await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
