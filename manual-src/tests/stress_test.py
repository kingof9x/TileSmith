"""Stress and abuse tests for review: what a damaged or hostile project file can do, and how the app scales.
  1. HTML in every text field of a project (wall, canvas, location, distro names...) is shown as text, never run.
     The desktop page has Node.js access, so script in a project file would reach the computer.
  2. Pictures in a project that point at web or file addresses are ignored: opening a project makes no requests.
  3. 150 damaged projects (random fields set to wrong types and extreme values, fixed seed): opening and using each one
     (panels, render, data and power plans, spec sheet, labels, undo) throws nothing.
  4. Timings of the hot paths from a default wall up to ten 64 x 64-tile walls (printed, not judged: they depend on the
     machine; headless Chromium draws on the CPU).
Prints ALL OK when 1 to 3 pass."""
import asyncio, json, random, sys
from _paths import TS_APP_URL
from playwright.async_api import async_playwright
PAY = '<img src=x onerror="window.__x=(window.__x||[]).concat(\'K\')">'
BUSY = """()=>{S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.pmode='Snake';S.wred='Loop';storeWall();try{distAct('dadd')}catch(e){}
  S.cabOn=true;S.rigOn=true;S.lbl=true;storeWall();addWall(true);S.half=[[0,0,'right']];S.gone=[[1,1]];storeWall();try{zAdd()}catch(e){};sync();const o=stateObj();o.rc=rcForProject();return o}"""
USE = """o=>{const E=[];const t=(n,f)=>{try{f()}catch(e){E.push(n+': '+e.message.slice(0,120))}};
  t('open',()=>openProject(o,'f'));document.querySelectorAll('details').forEach(d=>d.open=true);
  for(let i=0;i<walls.length;i++)t('select',()=>selWall(i));t('render',()=>{forceRen=true;render()});t('viewport',()=>vpDraw());
  t('plans',()=>{portPlan();powerPlan()});t('spec',()=>specSections());t('labels',()=>labelsHTML());t('info',()=>info());t('undo',()=>unUndo(1));
  const ts=document.querySelector('#toast').textContent;if(/Could not open/.test(ts))E.push('toast: '+ts.slice(0,120));return E}"""
async def main():
    ok = True
    def chk(c, m):
        nonlocal ok; print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []; reqs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.on('request', lambda r: reqs.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:')) else None)
        async def fresh():
            await pg.goto(TS_APP_URL); await pg.evaluate("()=>{window.__noSave=true;localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(700)
        # 1. HTML in every text field
        await fresh(); base = await pg.evaluate(BUSY)
        def poison(v, path):
            if isinstance(v, str): return v if v.startswith('data:') else PAY.replace('K', path[-50:].replace("'", ''))
            if isinstance(v, list): return [poison(x, f'{path}[{i}]') for i, x in enumerate(v)]
            if isinstance(v, dict): return {k: poison(x, path + '.' + k) for k, x in v.items()}
            return v
        o = poison(base, ''); o['S']['proc'] = base['S']['proc']
        e = await pg.evaluate(USE, o)
        await pg.evaluate("""()=>{for(const f of ['specSections','labelsHTML','pullPages','binderFront','zoneMapPages','cabRows','wallRows']){try{const r=window[f]&&window[f](walls[0]);
          if(typeof r=='string'){const d=document.createElement('div');d.innerHTML=r;document.body.appendChild(d)}}catch(e){}}}""")
        await pg.wait_for_timeout(600)
        st = await pg.evaluate("()=>({ran:window.__x||[],name:walls[0].name.slice(0,5),shown:(document.body.innerHTML.match(/&lt;img src=x/g)||[]).length})")
        chk(not st['ran'] and st['name'] == '<img ' and st['shown'] > 50, f"HTML in project text is shown as text, never run ({st['shown']} places shown, ran from {st['ran']})")
        # 2. outside pictures
        await fresh(); reqs.clear()
        r = await pg.evaluate("""async()=>{const o=stateObj();o.logo='https://example.invalid/pixel.png';o.dvd='file:///etc/hosts';o.walls[0].patImg='http://example.invalid/p.png';
          o.walls[0].boxImg=M.toDataURL('image/png');openProject(o,'x');await new Promise(r=>setTimeout(r,800));forceRen=true;render();let read=true;try{mc.getImageData(0,0,2,2)}catch(e){read=false}
          return{logo:!!logoImg,dvd:!!dvdImg,pat:!!walls[0].patImg,box:!!walls[0].boxImg,read}}""")
        chk(r == {'logo': False, 'dvd': False, 'pat': False, 'box': True, 'read': True} and not reqs, f'only embedded pictures load, no requests {r} {reqs}')
        # 3. damaged projects
        await fresh(); base = await pg.evaluate(BUSY); rnd = random.Random(7)
        BAD = [None, -1, 0, 1e9, -1e9, 'x', '', [], {}, [None], [[1e9, 1e9]], [['a', 'b']], {'a': 1}, True, 0.5, [[0, 0, 'right']]]
        def paths(v, p=()):
            yield p
            if isinstance(v, dict):
                for k, x in v.items(): yield from paths(x, p + (k,))
            elif isinstance(v, list):
                for i, x in enumerate(v[:6]): yield from paths(x, p + (i,))
        P = [q for q in paths(base) if q and q[0] not in ('ut', 'rc')]; found = {}
        for it in range(150):
            o = json.loads(json.dumps(base)); muts = []
            for _ in range(rnd.randint(1, 8)):
                q = rnd.choice(P); v = rnd.choice(BAD); t = o
                try:
                    for k in q[:-1]: t = t[k]
                    t[q[-1]] = v; muts.append(('.'.join(map(str, q)), v))
                except Exception: pass
            errs.clear(); E = await pg.evaluate(USE, o); await pg.wait_for_timeout(20)
            for x in E + errs: found.setdefault(x[:100], muts)
            await pg.evaluate("o=>{try{openProject(o,'base')}catch(e){}}", base)
        for k, m in list(found.items())[:10]: print('   ', k, '<-', m)
        chk(not found, f'150 damaged projects open and work without errors ({len(found)} distinct errors)')
        # 4. timings
        await fresh()
        await pg.evaluate("""()=>{window.TM=(f,n)=>{const t=[];for(let i=0;i<n;i++){const a=performance.now();f();t.push(performance.now()-a)}t.sort((a,b)=>a-b);return Math.round(t[t.length>>1])}}""")
        for name, setup in [('default wall', ''), ('one 64x64 wall, wired, 4K', "S.cw=3840;S.ch=2160;S.cols=64;S.rows=64;S.tw=60;S.th=33;S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.pmode='Snake';storeWall();try{distAct('dadd')}catch(e){}"),
                            ('ten 64x64 walls', "for(let i=0;i<9;i++){addWall(false);S.cols=64;S.rows=64;S.tw=20;S.th=20;storeWall()}")]:
            r = await pg.evaluate("s=>{(new Function(s))();sync();S.play=false;return{tiles:walls.reduce((a,w)=>a+wst(w).N,0),render_ms:TM(()=>{forceRen=true;render()},5),sync_ms:TM(()=>sync(),5),save_ms:TM(()=>saveNow(),5),undo_snapshot_ms:TM(()=>unKey(unSnap()),5),state_kb:Math.round(JSON.stringify(stateObj()).length/1024)}}", setup)
            print('    timing', name.ljust(26), r)
        chk(not errs, f'no page errors {errs[:3]}')
        await b.close()
    print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
