# Cable lengths and pack list (Engineering › Cable lengths)
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # off by default: no pack list
        r = await pg.evaluate("()=>{S.cols=12;S.rows=8;storeWall();S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.pdist=true;S.pmode='Snake';S.pdt='Socapex (6 circuits per cable)';S.pvolt=120;S.pamps=20;sync();return{eng:document.querySelector('#right').innerHTML.includes('Cable pack list'),spec:specSections().map(x=>x[0])}}")
        ok &= not r['eng'] and 'Cable pack list' not in r['spec']; print('off', r['spec'])
        # cPick: smallest cable that fits, joined when longer than the longest
        r = await pg.evaluate("()=>{const st=cLens('50, 1,3 5;10 15 20 30 x 0');return{st,a:cPick(32,st),b:cPick(120,st),c:cPick(.4,st),d:cPick(50,st),e:cPick(5,[])}}"); print('pick', r)
        ok &= r == {'st': [1, 3, 5, 10, 15, 20, 30, 50], 'a': [50], 'b': [50, 50, 20], 'c': [1], 'd': [50], 'e': []}
        # on: P1 = (25 m + climb from bottom-left to its first tile) * 1.1
        r = await pg.evaluate("""()=>{S.cabOn=true;S.cdD=25;S.cdP=15;S.cin='Bottom left';S.cslack=10;sync();const w=walls[cur],pl=portPlan(),pp=powerPlan(),R=cabRuns(pl,pp),p1=R.find(x=>x.id=='P1'),t=pl[0][0].tiles[0],q=pieceOf(w,t),s=wst(w),
          x=(q.x+q.w/2)/w.tw*w.wmm/1000,y=(q.y+q.h/2)/w.th*w.hmm/1000,exp=(25+x+Math.abs(s.mh-y))*1.1;
          return{m:p1.m,exp,cab:p1.cab,nd:R.filter(x=>x.kind=='d').length,ports:pl.flat().length,np:R.filter(x=>x.kind=='p').length,cables:R.cables,soca:powerTotals(pp).cables,jd:R.jd,tiles:s.N,
           rows:cabRows(R),wr:cabWallRows(R,0),eng:document.querySelector('#right').innerHTML.includes('Cable pack list'),spec:specSections().map(x=>x[0])}}""")
        print('on', json.dumps({k: r[k] for k in ['m', 'exp', 'cab', 'nd', 'ports', 'np', 'cables', 'soca', 'jd', 'tiles']})); print('  rows', r['rows']); print('  wall', r['wr'])
        ok &= abs(r['m'] - r['exp']) < 1e-9 and r['nd'] == r['ports'] and r['np'] == r['soca'] == r['cables'] and r['jd'] == r['tiles'] - r['ports'] and r['eng'] and 'Cable pack list' in r['spec']
        ok &= r['cab'] == [min(x for x in [1, 3, 5, 10, 15, 20, 30, 50] if x >= r['m'])]
        # return lines double the data runs; top-right arrival changes the climb
        r = await pg.evaluate("()=>{S.ret=true;sync();const a=cabRuns().filter(x=>x.kind=='r').length,n=portPlan().flat().length;S.ret=false;const b=cabRuns().find(x=>x.id=='P1').m;S.cin='Top right';sync();const c=cabRuns().find(x=>x.id=='P1').m;S.cin='Bottom left';sync();return{a,n,b,c}}")
        print('ret/arrive', r); ok &= r['a'] == r['n'] and abs(r['b'] - r['c']) > 1e-6
        # over 100 m: fibre warning and joined cables
        r = await pg.evaluate("()=>{S.cdD=120;sync();const R=cabRuns();S.cdD=25;sync();return cabRows(R)}")
        ok &= any(x[0] == 'Over 100 m' and len(x) == 3 for x in r) and any(x[0] == 'Runs made of joined cables' for x in r); print('far', [x for x in r if x[0] in ('Over 100 m',)])
        # feet: switching units converts the distances and swaps the default cable lists; lengths stay the same in metres
        r = await pg.evaluate("""()=>{const m0=cabRuns().find(x=>x.id=='P1').m,sel=document.querySelector('select[data-k=cunit]');sel.value='ft';sel.dispatchEvent(new Event('input',{bubbles:true}));
          const R=cabRuns();return{cdD:S.cdD,w:walls[cur].cdD,clenD:S.clenD,clenP:S.clenP,m0,m1:R.find(x=>x.id=='P1').m,cab:R.find(x=>x.id=='P1').cab,cu:document.querySelector('.cu').textContent,rows:cabRows(R).slice(0,2)}}""")
        print('ft', r); ok &= r['cdD'] == r['w'] == 82 and r['clenD'].startswith('3, 10') and abs(r['m0'] - r['m1']) < 0.05 and r['cu'] == 'ft' and r['cab'] == [150]
        r = await pg.evaluate("()=>{const sel=document.querySelector('select[data-k=cunit]');sel.value='m';sel.dispatchEvent(new Event('input',{bubbles:true}));return{cdD:S.cdD,clenD:S.clenD}}")
        print('back to m', r); ok &= abs(r['cdD'] - 25) < 0.1 and r['clenD'] == '1, 3, 5, 10, 15, 20, 30, 50'
        # per wall: a second wall keeps its own distance; saved and opened again
        r = await pg.evaluate("""()=>{addWall(false);S.cdD=40;storeWall();sync();const o=JSON.parse(JSON.stringify(stateObj()));selWall(0);const a=S.cdD;applyCore(o);sync();
          return{a,w:walls.map(w=>w.cdD),on:S.cabOn,wr:cabWallRows(cabRuns(),1)}}""")
        print('walls', r); ok &= r['a'] == 25 and r['w'] == [25, 40] and r['on'] is True
        # an old project without the new keys opens with the defaults
        r = await pg.evaluate("()=>{const o=JSON.parse(JSON.stringify(stateObj()));['cabOn','cdD','cdP','cin','cunit','cslack','clenD','clenP'].forEach(k=>delete o.S[k]);o.walls.forEach(w=>{delete w.cdD;delete w.cdP;delete w.cin});S.cabOn=false;applyCore(o);sync();return{w:walls.map(w=>[w.cdD,w.cin]),on:S.cabOn}}")
        print('old', r); ok &= all(x[1] == 'Bottom left' for x in r['w']) and r['on'] is False
        # canvas draws the length tags without errors; no processor or power: a note, no runs
        await pg.evaluate("()=>{S.cabOn=true;S.showData=true;S.showPow=true;sync()}"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("()=>{S.proc=Object.keys(PROC).find(k=>/none/i.test(k))||S.proc;S.pdist=false;sync();return{n:procOn(),note:document.querySelector('#cabNote').textContent,runs:cabRuns().length}}"); print('none', r)
        if not r['n']: ok &= 'first' in r['note'] and r['runs'] == 0
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
