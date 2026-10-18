"""powerCON to Edison distribution: defaults 120 V / 15 A on selecting it, one number per circuit, one label pair per circuit
(Edison plug end / powerCON end), engineering rows (plugs, load per plug, wall circuits and overload), regression for Socapex. Prints ALL OK."""
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
ED = 'powerCON to Edison (1 circuit per cable)'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{S.cols=12;S.rows=8;storeWall();S.pdist=true;S.pmode='Snake';S.pvolt=208;S.pamps=30;S.lblWhat='Power only';sync()}"); await pg.wait_for_timeout(150)
        hid = await pg.evaluate("()=>getComputedStyle(document.querySelector('#edW')).display=='none'"); print('Edison fields hidden for Socapex', hid); ok &= hid
        base = await pg.evaluate("()=>({n:powerPlan().flat().length,labels:labelList().length,rows:powRowsCanvas(powerPlan()).map(r=>r[0])})"); print('SOCAPEX', json.dumps(base)[:300])
        # pick Edison through the real select
        await pg.evaluate("(t)=>{const s=document.querySelector('select[data-k=pdt]');s.value=t;s.dispatchEvent(new Event('input',{bubbles:true}))}", ED); await pg.wait_for_timeout(250)
        r = await pg.evaluate("()=>({v:S.pvolt,a:S.pamps,pdt:S.pdt,ed:getComputedStyle(document.querySelector('#edW')).display,lblPow:getComputedStyle(document.querySelector('#lblPowW')).display,note:document.querySelector('#socaNote').textContent.slice(0,140),vf:document.querySelector('[data-k=pvolt]').value,af:document.querySelector('[data-k=pamps]').value})")
        print('SELECTED', json.dumps(r)); ok &= r['v'] == 120 and r['a'] == 15 and r['ed'] != 'none' and r['lblPow'] == 'none' and r['vf'] == '120' and r['af'] == '15' and 'Edison' in r['note']
        r = await pg.evaluate("""()=>{const pl=powerPlan().flat(),T=powerTotals(powerPlan()),L=labelList().filter(x=>x[0].kind=='p');
          return{n:pl.length,cables:T.cables,spare:T.spare,labels:L.length,first:L[0].map(x=>[x.big,x.tag,x.lines]),bigs:L.map(x=>x[0].big).slice(0,4),cl:pl.slice(0,3).map(x=>cLabel(x.k)),rows:powRowsCanvas(powerPlan())}}""")
        print('EDISON', json.dumps(r)[:900]); n = r['n']
        names = [x[0] for x in r['rows']]
        ok &= n > 1 and r['cables'] == n and r['spare'] == 0 and r['labels'] == n and r['bigs'][:2] == ['1', '2'] and r['cl'] == ['1', '2', '3']
        ok &= r['first'][0][1] == '1/2 EDISON PLUG END' and r['first'][1][1] == '2/2 POWERCON END' and 'Edison plug 1' in r['first'][0][2][0] and 'POWER IN' in r['first'][1][2][0]
        ok &= 'Edison plugs needed' in names and 'Peak load per plug' in names and 'Peak load per cable' not in names and 'Wall circuits needed' not in names
        ok &= [x[1] for x in r['rows'] if x[0] == 'Edison plugs needed'][0] == n
        # wall circuits: 3 plugs per 20 A wall circuit, loaded to 80%
        r = await pg.evaluate("""()=>{S.pwall=3;S.pwallA=20;S.derate=true;sync();const T=powerTotals(powerPlan()),pl=powerPlan().flat(),rows=powRowsCanvas(powerPlan()),
          L=labelList().filter(x=>x[0].kind=='p');const g=Math.ceil(pl.length/3),sums=[];pl.forEach(x=>{const i=Math.ceil(x.k/3)-1;sums[i]=(sums[i]||0)+x.watts/S.pvolt});
          return{wn:T.wn,g,over:T.wover,expOver:sums.filter(s=>s>16+1e-6).length,rows:rows.filter(x=>/[Ww]all circuit/.test(x[0])),lab:L[0][0].lines[0],lab4:L[6]?L[6][0].lines[0]:''}}""")
        print('WALL 3x20A', json.dumps(r)[:700]); ok &= r['wn'] == r['g'] and r['over'] == r['expOver'] and 'wall circuit 1' in r['lab'] and any(x[0] == 'Peak load per wall circuit' for x in r['rows'])
        r = await pg.evaluate("()=>{S.pwall=1;S.pwallA=15;S.derate=false;sync();const T=powerTotals(powerPlan());return{wn:T.wn,over:T.wover,n:T.n}}"); print('WALL 1 plug per 15 A circuit', r); ok &= r['over'] == 0 and r['wn'] == r['n']
        await pg.evaluate("()=>{S.derate=true;sync()}")
        # too many plugs on one wall circuit -> over capacity row and (over) marks
        r = await pg.evaluate("""()=>{S.pwall=100;S.pwallA=15;sync();const T=powerTotals(powerPlan()),rows=powRowsCanvas(powerPlan());
          return{over:T.wover,wn:T.wn,row:rows.find(x=>x[0]=='Wall circuit over capacity'),peak:(rows.find(x=>x[0]=='Peak load per wall circuit')||[])[1]}}""")
        print('WALL overload', json.dumps(r)); ok &= r['over'] == 1 and r['wn'] == 1 and r['row'] and '(over)' in r['peak']
        await pg.evaluate("()=>{S.pwall=0;sync()}"); r = await pg.evaluate("()=>powRowsCanvas(powerPlan()).map(x=>x[0]).filter(x=>/Wall/.test(x)).length"); print('pwall 0 -> no wall rows', r); ok &= r == 0
        # saved and restored
        await pg.evaluate("()=>{S.pwall=4;S.pwallA=16;saveNow()}"); await pg.reload(); await pg.wait_for_timeout(600)
        r = await pg.evaluate("()=>[S.pdt,S.pwall,S.pwallA,S.pvolt,S.pamps]"); print('RELOAD', r); ok &= r == [ED, 4, 16, 120, 15]
        # screenshot of the settings and the engineering panel
        await pg.evaluate("()=>{document.querySelectorAll('details').forEach(d=>d.open=false);document.querySelector('#pwrBox').closest('details').open=true;let d=document.querySelector('#pwrBox').closest('details');while(d){d.open=true;d=d.parentElement.closest('details')}}")
        await pg.evaluate("()=>document.querySelector('#pwrBox').scrollIntoView()"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/edison.png')
        # regression: back to Socapex
        await pg.evaluate("()=>{S.pdt='Socapex (6 circuits per cable)';S.lblWhat='Power only';S.lblPow='Cable and circuit labels';sync()}"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("()=>({n:powerPlan().flat().length,cab:powerTotals(powerPlan()).cables,labels:labelList().length,ed:getComputedStyle(document.querySelector('#edW')).display,lp:getComputedStyle(document.querySelector('#lblPowW')).display,first:labelList()[0][0].big,rows:powRowsCanvas(powerPlan()).map(x=>x[0])})")
        print('SOCAPEX again', json.dumps(r)[:400]); ok &= r['labels'] == r['n'] + r['cab'] and r['ed'] == 'none' and r['lp'] != 'none' and r['first'] == '1' and 'Socapex cables' in r['rows'] and 'Peak load per cable' in r['rows']
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
