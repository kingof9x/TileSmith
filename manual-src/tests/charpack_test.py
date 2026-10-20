# Character packs: load a zip of part images, it is stored, used by the technician through a whole build, saved in projects and per crew member.
import asyncio, sys, os, json, base64
from playwright.async_api import async_playwright
APP = '/home/claude/tilesmith-desktop/app/index.html'
ZIP = os.environ.get('PACKZIP', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TestTech.zip'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APP); await pg.evaluate("()=>{localStorage.clear();indexedDB.deleteDatabase('tilesmith-packs')}"); await pg.reload(); await pg.wait_for_timeout(800)
        ok = True
        def chk(c, m):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ') + m); ok = ok and c
        chk('Character pack' in await pg.evaluate("()=>[...document.querySelector('[data-k=tstyle]').options].map(o=>o.value)"), 'style list has Character pack')
        await pg.evaluate("()=>{const e=document.querySelector('[data-k=tstyle]');e.value='Character pack';e.dispatchEvent(new Event('input',{bubbles:true}))}")
        chk(await pg.evaluate("()=>getComputedStyle(document.getElementById('pkBox')).display!='none'"), 'pack controls show for Character pack')
        await pg.set_input_files('#pkf', ZIP); await pg.wait_for_timeout(1500)
        info = await pg.evaluate("()=>{const r=PK.get(S.tpack);return r?{name:r.name,n:Object.keys(r.files).length,views:[...new Set(Object.keys(r.files).map(k=>k.split('/')[0]))]}:null}")
        chk(info and info['n'] == 51 and len(info['views']) == 4, f'zip loaded: {info}')
        chk(info and info['name'] == 'Test tech', 'name taken from pack.json')
        chk(await pg.evaluate("()=>document.getElementById('pkSel').value==S.tpack"), 'pack selected in the menu')
        # whole build with the pack, every phase drawn
        await pg.evaluate("()=>{S.cols=4;S.rows=3;storeWall();showAll();sync();fit();reset();S.play=true}")
        seen = set()
        for i in range(60):
            await pg.evaluate("()=>{for(let k=0;k<20;k++)step(1/60);forceRen=true}"); await pg.wait_for_timeout(25); seen.add(await pg.evaluate("()=>sims[0].ph"))
        chk(len(seen) >= 4, f'build phases ran with the pack {sorted(seen)}')
        used = await pg.evaluate("()=>{let n=0;const o=workerPack;window.workerPack=function(){n++;return o.apply(this,arguments)};drawTech(document.createElement('canvas').getContext('2d'),100,100,100,{th:1,mv:0,m:crew[0],ix:0,hands:null});return n}")
        chk(used == 1, 'technician is drawn from the pack')
        # stored on the device
        await pg.reload(); await pg.wait_for_timeout(1500)
        chk(await pg.evaluate("()=>PK.size==1&&S.tstyle=='Character pack'&&PK.has(S.tpack)"), 'pack kept on the device after reload')
        # per crew member
        await pg.evaluate("()=>{S.cd=true;sync();crewUI()}")
        chk(await pg.evaluate("()=>document.querySelectorAll('#crew select[data-f=\"4\"]').length==crew.length"), 'each crew member has a pack picker')
        await pg.evaluate("()=>{S.tstyle='Classic';sync();const s=document.querySelector('#crew select[data-f=\"4\"]');s.value=S.tpack;s.dispatchEvent(new Event('input',{bubbles:true}))}")
        chk(await pg.evaluate("()=>pkFor(crew[0])==S.tpack&&pkFor(crew[1])==''"), 'pack per crew member while the style is Classic')
        # saved in a project and brought back on a clean device
        proj = await pg.evaluate("()=>{const o=stateObj();o.rc=rcForProject();o.pk=pkForProject();return JSON.stringify(o)}")
        chk('"pk"' in proj and len(json.loads(proj)['pk']) == 1, 'project carries the pack')
        await pg.evaluate("()=>{indexedDB.deleteDatabase('tilesmith-packs');localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(1000)
        chk(await pg.evaluate("()=>PK.size") == 0, 'clean device has no packs')
        await pg.evaluate("(s)=>applyState(JSON.parse(s))", proj); await pg.wait_for_timeout(500)
        chk(await pg.evaluate("()=>PK.size==1&&pkFor(crew[0])!=''"), 'opening the project adds the pack and the crew assignment')
        # loose PNG files with view prefixes work too
        files = await pg.evaluate("()=>[...PK.values()][0].files")
        os.makedirs('/tmp/tech/loose', exist_ok=True); paths = []
        for k, v in list(files.items())[:20]:
            fn = '/tmp/tech/loose/' + k.replace('/', '_') + '.png'; open(fn, 'wb').write(base64.b64decode(v.split(',', 1)[1])); paths.append(fn)
        await pg.set_input_files('#pkf', paths); await pg.wait_for_timeout(1200)
        chk(await pg.evaluate("()=>PK.size==2&&Object.keys(PK.get(S.tpack).files).length==20"), 'loose PNG files load as a pack')
        await pg.evaluate("()=>pkDel()")
        chk(await pg.evaluate("()=>PK.size==1"), 'delete pack removes it')
        chk(not errs, f'no page errors {errs[:3]}')
        await b.close(); print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
