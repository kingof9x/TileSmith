# (from PR #8) Power per phase, connector checks, and the HELIOS port capacity table
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, json
from playwright.async_api import async_playwright
APP = TS_APP_URL
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # 120 V 20 A Socapex on a 120/208 V distro: every circuit on one phase, phases A B C A B C (power settings 2026-11-19:
        # the distro sets the voltage and breaker; the old phase rows without a distro are gone, the distro legs replace them)
        r = await pg.evaluate("""()=>{S.cols=12;S.rows=8;storeWall();distAct('dadd');S.pmode='Snake';S.pdt='Socapex (6 circuits per cable)';S.derate=true;storeWall();sync();
          const pl=powerPlan(),T=powerTotals(pl),all=pl.flat(),exp={};all.forEach(x=>{const ph='ABC'[((x.k-1)%6)%3];exp[ph]=(exp[ph]||0)+x.watts/120});
          return{ph:T.ph,exp,c1:T.cph[1],sum1:T.cab[1],rows:powRowsCanvas(pl).map(x=>x[0]),warn:powWarn(),k1:cPhases(1),k4:cPhases(4),k6:cPhases(6),legs:DSX.load.d1.legs}}""")
        print('120V', json.dumps({k: r[k] for k in ['ph', 'exp', 'c1', 'sum1', 'warn', 'k1', 'k4', 'k6', 'legs']}))
        ok &= r['k1'] == ['A'] and r['k4'] == ['A'] and r['k6'] == ['C'] and not r['warn']
        ok &= all(abs(r['ph'][k] - r['exp'][k]) < 1e-6 for k in r['exp']) and all(abs(r['legs'][i] - r['exp'][k]) < 1e-6 for i, k in enumerate('ABC'))
        ok &= abs(sum(r['c1'].values()) - r['sum1']) < 1e-6 and max(r['c1'].values()) < r['sum1']
        ok &= 'Socapex cables' in r['rows'] and 'Circuit: Distro 1, Socapex' in r['rows']
        # 208 V: line to line, each circuit on two phases
        r = await pg.evaluate("()=>{S.dists[0].cv=208;sync();powerPlan();return{k1:cPhases(1),k3:cPhases(3),v:svcVLL(),warn:powWarn()}}"); print('208V', r)
        ok &= r['k1'] == ['A', 'B'] and r['k3'] == ['C', 'A'] and r['v'] == 208 and not r['warn']
        # 230 V Socapex (EU): line to neutral on a 400 V service
        r = await pg.evaluate("()=>{const d=S.dists[0];d.sys='230/400 V 3-phase wye';d.cv=230;S.dists[0]=dsSan(d,0);S.derate=false;sync();powerPlan();return{k2:cPhases(2),v:svcVLL()}}"); print('230V', r); ok &= r['k2'] == ['B'] and r['v'] == 400
        # breaker above the connector rating is capped at the rating, and a voltage the connector is not made for is flagged
        r = await pg.evaluate("()=>{const d=S.dists[0];d.cb=30;d.l1430=2;sync();const a=[powWarn(),S.pamps];S.pdt='L21-30 (3 circuits per cable)';storeWall();sync();const b=[powWarn(),S.pamps];d.sys='120/240 V split phase';d.cv=240;S.dists[0]=dsSan(d,0);S.pdt='L14-30 (2 circuits per cable)';storeWall();sync();powerPlan();return{a,b,c:powWarn(),l14:cPhases(1),note:document.querySelector('#pwnote').innerHTML}}")
        print('WARN', json.dumps(r)[:600]); ok &= r['a'] == [[], 20] and len(r['b'][0]) == 1 and '230 V' in r['b'][0][0] and r['b'][1] == 30 and r['c'] == [] and r['l14'] == ['A', 'B']
        r = await pg.evaluate("()=>{const d=S.dists[0];d.sys='120/208 V 3-phase wye';d.cv=120;d.cb=40;S.dists[0]=dsSan(d,0);S.pdt='L21-30 (3 circuits per cable)';storeWall();sync();return document.querySelector('#pwnote').innerHTML}"); print('NOTE', r[:300]); ok &= '30 A' in r and (await pg.evaluate('()=>S.pamps')) == 30  # capped at the L21-30 rating
        await pg.evaluate("()=>{S.dists[0].cb=20;sync()}")
        # HELIOS: published table, next row up, nothing above 240 Hz
        r = await pg.evaluate("""()=>{const out={};for(const [f,d] of [[60,12],[60,10],[60,8],[50,12],[100,12],[120,12],[240,12],[24,10]]){S.fps=f;S.bpc=d;out[f+'/'+d]=specPx(PROC['HELIOS Jr'])}
          S.fps=60;S.bpc=8;out.brompton=specPx(PROC['Brompton Tessera S8']);S.bpc=10;out.b10=specPx(PROC['Brompton Tessera S8']);S.bpc=8;out.nova=specPx(PROC['NovaStar VX1000 Pro']);return out}""")
        print('HELIOS', r)
        ok &= r == {'60/12': 401000, '60/10': 482000, '60/8': 482000, '50/12': 485000, '100/12': 192000, '120/12': 192000, '240/12': 87000, '24/10': 1237000, 'brompton': 525000, 'b10': 420000, 'nova': 650000}
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
