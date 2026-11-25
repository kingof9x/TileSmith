# Power cabling (2026-11-19) and power settings (2026-11-19): each wall starts on its own cable, cables run to a wall, circuit chips for drawing power by
# hand with a hard limit, and the maker's power data (PWR): voltages a tile takes and panels per power link.
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, json
from playwright.async_api import async_playwright
APP = TS_APP_URL
ok = True
def chk(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        # own cable per wall (default) vs sharing the cable of the wall before
        r = await pg.evaluate("""()=>{distAct('dadd');S.pmode='Snake';storeWall();addWall();S.pmode='Snake';storeWall();sync();
          const a=powerPlan().map(x=>x.map(c=>cLabel(c.k))),T=powerTotals(powerPlan());walls[1].pown=false;const b=powerPlan().map(x=>x.map(c=>cLabel(c.k)));walls[1].pown=true;
          return{a,b,cables:T.cables,spare:T.spare}}""")
        chk(r['a'] == [['1-1', '1-2'], ['2-1']] and r['cables'] == 2 and r['spare'] == 9, f'each wall starts on its own Socapex {r}')
        chk(r['b'] == [['1-1', '1-2'], ['1-3']], 'a wall set to share continues on the cable before')
        # cables run to a wall: circuits past them are over
        r = await pg.evaluate("""()=>{S.plink=1;S.pcabs=1;storeWall();sync();const P=powerPlan()[cur];return{n:P.length,over:P.filter(x=>x.nocab).length,note:$('#pcabNote').textContent}}""")
        chk(r['n'] > 6 and r['over'] == r['n'] - 6 and 'more circuits' in r['note'], f'circuits past the cables run to the wall are over {r}')
        # drawing by hand: chips pick the circuit, a full circuit refuses tiles
        r = await pg.evaluate("""()=>{walls.splice(1);cur=0;S.pmode='Manual';S.pcabs=0;S.plink=4;S.pman=[];storeWall();sync();const L=pieces(walls[cur]).list;
          [0,1,2].forEach(i=>pmanAdd(L[i],'click'));S.pman.push([]);pcSel=-1;[6,7].forEach(i=>pmanAdd(L[i],'click'));pcSel=0;pmanAdd(L[3],'click');pmanAdd(L[4],'click');
          const msg=$('#pmsg').textContent;storeWall();sync();return{m:S.pman.map(c=>c.length),msg,chips:[...document.querySelectorAll('#pcabCards [data-pc]')].map(b=>b.textContent)}}""")
        chk(r['m'] == [4, 2] and 'full' in r['msg'], f'a chip draws onto its circuit and a full circuit refuses tiles {r["m"]} {r["msg"]}')
        chk(r['chips'][:2] == ['1-1 · 4/4', '1-2 · 2/4'] and sum(c.endswith('spare') for c in r['chips']) == 4, f'chips show tiles / limit and the spare circuits {r["chips"]}')
        # + Add Socapex cable reserves a cable (patched in the tray) and Draw circuit turns an automatic pattern into circuits to draw on
        r = await pg.evaluate("""()=>{S.pman=[];S.pmode='Snake';S.plink=0;storeWall();sync();const before=document.querySelectorAll('#pcabCards .pcab').length;
          document.querySelector('[data-pcx="add"]').click();const T=powerTotals(powerPlan());const after=[...document.querySelectorAll('#pcabCards .pcabh')].map(x=>x.textContent);
          const n0=powerPlan()[cur].length;document.querySelector('[data-pcx="draw"]').click();return{before,after,cables:T.cables,mode:S.pmode,pman:S.pman.filter(c=>c.length).length,n0,pw:pwiring}}""")
        print(json.dumps(r))
        chk(r['before'] == 1 and len(r['after']) == 2 and r['cables'] == 2, 'Add Socapex cable adds a second cable to the wall')
        chk(r['mode'] == 'Manual' and r['pman'] == r['n0'] and r['pw'], 'Draw circuit keeps the pattern circuits as Manual ones and starts drawing')
        await pg.evaluate("()=>{pwiring=false;S.pcabs=0;storeWall();sync()}")
        # maker data: link limit follows the voltage, a lower user limit is kept, voltages a tile does not take are blocked
        r = await pg.evaluate("""()=>{const o={};const d=S.dists[0],eu=()=>{d.sys='230/400 V 3-phase wye';d.cv=230;S.dists[0]=dsSan(d,0)},us=()=>{const e=S.dists[0];e.sys='120/208 V 3-phase wye';e.cv=120;S.dists[0]=dsSan(e,0)};
          S.pmode='Snake';S.pman=[];S.plink=0;S.preset='ROE Black Pearl BP2V2';applyPreset();us();storeWall();sync();o.a=[S.plink,tpcW(walls[cur])];
          eu();sync();o.b=S.plink;S.plink=25;storeWall();sync();o.c=S.plink;S.plink=6;storeWall();sync();us();sync();o.d=S.plink;
          S.preset='INFiLED GX2.5 mk2';applyPreset();storeWall();sync();o.v=S.pvolt;o.dcv=S.dists[0].cv;o.dis=[...document.querySelectorAll('select[data-dk="cv"] option')].filter(x=>x.disabled).map(x=>+x.value);
          S.preset='ROE Ruby RB-B2.6';applyPreset();storeWall();sync();o.ruby=[mkLink(walls[cur],120),Math.floor(16*120/walls[cur].wmax)];
          o.rows=pwrRows({preset:'ROE Black Pearl BP2V2',wmax:190}).map(x=>x[0]);return o}""")
        print(json.dumps(r))
        chk(r['a'] == [10, 10] and r['b'] == 20 and r['c'] == 20, 'BP2V2: 10 panels at 120 V, 20 at 230 V, never above the maker')
        chk(r['d'] == 6, 'a limit the user lowered is kept when the voltage changes')
        chk(r['v'] == 208 and r['dcv'] == 208 and r['dis'] == [120], f'GX mk2 (200-240 V): 120 V is blocked on the distro and its circuits move to 208 V {r}')
        chk(r['ruby'][0] == r['ruby'][1] and r['ruby'][0] > 0, f'ROE TRUE1 loop-through 16 A gives V x A / W panels {r["ruby"]}')
        chk('Power input' in r['rows'] and 'Panels per power link' in r['rows'] and 'Power source' in r['rows'], 'Engineering shows the maker power rows')
        # Power settings (2026-11-19): the supplies set the rules; each wall picks its supply (Fed from) and a cable that supply has
        r = await pg.evaluate("""()=>{const o={};S.preset='ROE Black Pearl BP2V2';applyPreset();storeWall();S.dists=[];S.pdt='Socapex (6 circuits per cable)';sync();o.off=[pdOn(),$('#supNone').style.display];
          distAct('dadd');sync();o.on=[pdOn(),$('#supNone').style.display,$('#pwrBox').style.display];o.v=[S.pvolt,S.pamps];o.cvo=[...document.querySelectorAll('select[data-dk="cv"] option')].map(x=>+x.value);
          S.dists[0].edison=0;S.pdt='powerCON to Edison (1 circuit per cable)';storeWall();sync();o.kind=outKind();o.kdis=[...document.querySelectorAll('select[data-k="pdt"] option')].filter(x=>x.disabled).map(x=>x.value);
          S.dists[0].cb=30;sync();o.amps=S.pamps;o.note=$('#pwnote').textContent;
          S.dists.push(dsSan({id:'d9',name:'EU',sys:'230/400 V 3-phase wye'},1));addWall();S.pmode='Snake';S.pfeed='d9';S.pdt='L21-30 (3 circuits per cable)';storeWall();sync();
          o.feeds=[...document.querySelectorAll('select[data-k="pfeed"] option')].map(x=>x.value);o.w=walls.map(w=>{const c=pwC(w);return[c.d.id,c.kind,c.V,c.A]});
          const pl=powerPlan();o.labs=pl.map(r=>r.map(x=>cLabel(x.k)));o.patch=DSX.cables.map(c=>[c.name,(S.pcab[c.key]||{}).d]);o.warn=powWarn(walls[1]);
          o.eng=powRowsCanvas(pl).map(x=>x[0]);return o}""")
        print(json.dumps(r))
        chk(r['off'] == [False, ''] and r['on'][0] and r['on'][1] == 'none' and r['on'][2] == '', 'no supply: power is off and the panel asks for one; adding a distro turns it on')
        chk(r['v'] == [120, 20] and r['cvo'] == [120, 208], 'a 120/208 V distro gives 120 V (line to neutral) or 208 V (line to line) circuits')
        chk(r['kind'] == 'soca' and r['kdis'] == ['L14-30 (2 circuits per cable)', 'powerCON to Edison (1 circuit per cable)'], 'a cable type the supply has no outputs for is blocked')
        chk(r['amps'] == 20 and 'Socapex rating' in r['note'], 'the breaker cannot go above the Socapex rating')
        chk(r['feeds'] == ['d1', 'd9'] and r['w'] == [['d1', 'soca', 120, 20], ['d9', 'l2130', 230, 20]], f'each wall has its own supply, cable and voltage {r["w"]}')
        chk(r['labs'][1] and all(x.endswith(('-X', '-Y', '-Z')) for x in r['labs'][1]) and r['patch'] == [['Socapex 1', 'd1'], ['L21-30 1', 'd9']], f'cables are numbered per type and patched to their own supply {r["labs"]} {r["patch"]}')
        chk(any('L21-30 is not made for 230 V' in x for x in r['warn']), 'an L21-30 at 230 V is flagged')
        chk('Circuit: Distro 1, Socapex' in r['eng'] and 'Circuit: EU, L21-30' in r['eng'] and 'L21-30 cables' in r['eng'], 'Engineering lists the circuit of each supply and the cables of each type')
        # moving a cable to another supply in the tray changes its wall's Fed from
        r = await pg.evaluate("""()=>{const c=DSX.cables.find(x=>x.kind=='soca');S.dists[1].soca=2;sync();trayPatch(c.key,'d9|soca1');sync();return{f:walls.map(w=>w.pfeed),p:(S.pcab[c.key]||{}).d,V:pwC(walls[0]).V}}""")
        chk(r['f'] == ['d9', 'd9'] and r['p'] == 'd9' and r['V'] == 230, f'a cable moved to another supply moves its wall {r}')
        # house power: outlets grouped per house circuit, each house circuit checked against its breaker
        r = await pg.evaluate("""()=>{walls.splice(1);cur=0;loadWall(0);S.dists=[];S.cols=6;S.rows=4;S.preset='Unilumin UpadIV 2.6';applyPreset();S.pmode='Snake';S.pman=[];S.plink=0;storeWall();distAct('hadd');sync();
          const L=DSX.load[S.dists[0].id];return{pdt:S.pdt,V:S.pvolt,A:S.pamps,g:L.groups,over:L.over,rows:dsRows(DSX).map(x=>x[0])}}""")
        print(json.dumps(r))
        chk(r['pdt'] == 'powerCON to Edison (1 circuit per cable)' and r['V'] == 120 and r['A'] == 15, 'house power: powerCON to Edison at 120 V on 15 A outlets')
        chk(r['g'] and abs(r['g']['1'] - 24) < 0.01 and r['over'] == 1 and 'Load per house circuit' in r['rows'], f'two plugs on one 20 A house circuit are over {r["g"]}')
        # projects from before: the old cable, voltage and breaker become a supply
        r = await pg.evaluate("""()=>{const out={};applyState({S:{pdist:true,pvolt:208,pamps:30,pdt:'L21-30 (3 circuits per cable)'},walls:[{cols:4,rows:2,pmode:'Snake'}],cur:0});sync();out.a=[S.dists.map(d=>[d.sys,d.cv,d.cb]),S.pdt,S.pvolt,S.pamps];
          applyState({S:{pdist:true,pvolt:120,pamps:15,pwall:3,pwallA:20,pdt:'powerCON to Edison (1 circuit per cable)'},walls:[{cols:4,rows:2,pmode:'Snake'}],cur:0});sync();out.b=S.dists.map(d=>[d.type,d.cv,d.cb,d.outl,d.hb]);
          applyState({S:{pdist:false,pvolt:120},walls:[{cols:4,rows:2}],cur:0});sync();out.c=pdOn();
          applyState({S:{pdist:true,pvolt:120,pamps:20,dists:[{id:'d1',name:'A'},{id:'d2',name:'B'}],pcab:{'0:1':{d:'d1',o:'soca1',r:0},'0:2':{d:'d2',o:'soca2',r:0}}},walls:[{cols:4,rows:2,pmode:'Snake'},{cols:4,rows:2,ox:1000,pmode:'Snake'}],cur:0});sync();out.d=walls.map(w=>w.pfeed);return out}""")
        print(json.dumps(r))
        chk(r['a'] == [[['120/208 V 3-phase wye', 208, 30]], 'L21-30 (3 circuits per cable)', 208, 30], 'an old 208 V L21-30 project gets a 120/208 V distro with 208 V 30 A circuits')
        chk(r['b'] == [['house', 120, 15, 3, 20]] and r['c'] is False, 'old Edison wall circuits become house power; power that was off stays off')
        chk(r['d'] == ['d1', 'd2'], 'an old project with two distros feeds each wall from the distro its cable was patched to')
        # (2026-11-20) a copied or new wall never shares power circuits with the wall it came from; an empty tray says so
        r = await pg.evaluate("""()=>{selWall(0);walls.splice(1);sync();S.pmode='Manual';S.pman=[];storeWall();addWall(true);S.ox=4000;storeWall();addWall();S.ox=8000;storeWall();selWall(0);sync();
          const L=pieces(walls[0]).list;[0,1,2].forEach(i=>pmanAdd(L[i],'click'));storeWall();sync();
          pcabUI();return{chips:[...document.querySelectorAll('#pcabCards [data-pc]')].map(b=>b.textContent),own:walls.map(w=>(w.pman||[]).flat().length),plan:powerPlan().map(x=>x.length),mode:walls[2].pmode,sh:walls[0].pman===walls[1].pman}}""")
        print(json.dumps(r))
        chk(r['chips'] and all(c.startswith('1') for c in r['chips']), f'spare chips are named after the wall\'s own cable {r["chips"]}')
        chk(r['own'] == [3, 0, 0] and r['plan'][1:] == [0, 0] and not r['sh'] and r['mode'] == 'None', 'drawing on one wall never wires a copied or new wall')
        r = await pg.evaluate("""()=>{walls.forEach(w=>{w.pman=[];w.pmode='None'});S.pman=[];S.pmode='None';sync();trayUI(DSX,true);return document.querySelector('#ptray .ptflag').textContent}""")
        chk(r == 'No cables yet', f'the tray says No cables yet when no wall is wired ({r})')
        n = await pg.evaluate("()=>Object.keys(PWR).filter(k=>!P[k]).length"); chk(n == 0, 'every PWR key is a catalog model')
        chk(not errs, f'no page errors {errs}'); await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
