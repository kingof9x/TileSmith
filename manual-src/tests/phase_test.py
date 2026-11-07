# Power per phase, 3-phase totals, connector checks, and the HELIOS port capacity table
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # 120 V 20 A Socapex: every circuit on one phase, phases A B C A B C
        r = await pg.evaluate("""()=>{S.cols=12;S.rows=8;storeWall();S.pdist=true;S.pmode='Snake';S.pdt='Socapex (6 circuits per cable)';S.pvolt=120;S.pamps=20;S.derate=true;sync();
          const pl=powerPlan(),T=powerTotals(pl),all=pl.flat(),exp={};all.forEach(x=>{const ph='ABC'[((x.k-1)%6)%3];exp[ph]=(exp[ph]||0)+x.watts/120});
          return{ph:T.ph,exp,c1:T.cph[1],sum1:T.cab[1],rows:powRowsCanvas(pl),warn:powWarn(),k1:cPhases(1),k4:cPhases(4),k6:cPhases(6)}}""")
        print('120V', json.dumps({k: r[k] for k in ['ph', 'exp', 'c1', 'sum1', 'warn', 'k1', 'k4', 'k6']}))
        ok &= r['k1'] == ['A'] and r['k4'] == ['A'] and r['k6'] == ['C'] and not r['warn']
        ok &= all(abs(r['ph'][k] - r['exp'][k]) < 1e-6 for k in r['exp'])
        ok &= abs(sum(r['c1'].values()) - r['sum1']) < 1e-6 and max(r['c1'].values()) < r['sum1']
        names = [x[0] for x in r['rows']]; ok &= 'Peak amps per phase, each cable' in names and 'Balanced 3-phase current @208 V' in names and 'Peak load per cable' not in names
        bal = [x[1] for x in r['rows'] if x[0].startswith('Balanced')][0]; print(' ', bal)
        # 208 V: line to line, each circuit on two phases
        r = await pg.evaluate("()=>{S.pvolt=208;sync();return{k1:cPhases(1),k3:cPhases(3),v:svcVLL(),warn:powWarn()}}"); print('208V', r)
        ok &= r['k1'] == ['A', 'B'] and r['k3'] == ['C', 'A'] and r['v'] == 208 and not r['warn']
        # 230 V Socapex (EU): line to neutral on a 400 V service
        r = await pg.evaluate("()=>{S.pvolt=230;S.derate=false;sync();return{k2:cPhases(2),v:svcVLL()}}"); print('230V', r); ok &= r['k2'] == ['B'] and r['v'] == 400
        # breaker above the connector rating, and a voltage the connector is not made for
        r = await pg.evaluate("()=>{S.pvolt=120;S.pamps=30;sync();const a=powWarn();S.pdt='L21-30 (3 circuits per cable)';S.pvolt=230;S.pamps=30;sync();const b=powWarn();S.pdt='L14-30 (2 circuits per cable)';S.pvolt=240;sync();return{a,b,c:powWarn(),l14:cPhases(1),note:document.querySelector('#pwnote').innerHTML}}")
        print('WARN', json.dumps(r)[:600]); ok &= len(r['a']) == 1 and '20 A' in r['a'][0] and len(r['b']) == 1 and '230 V' in r['b'][0] and r['c'] == [] and r['l14'] == ['A', 'B']
        r = await pg.evaluate("()=>{S.pdt='L21-30 (3 circuits per cable)';S.pvolt=120;S.pamps=40;sync();return document.querySelector('#pwnote').innerHTML}"); print('NOTE', r[:300]); ok &= 'bad' in r and '30 A' in r
        await pg.evaluate("()=>{S.pamps=20;sync()}")
        # HELIOS: published table, next row up, nothing above 240 Hz
        r = await pg.evaluate("""()=>{const out={};for(const [f,d] of [[60,12],[60,10],[60,8],[50,12],[100,12],[120,12],[240,12],[24,10]]){S.fps=f;S.bpc=d;out[f+'/'+d]=specPx(PROC['HELIOS Jr'])}
          S.fps=60;S.bpc=8;out.brompton=specPx(PROC['Brompton Tessera S8']);S.bpc=10;out.b10=specPx(PROC['Brompton Tessera S8']);S.bpc=8;out.nova=specPx(PROC['NovaStar VX1000 Pro']);return out}""")
        print('HELIOS', r)
        ok &= r == {'60/12': 401000, '60/10': 482000, '60/8': 482000, '50/12': 485000, '100/12': 192000, '120/12': 192000, '240/12': 87000, '24/10': 1237000, 'brompton': 525000, 'b10': 420000, 'nova': 650000}
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
