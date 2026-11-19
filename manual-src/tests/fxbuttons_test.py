"""Effect buttons and LED build on restart: the Start LED Build, Start DVD Screensaver and Start Tile Faults
buttons light up while their effect is on; the LED build comes back on after a restart only if it was on when
the app closed (also with Loop build on); a first start has it off. Prints ALL OK."""
import asyncio, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('TILESMITH_ROOT') or os.path.dirname(os.path.dirname(HERE))
APP = 'file://' + os.path.join(ROOT, 'tilesmith-desktop', 'app', 'index.html')
SHOT = os.environ.get('SHOT')
async def main():
    ok = True; r = None
    def chk(c, name=''):
        nonlocal ok
        if not c: print('FAILED', name, r)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {})); pg = await b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = pg.evaluate
        st = lambda: ev("""()=>{const l=a=>document.querySelector('#bar [data-a='+a+']').classList.contains('live');
          return{bld:barBuilding(),act:bldActive(),lb:l('bldgo'),ld:l('dvdgo'),lg:l('glgo'),lgp:document.querySelector('#glBox [data-a=glgo]').classList.contains('live'),
          txt:document.querySelector('#bar [data-a=bldgo]').textContent,key:localStorage.getItem('tilesmith-build-on')}}""")
        bar = lambda a: pg.click('#bar [data-a=' + a + ']')
        r = await st(); print('FIRST START', r)
        chk(not r['bld'] and not r['lb'] and not r['ld'] and not r['lg'], 'first start: nothing on, nothing lit')
        await bar('bldgo'); await pg.wait_for_timeout(400); r = await st()
        chk(r['bld'] and r['lb'] and r['txt'] == 'Stop LED Build' and r['key'] == '1', 'build on: button lit, saved on')
        await ev("()=>{const e=document.querySelector('[data-k=glPick]');e.value='Random';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
        await bar('dvdgo'); await bar('glgo'); await pg.wait_for_timeout(400); r = await st()
        chk(r['ld'] and r['lg'] and r['lgp'], 'DVD and tile faults buttons lit')
        if SHOT: await pg.screenshot(path=SHOT, clip={'x': 0, 'y': 0, 'width': 1500, 'height': 120})
        await bar('dvdgo'); await bar('glgo'); await pg.wait_for_timeout(400); r = await st()
        chk(not r['ld'] and not r['lg'] and not r['lgp'], 'DVD and tile faults buttons unlit when stopped')
        # closed while building: the build starts again
        await pg.reload(); await pg.wait_for_timeout(800); r = await st(); print('RESTART WHILE ON', r)
        chk(r['bld'] and r['lb'], 'restart: build comes back on')
        await bar('bldgo'); await pg.wait_for_timeout(400); r = await st()
        chk(not r['bld'] and not r['lb'] and r['key'] == '0', 'stopped: unlit, saved off')
        # closed while stopped, with Loop build on: stays off (the loop used to restart it)
        await ev("()=>{S.loop=true;S.loopHold=1;saveNow()}")
        await pg.reload(); await pg.wait_for_timeout(3000); r = await st(); print('RESTART WHILE OFF, LOOP ON', r)
        chk(not r['bld'] and not r['act'] and not r['lb'], 'restart with loop on: build stays off')
        # a looped build stays on in the pause between rounds, and after a restart
        await bar('bldgo'); await pg.wait_for_timeout(300); await ev("()=>{eachCv(()=>showAll())}"); await pg.wait_for_timeout(300); r = await st()
        chk(not r['bld'] and r['act'] and r['lb'] and r['txt'] == 'Stop LED Build' and r['key'] == '1', 'loop pause: still on and lit')
        await pg.wait_for_timeout(1500); r = await st(); chk(r['bld'], 'loop restarts the build')
        await pg.reload(); await pg.wait_for_timeout(800); r = await st(); chk(r['bld'] and r['lb'], 'restart: looped build comes back on')
        await bar('bldgo'); await pg.wait_for_timeout(2500); r = await st()
        chk(not r['bld'] and not r['act'] and r['key'] == '0', 'Stop during a looped build turns it off')
        chk(not errs, 'no page errors: ' + '; '.join(errs[:3]))
        await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
