# Power cabling (2026-11-19): each wall starts on its own cable, cables run to a wall, circuit chips for drawing power by
# hand with a hard limit, and the maker's power data (PWR): voltages a tile takes and panels per power link.
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
ok = True
def chk(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        # own cable per wall (default) vs sharing the cable of the wall before
        r = await pg.evaluate("""()=>{S.pdist=true;S.pmode='Snake';storeWall();addWall();S.pmode='Snake';storeWall();sync();
          const a=powerPlan().map(x=>x.map(c=>c.k)),T=powerTotals(powerPlan());walls[1].pown=false;const b=powerPlan().map(x=>x.map(c=>c.k));walls[1].pown=true;
          return{a,b,cables:T.cables,spare:T.spare}}""")
        chk(r['a'] == [[1, 2], [7]] and r['cables'] == 2 and r['spare'] == 9, f'each wall starts on its own Socapex {r}')
        chk(r['b'] == [[1, 2], [3]], 'a wall set to share continues on the cable before')
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
        r = await pg.evaluate("""()=>{const o={};S.pmode='Snake';S.pman=[];S.plink=0;S.preset='ROE Black Pearl BP2V2';applyPreset();S.pvolt=120;storeWall();sync();o.a=[S.plink,tpcW(walls[cur])];
          S.pvolt=230;sync();o.b=S.plink;S.plink=25;storeWall();sync();o.c=S.plink;S.plink=6;storeWall();sync();S.pvolt=120;sync();o.d=S.plink;
          S.preset='INFiLED GX2.5 mk2';applyPreset();S.pvolt=120;storeWall();sync();o.v=S.pvolt;o.dis=[...document.querySelectorAll('select[data-k="pvolt"] option')].filter(x=>x.disabled).map(x=>+x.value);
          S.preset='ROE Ruby RB-B2.6';applyPreset();storeWall();sync();o.ruby=[mkLink(walls[cur],120),Math.floor(16*120/walls[cur].wmax)];
          o.rows=pwrRows({preset:'ROE Black Pearl BP2V2',wmax:190}).map(x=>x[0]);return o}""")
        print(json.dumps(r))
        chk(r['a'] == [10, 10] and r['b'] == 20 and r['c'] == 20, 'BP2V2: 10 panels at 120 V, 20 at 230 V, never above the maker')
        chk(r['d'] == 6, 'a limit the user lowered is kept when the voltage changes')
        chk(r['v'] == 208 and r['dis'] == [100, 110, 120], 'GX mk2 (200-240 V): 120 V is blocked and the circuits move to 208 V')
        chk(r['ruby'][0] == r['ruby'][1] and r['ruby'][0] > 0, f'ROE TRUE1 loop-through 16 A gives V x A / W panels {r["ruby"]}')
        chk('Power input' in r['rows'] and 'Panels per power link' in r['rows'] and 'Power source' in r['rows'], 'Engineering shows the maker power rows')
        # option A: the distros set the rules (voltage, cable type, breaker)
        r = await pg.evaluate("""()=>{const o={};S.preset='ROE Black Pearl BP2V2';applyPreset();storeWall();S.dists=[];S.pdt='Socapex (6 circuits per cable)';S.pamps=20;S.pvolt=230;sync();distAct('dadd');sync();
          o.v=S.pvolt;o.dis=[...document.querySelectorAll('select[data-k="pvolt"] option')].filter(x=>x.disabled).map(x=>+x.value);o.src=$('#dsSrc').textContent;
          S.dists[0].edison=0;S.pdt='powerCON to Edison (1 circuit per cable)';sync();o.kind=outKind();o.kdis=[...document.querySelectorAll('select[data-k="pdt"] option')].filter(x=>x.disabled).map(x=>x.value);
          S.pamps=30;sync();o.amps=S.pamps;S.dists.push(dsSan({id:'d9',sys:'230/400 V 3-phase wye'},1));sync();o.mixed=$('#dsSrc').textContent;return o}""")
        print(json.dumps(r))
        chk(r['v'] == 208 and r['dis'] == [100, 110, 220, 230, 240] and 'Distro 1' in r['src'], 'with a 120/208 V distro only 120 and 208 V can be picked')
        chk(r['kind'] == 'soca' and r['kdis'] == ['L14-30 (2 circuits per cable)', 'powerCON to Edison (1 circuit per cable)'], 'a cable type no distro has outputs for is blocked')
        chk(r['amps'] == 20, 'the breaker cannot go above the Socapex rating')
        chk('do not share a circuit voltage' in r['mixed'], 'distros on different systems are flagged')
        n = await pg.evaluate("()=>Object.keys(PWR).filter(k=>!P[k]).length"); chk(n == 0, 'every PWR key is a catalog model')
        chk(not errs, f'no page errors {errs}'); await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
