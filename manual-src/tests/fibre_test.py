# Fibre and breakout boxes (Engineering › Cable lengths): Auto by the copper limit, per-wall Fibre / Copper override
import asyncio, json, os
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
SHOT = os.environ.get('FIBRE_SHOT')
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # two walls: Main 40 m away stays copper, Delay 120 m away goes over fibre on Auto
        r = await pg.evaluate("""()=>{S.cols=12;S.rows=8;S.name='Main';storeWall();S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.ret=false;S.cabOn=true;S.cdD=40;S.cslack=10;storeWall();
          addWall(false);S.name='Delay';S.cols=8;S.rows=6;S.cdD=120;storeWall();sync();const R=cabRuns(),pl=portPlan();
          return{fib:R.fib.map(x=>({wi:x.wi,ports:x.ports,boxes:x.boxes,trunks:x.trunks,m:x.m,cab:x.cab})),ports:pl.map(x=>x.length),tails:R.filter(x=>x.fib).map(x=>[x.id,x.m,x.cab]),
           rows:cabRows(R),w0:cabWallRows(R,0),w1:cabWallRows(R,1),pull:pullItems().find(d=>d[0]=='Data'),over:cabRows(R).some(x=>x[0]=='Over 100 m')}}""")
        print(json.dumps(r, indent=1)[:3000])
        n1 = r['ports'][1]
        ok &= len(r['fib']) == 1 and r['fib'][0]['wi'] == 1 and r['fib'][0]['ports'] == n1 and r['fib'][0]['boxes'] == -(-n1 // 10)
        ok &= r['fib'][0]['trunks'] == -(-r['fib'][0]['boxes'] // 2) and abs(r['fib'][0]['m'] - 132) < 1e-9 and r['fib'][0]['cab'] == [150]
        ok &= len(r['tails']) == n1 and all(t[1] < 10 and len(t[2]) == 1 for t in r['tails']) and not r['over']
        ok &= r['w0'][1][1].startswith('Copper') and r['w1'][1][1].startswith('Fibre (longest copper run')
        names = [x[0] for x in r['pull'][1]]
        ok &= 'Fibre breakout box, 10 ports' in names and 'Fibre converter at the processor, 10 ports' in names and 'opticalCON QUAD fibre 150 m' in names and any(x.startswith('etherCON tail') for x in names)
        # processor with fibre outputs: no converters; DUO trunks: one per box; 4-port boxes
        r = await pg.evaluate("()=>{S.fibNat=true;S.fibTr='opticalCON DUO';S.fibBox=4;sync();const R=cabRuns(),f=R.fib[0];return{boxes:f.boxes,trunks:f.trunks,ports:f.ports,pull:pullItems().find(d=>d[0]=='Data')[1].map(x=>x[0])}}")
        print('duo', r); ok &= r['boxes'] == -(-r['ports'] // 4) and r['trunks'] == r['boxes'] and not any('converter' in x for x in r['pull'])
        # overrides: Main forced to fibre, Delay forced to copper (then the 100 m warning comes back)
        r = await pg.evaluate("""()=>{S.fibNat=false;S.fibTr='opticalCON QUAD';S.fibBox=10;storeWall();selWall(0);S.wfib='Fibre';storeWall();selWall(1);S.wfib='Copper';storeWall();sync();const R=cabRuns();
          return{fib:R.fib.map(x=>x.wi),w0:cabWallRows(R,0)[1],w1:cabWallRows(R,1)[1],over:cabRows(R).filter(x=>x[0]=='Over 100 m')}}""")
        print('override', r); ok &= r['fib'] == [0] and r['w0'][1] == 'Fibre (set by hand)' and 'set by hand' in r['w1'][1] and len(r['over']) == 1
        # the copper limit: raise it above the Delay run and Auto keeps it on copper
        r = await pg.evaluate("()=>{S.wfib='Auto';storeWall();selWall(0);S.wfib='Auto';storeWall();S.fibLim=200;sync();const a=cabRuns().fib.length;S.fibLim=90;sync();return{a,b:cabRuns().fib.length}}")
        print('limit', r); ok &= r == {'a': 0, 'b': 1}
        # feet: the limit and default fibre lists convert; switching back restores them
        r = await pg.evaluate("""()=>{const sel=document.querySelector('select[data-k=cunit]');sel.value='ft';sel.dispatchEvent(new Event('input',{bubbles:true}));const a={lim:S.fibLim,len:S.fibLen,tail:S.fibTail,n:cabRuns().fib.length};
          sel.value='m';sel.dispatchEvent(new Event('input',{bubbles:true}));return{a,b:{lim:S.fibLim,len:S.fibLen,tail:S.fibTail}}}""")
        print('ft', r); ok &= r['a']['lim'] == 295 and r['a']['len'].startswith('150') and r['a']['n'] == 1 and r['b'] == {'lim': 90, 'len': '50, 100, 150, 300', 'tail': '1, 3, 5, 10'}
        # saved and opened again keeps the per-wall choice; an old project opens on Auto
        r = await pg.evaluate("""()=>{selWall(1);S.wfib='Copper';storeWall();const o=JSON.parse(JSON.stringify(stateObj()));applyCore(o);sync();const a=walls.map(w=>w.wfib);
          const o2=JSON.parse(JSON.stringify(stateObj()));o2.walls.forEach(w=>delete w.wfib);S.wfib='Auto';['wfib','fibLim','fibBox','fibNat','fibTr','fibLen','fibTail'].forEach(k=>delete o2.S[k]);applyCore(o2);sync();return{a,b:walls.map(w=>w.wfib),lim:S.fibLim}}""")
        print('save', r); ok &= r['a'] == ['Auto', 'Copper'] and r['b'] == ['Auto', 'Auto']
        # the panel shows the fibre settings; the canvas draws with fibre on
        await pg.evaluate("()=>{selWall(1);S.wfib='Auto';storeWall();S.showData=true;sync()}"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("()=>({sel:!!document.querySelector('select[data-k=wfib]'),vis:document.querySelector('select[data-k=wfib]').offsetParent!==null,eng:document.querySelector('#right').innerText.includes('Fibre breakout boxes')})")
        print('ui', r); ok &= r['sel'] and r['eng']
        if SHOT:
            await pg.evaluate("()=>{const e=document.querySelector('select[data-k=wfib]');e.closest('details')&&(e.closest('details').open=true);e.scrollIntoView({block:'center'})}"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=SHOT)
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
