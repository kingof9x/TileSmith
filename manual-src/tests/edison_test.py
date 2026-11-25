"""powerCON to Edison on house power (power settings 2026-11-19): adding house power puts the walls on powerCON to Edison at
120 V / 15 A outlets, one number per plug, one label pair per plug (Edison plug end / powerCON end), engineering rows
(plugs, load per plug), house circuits (outlets per house circuit and its breaker, overload), saved and restored, and a
regression for Socapex from a distro. Prints ALL OK."""
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, json
from playwright.async_api import async_playwright
APP = TS_APP_URL
ED = 'powerCON to Edison (1 circuit per cable)'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{S.cols=12;S.rows=8;S.pmode='Snake';S.lblWhat='Power only';storeWall();distAct('hadd');sync()}"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("()=>({v:S.pvolt,a:S.pamps,pdt:S.pdt,d:S.dists[0],lblPow:getComputedStyle(document.querySelector('#lblPowW')).display,note:document.querySelector('#socaNote').textContent.slice(0,160),kdis:[...document.querySelectorAll('select[data-k=pdt] option')].filter(o=>o.disabled).length})")
        print('HOUSE', json.dumps(r)); ok &= r['v'] == 120 and r['a'] == 15 and r['pdt'] == ED and r['d']['type'] == 'house' and r['lblPow'] == 'none' and 'Edison' in r['note'] and r['kdis'] == 3
        r = await pg.evaluate("""()=>{const pl=powerPlan().flat(),T=powerTotals(powerPlan()),L=labelList().filter(x=>x[0].kind=='p');
          return{n:pl.length,cables:T.cables,spare:T.spare,labels:L.length,first:L[0].map(x=>[x.big,x.tag,x.lines]),bigs:L.map(x=>x[0].big).slice(0,4),cl:pl.slice(0,3).map(x=>cLabel(x.k)),rows:powRowsCanvas(powerPlan())}}""")
        print('EDISON', json.dumps(r)[:900]); n = r['n']
        names = [x[0] for x in r['rows']]
        ok &= n > 1 and r['cables'] == n and r['spare'] == 0 and r['labels'] == n and r['bigs'][:2] == ['1', '2'] and r['cl'] == ['1', '2', '3']
        ok &= r['first'][0][1] == '1/2 EDISON PLUG END' and r['first'][1][1] == '2/2 POWERCON END' and 'Edison plug 1' in r['first'][0][2][0] and 'POWER IN' in r['first'][1][2][0]
        ok &= 'Edison plugs' in names and 'Peak load per plug' in names and 'Socapex cables' not in names
        ok &= [x[1] for x in r['rows'] if x[0] == 'Edison plugs'][0] == n
        # house circuits: 3 outlets per 20 A house circuit, loaded to 80%; plugs go to outlets 1, 2, 3 ... in order
        r = await pg.evaluate("""()=>{const d=S.dists[0];d.outl=3;d.hb=20;d.edison=48;S.derate=true;sync();const L=DSX.load[d.id],pl=powerPlan().flat(),sums=[];
          pl.forEach(x=>{const i=Math.ceil(cCab(x.k)/3)-1;sums[i]=(sums[i]||0)+x.watts/120});const lab=labelList().filter(x=>x[0].kind=='p');
          return{g:Object.keys(L.groups).length,exp:sums.length,over:L.over,expOver:sums.filter(s=>s>16+1e-6).length,rows:dsRows(DSX).map(x=>x[0]),lab:lab[0][0].lines[0],bars:document.querySelectorAll(`[data-dbars="${d.id}"] .dleg`).length}}""")
        print('HOUSE 3x20A', json.dumps(r)[:700]); ok &= r['g'] == r['exp'] and r['over'] == r['expOver'] and 'house circuit 1' in r['lab'] and 'Load per house circuit' in r['rows'] and r['bars'] == r['g']
        r = await pg.evaluate("()=>{const d=S.dists[0];d.outl=1;d.hb=15;S.derate=false;sync();const L=DSX.load[d.id];return{g:Object.keys(L.groups).length,over:L.over,n:powerPlan().flat().length}}"); print('HOUSE 1 outlet per 15 A circuit', r); ok &= r['over'] == 0 and r['g'] == r['n']
        await pg.evaluate("()=>{S.derate=true;sync()}")
        # too many plugs on one house circuit -> over capacity row and (over) marks
        r = await pg.evaluate("""()=>{const d=S.dists[0];d.outl=48;d.hb=15;sync();const L=DSX.load[d.id],rows=dsRows(DSX);
          return{over:L.over,g:Object.keys(L.groups).length,row:rows.find(x=>x[0]=='Over capacity'),peak:(rows.find(x=>x[0]=='Load per house circuit')||[])[1]}}""")
        print('HOUSE overload', json.dumps(r)); ok &= r['over'] == 1 and r['g'] == 1 and r['row'] and '(over)' in r['peak']
        r = await pg.evaluate("()=>{S.dists[0].outl=0;sync();return dsRows(DSX).map(x=>x[0]).filter(x=>/House circuit|house circuit/.test(x)).length}"); print('outl 0 -> no house circuit rows', r); ok &= r == 0
        # saved and restored
        await pg.evaluate("()=>{const d=S.dists[0];d.outl=4;d.hb=16;saveNow()}"); await pg.reload(); await pg.wait_for_timeout(600)
        r = await pg.evaluate("()=>[S.pdt,S.dists[0].type,S.dists[0].outl,S.dists[0].hb,S.pvolt,S.pamps]"); print('RELOAD', r); ok &= r == [ED, 'house', 4, 16, 120, 15]
        await pg.evaluate("()=>{document.querySelectorAll('details').forEach(d=>d.open=false);let d=document.querySelector('#distBox').closest('details');while(d){d.open=true;d=d.parentElement.closest('details')}}")
        await pg.evaluate("()=>document.querySelector('#distBox').scrollIntoView()"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/edison.png')
        # regression: a distro, the wall fed from it on Socapex
        await pg.evaluate("()=>{distAct('dadd');S.pfeed=S.dists[1].id;S.pdt='Socapex (6 circuits per cable)';S.lblWhat='Power only';S.lblPow='Cable and circuit labels';storeWall();sync()}"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("()=>({n:powerPlan().flat().length,cab:powerTotals(powerPlan()).cables,labels:labelList().length,lp:getComputedStyle(document.querySelector('#lblPowW')).display,first:labelList()[0][0].big,rows:powRowsCanvas(powerPlan()).map(x=>x[0])})")
        print('SOCAPEX again', json.dumps(r)[:400]); ok &= r['labels'] == r['n'] + r['cab'] and r['lp'] != 'none' and r['first'] == '1' and 'Socapex cables' in r['rows']
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
