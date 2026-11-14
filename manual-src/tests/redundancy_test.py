# Redundancy (Engineering › LED processor): per-wall method, priority, gear on hand with step-down, port map, signal path
import asyncio, json, os
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
SHOT = os.environ.get('RED_SHOT')
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1100}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        P = "()=>{const R=redPlan();return{main:R.main,back:R.back,spare:R.spare,loops:R.loops,backs:R.backs,short:R.shortP,got:R.got,why:R.why,P:R.P}}"
        # two walls, 11 primary ports on 10-port processors; default Loop everywhere (matches the old Return lines default)
        r = await pg.evaluate("""()=>{S.cols=12;S.rows=8;S.name='Main';storeWall();S.proc='NovaStar VX1000 Pro';applySpec();S.pports=10;S.wmode='Snake';storeWall();
          addWall(false);S.name='Side';S.cols=8;S.rows=6;S.wmode='Snake';storeWall();sync();return portPlan().map(x=>x.length)}""")
        print('ports', r); n0, n1 = r
        r = await pg.evaluate(P); print('loop', r)
        ok &= r['got'] == ['Loop', 'Loop'] and r['loops'] == n0 + n1 and r['main'] == -(-(2 * (n0 + n1)) // 10) and r['back'] == 0
        # Main on a backup processor: R# mirror P# on one backup unit
        r = await pg.evaluate("()=>{selWall(0);S.wred='Backup processor';storeWall();sync();return ("+P+")()}"); print('backup', r)
        ok &= r['got'] == ['Backup processor', 'Loop'] and r['back'] == 1 and r['backs'] == n0
        # gear on hand: 2 processors. Main wants Full but no processor is left for a backup, so it steps down to Loop
        r = await pg.evaluate("()=>{S.wred='Full';storeWall();selWall(1);S.wred='Backup processor';storeWall();S.gOn=true;S.gProc=2;sync();return ("+P+")()}"); print('short', r)
        ok &= r['got'][0] == 'Loop' and r['why'][0] == 'no processor left for a backup' and r['got'][1] == 'None' and r['main'] == 2 and r['back'] == 0
        # priority: Side first now takes the spare ports for its loop... it wants backup; with 3 processors it gets one
        r = await pg.evaluate("()=>{S.gProc=3;sync();return ("+P+")()}"); print('3 procs', r)
        ok &= r['back'] == 1 and r['main'] == 2
        # priority: both walls on Loop with 2 processors, 9 spare ports; whoever goes first gets them
        r = await pg.evaluate("()=>{S.gProc=2;S.wred='Loop';storeWall();selWall(0);S.wred='Loop';storeWall();sync();const a=redPlan().got;S.wpri=2;storeWall();sync();const b=redPlan();return{a,b:b.got,why:b.why}}"); print('priority', r)
        ok &= r['a'] == ['Loop', 'None'] and r['b'] == ['None', 'Loop'] and r['why'][0] == 'no spare processor ports left'
        await pg.evaluate("()=>{S.wpri=1;storeWall();sync()}")
        # one processor: primaries do not fit, warning row
        r = await pg.evaluate("()=>{S.gProc=1;sync();const R=redPlan();return{short:R.shortP,rows:redRows(R).filter(x=>x[2]=='warn').map(x=>x[0])}}"); print('one', r)
        ok &= r['short'] == n0 + n1 - 10 and 'Not enough processors' in r['rows']
        # spare processor: one on the truck when one is left over, else None with the reason
        r = await pg.evaluate("()=>{S.gProc=5;selWall(0);S.wred='Spare processor';storeWall();selWall(1);S.wred='None';storeWall();sync();const a=redPlan();S.gProc=2;sync();const b=redPlan();return{a:[a.got,a.spare],b:[b.got,b.spare,b.why]}}"); print('spare', r)
        ok &= r['a'] == [['Spare processor', 'None'], 1] and r['b'][0][0] == 'None' and r['b'][1] == 0
        # pull sheet: backup processor, link cable; labels say where R# lands
        r = await pg.evaluate("""()=>{S.gOn=false;selWall(0);S.wred='Backup processor';storeWall();selWall(1);S.wred='Loop';storeWall();sync();const v=pullItems().find(d=>d[0]=='Video')[1].map(x=>[x[0],x[1]]);
          const L=labelList?labelList().flat().filter(x=>x&&x.big&&x.big[0]=='R').map(x=>x.lines[0]):[];return{v,L:[...new Set(L)].slice(0,40)}}""")
        print('pull', r['v']); print('labels', r['L'][:4], r['L'][-2:])
        ok &= any(x[0].startswith('Backup ') and x[1] == 1 for x in r['v']) and any(x[0] == 'Processor link / sync cable' for x in r['v'])
        ok &= any(x.startswith('Backup ') for x in r['L']) and any('return' in x for x in r['L'])
        # Engineering: Redundancy section with the port map, and the signal path svg
        r = await pg.evaluate("()=>{S.showData=true;sync();const e=document.querySelector('#right');return{red:!!e.querySelector('[data-eng=red]'),svg:!!e.querySelector('[data-eng=sig] svg'),map:e.innerText.includes('Backup processor 1'),spec:specSections().map(x=>x[0])}}")
        print('eng', r); ok &= r['red'] and r['svg'] and r['map'] and 'Redundancy' in r['spec']
        # fibre wall on Full: the R# lines get their own trunk and box
        r = await pg.evaluate("""()=>{S.cabOn=true;selWall(1);S.cdD=150;S.wred='Full';storeWall();sync();const R=cabRuns(),f=R.fib.find(x=>x.wi==1);const a={boxes:f.boxes,trunks:f.trunks,own:f.own,ports:f.ports};
          S.wred='Loop';storeWall();sync();const g=cabRuns().fib.find(x=>x.wi==1);return{a,b:{boxes:g.boxes,trunks:g.trunks,own:g.own,ports:g.ports}}}""")
        print('fibre', r); ok &= r['a']['own'] and r['a']['boxes'] == 2 and r['a']['trunks'] == 2 and not r['b']['own'] and r['b']['boxes'] == 1
        # old project: global Return lines off -> None; on -> Loop
        r = await pg.evaluate("()=>{const o=JSON.parse(JSON.stringify(stateObj()));o.walls.forEach(w=>delete w.wred);delete o.S.wred;o.S.ret=false;applyCore(o);sync();const a=walls.map(w=>w.wred);o.S.ret=true;applyCore(o);sync();return{a,b:walls.map(w=>w.wred)}}")
        print('old', r); ok &= r == {'a': ['None', 'None'], 'b': ['Loop', 'Loop']}
        if SHOT:
            await pg.evaluate("()=>{selWall(0);S.wred='Full';storeWall();selWall(1);S.wred='Loop';storeWall();S.cabOn=false;sync()}"); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{const e=document.querySelector('#right [data-eng=sig]');e.scrollIntoView({block:'start'})}"); await pg.wait_for_timeout(200)
            await pg.screenshot(path=SHOT)
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
