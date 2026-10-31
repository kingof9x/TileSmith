"""Distros, phases and phasor maths (v3.6 power work). Prints ALL OK.
- legSum: 10 A on each of AB, BC, CA -> 17.3 A per line; 120 V loads A 24 / B 18 / C 12 -> neutral 10.4 A; balanced -> 0.
- power factor: 2,880 W at 120 V, PF 0.95 -> 25.3 A; tiles per circuit 16 -> 15 for 120 W tiles.
- L14-30 case: legs 24/12/0 A (neutral 20.8) -> Balance -> 12/12/12 A (neutral 0), only the second cable turned.
- Balance on random walls never raises the highest leg, never moves a cable to another output, every cable stays patched.
- auto patch fills outputs of the matching type in order; a full distro leaves the rest unpatched.
- shared circuits (2fer): two runs take one circuit number, the circuit count drops by one, over capacity flagged.
- tray: click a cable then an output patches it (and swaps with the cable that was there); unpatch with the x button.
- design load Typical 40% scales leg amps; circuits are still checked at max.
- labels carry the distro phase; project without distros (sv 23) gives the same power rows as before; save/open keeps distros.
"""
import asyncio, json, random
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
ok = True
def chk(name, cond, info=''):
    global ok
    print(('ok   ' if cond else 'BAD  ') + name + (('  ' + str(info)) if info != '' else ''))
    ok = ok and bool(cond)

async def fresh(pg):
    await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await fresh(pg)

        r = await pg.evaluate("""()=>{const a=legSum([{I:10,ph:[0,1]},{I:10,ph:[1,2]},{I:10,ph:[2,0]}],3),
          b=legSum([{I:24,ph:[0]},{I:18,ph:[1]},{I:12,ph:[2]}],3),c=legSum([{I:5,ph:[0]},{I:5,ph:[1]},{I:5,ph:[2]}],3),
          d=legSum([{I:10,ph:[0,1]}],2),e=legSum([{I:7,ph:[0]}],1);return{a:a.legs,bn:b.neutral,cn:c.neutral,d:d.legs,e:[e.legs[0],e.neutral]}}""")
        chk('208 V line-to-line loads: 17.3 A per line', all(abs(x - 17.3205) < 1e-3 for x in r['a']), r['a'])
        chk('neutral of 24/18/12 A is 10.4 A', abs(r['bn'] - 10.3923) < 1e-3, r['bn'])
        chk('balanced 120 V load: neutral 0', r['cn'] < 1e-9, r['cn'])
        chk('240 V on split phase: both lines carry the current', all(abs(x - 10) < 1e-9 for x in r['d']), r['d'])
        chk('single phase: line = neutral', abs(r['e'][0] - 7) < 1e-9 and abs(r['e'][1] - 7) < 1e-9, r['e'])

        r = await pg.evaluate("""()=>{S.pdist=true;S.pf=0.95;storeWall();sync();const a=amp(2.88,120),t=tpcCalc(walls[cur]);S.pf=1;sync();return{a,t,t1:tpcCalc(walls[cur])}}""")
        chk('2,880 W at 120 V, PF 0.95 = 25.3 A', r['a'] == '25.3 A', r['a'])
        chk('PF 0.95 gives 15 tiles per circuit, PF 1 gives 16', r['t'] == 15 and r['t1'] == 16, r)

        # L14-30: three 12-tile walls, one circuit each -> cable 1 legs X,Y (A,B), cable 2 leg X (A)
        await fresh(pg)
        setup = """()=>{S.pdist=true;S.pdt='L14-30 (2 circuits per cable)';S.pmode='Snake';S.cols=4;S.rows=3;S.name='A';storeWall();showAll();
          for(const n of ['B','C']){addWall(false);S.cols=4;S.rows=3;S.pmode='Snake';S.name=n;storeWall()}showAll();distAct('dadd');S.dists[0].l1430=4;sync()}"""
        await pg.evaluate(setup)
        r = await pg.evaluate("()=>{const L=DSX.load[S.dists[0].id];return{legs:L.legs,n:L.neutral,p:JSON.parse(JSON.stringify(S.pcab))}}")
        chk('L14-30 before Balance: 24 / 12 / 0 A', [round(x, 1) for x in r['legs']] == [24.0, 12.0, 0.0], r['legs'])
        chk('L14-30 before Balance: neutral 20.8 A', abs(r['n'] - 20.78) < .01, r['n'])
        chk('auto patch: cables on L14-30 outputs 1 and 2', r['p'].get('0:1', {}).get('o') == 'l14301' and r['p'].get('0:2', {}).get('o') == 'l14302', r['p'])
        r = await pg.evaluate("()=>{const ch=dsBalance(S.dists[0].id);sync();const L=DSX.load[S.dists[0].id];return{ch,legs:L.legs,n:L.neutral,p:JSON.parse(JSON.stringify(S.pcab))}}")
        chk('L14-30 after Balance: 12 / 12 / 12 A, neutral 0', r['ch'] and [round(x, 1) for x in r['legs']] == [12.0, 12.0, 12.0] and r['n'] < 1e-6, r)
        chk('Balance kept both cables on their outputs', r['p']['0:1']['o'] == 'l14301' and r['p']['0:2']['o'] == 'l14302', r['p'])
        r = await pg.evaluate("()=>dsBalance(S.dists[0].id)")
        chk('Balance again changes nothing', r is False, r)

        # labels carry the phase
        r = await pg.evaluate("()=>{S.lblWhat='Power only';S.lblPow='Circuit labels only';sync();return labelList().map(p=>p[0].lines.join(' / ')+' | '+p[0].ft)}")
        chk('circuit labels name the distro and phase', any('Distro 1 phase A' in x for x in r) and any('PHASE C' in x for x in r), r)

        # random walls on Socapex: Balance never raises the highest leg and keeps every cable patched on its output
        await fresh(pg)
        random.seed(7); worse = 0; moved = 0; unp = 0
        for trial in range(12):
            cols, rows, n = random.randint(2, 9), random.randint(2, 6), random.randint(1, 3)
            r = await pg.evaluate("""([cols,rows,n,lim])=>{newCanvas();S.pdist=true;S.pdt='Socapex (6 circuits per cable)';S.pmode='Snake';S.plink=lim;S.cols=cols;S.rows=rows;storeWall();showAll();
              for(let i=1;i<n;i++){addWall(false);S.cols=cols+i;S.rows=rows;S.pmode='Snake';S.plink=lim;storeWall()}showAll();distAct('dadd');S.dists[0].soca=24;sync();
              const id=S.dists[0].id,b4=DSX.load[id].max,o4=JSON.stringify(Object.fromEntries(Object.entries(S.pcab).map(([k,v])=>[k,v.o])));dsBalance(id);sync();
              return{b4,af:DSX.load[id].max,same:o4==JSON.stringify(Object.fromEntries(Object.entries(S.pcab).map(([k,v])=>[k,v.o]))),un:DSX.cables.filter(c=>!(S.pcab[c.key]&&S.pcab[c.key].d)).length}}""",
                [cols, rows, n, random.choice([0, 3, 5, 7])])
            if r['af'] > r['b4'] + 1e-6: worse += 1
            if not r['same']: moved += 1
            unp += r['un']
        chk('Balance never raises the highest leg (12 random setups)', worse == 0, worse)
        chk('Balance never moves a cable to another output', moved == 0, moved)
        chk('every cable patched (24 Socapex outputs)', unp == 0, unp)

        # a full distro leaves cables unpatched and says so
        r = await pg.evaluate("""()=>{newCanvas();S.pdist=true;S.pmode='Snake';S.plink=1;S.cols=5;S.rows=5;storeWall();showAll();distAct('dadd');S.dists[0].soca=2;sync();
          return{n:DSX.cables.length,un:DSX.cables.filter(c=>!(S.pcab[c.key]&&S.pcab[c.key].d)).length,row:dsRows(DSX).find(r=>r[0]=='Cables not patched')}}""")
        chk('25 one-tile circuits = 5 Socapex; 2 outputs -> 3 not patched', r['n'] == 5 and r['un'] == 3 and r['row'] is not None, r)

        # tray: pick + click output, swap, unpatch
        r = await pg.evaluate("""()=>{S.dists[0].soca=4;sync();const before=JSON.parse(JSON.stringify(S.pcab));return before}""")
        await pg.click('[data-tpick="0:1"]'); await pg.click('[data-tslot="d1|soca3"]', position={'x': 6, 'y': 6})
        r = await pg.evaluate("()=>JSON.parse(JSON.stringify(S.pcab))")
        chk('tray: cable 1 moved to Socapex 3, cable 3 swapped to Socapex 1', r['0:1']['o'] == 'soca3' and r['0:3']['o'] == 'soca1', r)
        await pg.click('[data-dact="unpatch"][data-v="0:1"]')
        r = await pg.evaluate("()=>({p:S.pcab['0:1'],flag:document.querySelector('.ptflag').textContent})")
        chk('tray: x unpatches the cable and the flag counts it', r['p']['d'] == '' and 'not patched' in r['flag'], r)

        # tray: drag and drop onto an empty output, recorded as an undo step
        await pg.drag_and_drop('[data-tpick="0:2"]', '[data-tslot="d1|soca1"]'); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({p:S.pcab['0:2'],u:document.querySelector('[data-a=undom]').textContent})")
        chk('tray: drag and drop patches the cable (undo step recorded)', r['p']['o'] == 'soca1' and '(' in r['u'], r)

        # shared circuit (2fer): two small walls on one circuit
        r = await pg.evaluate("""()=>{newCanvas();S.pdist=true;S.pmode='Snake';S.cols=2;S.rows=2;S.name='Riser';storeWall();showAll();addWall(false);S.cols=3;S.rows=2;S.pmode='Snake';S.name='Logo';storeWall();showAll();sync();
          const n0=powerTotals(powerPlan()).n;document.querySelectorAll('#left details').forEach(d=>d.open=true);sync();return n0}""")
        await pg.select_option('#shA', '0,0'); await pg.select_option('#shB', '1,0'); await pg.click('[data-dact=shadd]')
        r = await pg.evaluate("()=>{const P=powerPlan(),T=powerTotals(P);return{n:T.n,ks:P.flat().map(x=>x.k),share:P.flat().map(x=>x.share),over:T.over,lab:(sync(),labelList().filter(p=>p[0].kind=='p').map(p=>p[0].big))}}")
        chk('2fer: 2 runs on one circuit number', r['n'] == 1 and r['ks'] == [1, 1] and r['share'] == [2, 2] and r['over'] == 0, r)
        r = await pg.evaluate("""()=>{const W=S.pman;newCanvas();S.pdist=true;S.pmode='Manual';S.cols=4;S.rows=5;storeWall();showAll();S.pman=[[[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2]],[[2,2],[3,2],[0,3],[1,3],[2,3],[3,3],[0,4],[1,4]]];storeWall();sync();
          S.pshare=[[0,[0,0],[0,1]]];sync();const P=powerPlan();return{over:powerTotals(P).over,n:powerTotals(P).n}}""")
        chk('2fer over the circuit (Manual): flagged over capacity', r['over'] == 1 and r['n'] == 1, r)

        # design load
        r = await pg.evaluate("""()=>{newCanvas();S.pdist=true;S.pmode='Snake';S.cols=4;S.rows=4;storeWall();showAll();distAct('dadd');sync();const a=DSX.load[S.dists[0].id].max,t=tpcCalc(walls[cur]);
          S.pload=PLOAD[1];S.ptyp=40;sync();const b=DSX.load[S.dists[0].id].max;return{a,b,t,t2:tpcCalc(walls[cur])}}""")
        chk('Typical 40% scales leg amps; tiles per circuit unchanged', abs(r['b'] - r['a'] * .4) < 1e-6 and r['t'] == r['t2'], r)

        # old project without distros: power rows identical to v3.5 maths
        r = await pg.evaluate("""()=>{newCanvas();const o={sv:23,S:{pdist:true,pvolt:120,pamps:20,derate:true},walls:[Object.assign(wallDef(),{cols:6,rows:4,pmode:'Snake',preset:'Unilumin UpadIV 2.6'})],cur:0};
          applyState(o);sync();return{rows:powRowsCanvas(powerPlan()).map(r=>r.join(' | ')),ds:S.dists.length,tray:document.querySelector('#ptray').hidden}}""")
        chk('sv 23 project: no distros, tray hidden', r['ds'] == 0 and r['tray'], r)
        chk('sv 23 project: same circuit row as v3.5', 'Circuit | 120 V · 20 A · loaded to 80% = 1,920 W usable' in r['rows'], r['rows'])

        # save and open keeps distros and patch
        r = await pg.evaluate("""()=>{distAct('dadd');S.dists[0].name='Distro SL';S.dists[0].amps=200;sync();const o=JSON.parse(JSON.stringify(stateObj()));newCanvas();applyState(o);sync();return{sv:o.sv,d:S.dists,p:S.pcab}}""")
        chk('save/open keeps distro and patch, state version 24', r['sv'] == 24 and r['d'][0]['name'] == 'Distro SL' and r['d'][0]['amps'] == 200 and len(r['p']) >= 1, r)

        # junk in a saved file is cleaned up
        r = await pg.evaluate("""()=>{applyState({sv:24,S:{dists:[{name:'X',amps:'abc',sys:'nope',map:'QQQ'},null],pcab:[1,2],pshare:'x',pload:'zzz'},walls:[wallDef()],cur:0});return{d:S.dists,p:S.pcab,s:S.pshare,l:S.pload}}""")
        chk('bad saved values are cleaned', r['d'][0]['amps'] == 100 and r['d'][0]['map'] == 'ABCABC' and r['d'][0]['sys'] == '120/208 V 3-phase wye' and r['p'] == {} and r['s'] == [] and r['l'] == 'Max (spec)', r)

        # PDF export still works with distros
        r = await pg.evaluate("""()=>{newCanvas();S.pdist=true;S.pmode='Snake';storeWall();showAll();distAct('dadd');sync();let ok=true;try{specSections();dsRows(dsState())}catch(e){ok=String(e)}return ok}""")
        chk('spec sections build with distros', r is True, r)

        chk('no page errors', not errs, errs)
        print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
