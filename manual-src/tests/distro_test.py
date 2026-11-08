# Distros: list in the Power settings, wall pick, per-distro phase amps, main breaker and output checks, Balance, save/restore
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        ev = pg.evaluate
        # two walls, Socapex 120 V 20 A at 80%: 1,920 W per circuit, 120 W tiles -> 16 per circuit
        await ev("""()=>{S.cols=8;S.rows=5;S.name='Main';storeWall();S.pdist=true;S.pmode='Snake';S.pdt='Socapex (6 circuits per cable)';S.pvolt=120;S.pamps=20;S.derate=true;sync()}""")
        await ev("()=>document.querySelector('[data-a=wdup]').click()"); await pg.wait_for_timeout(200)
        await ev("()=>{S.cols=4;S.rows=4;S.name='Side';storeWall();sync()}"); await pg.wait_for_timeout(100)
        r = await ev("()=>({n:walls.length,box:document.querySelector('#distBox').textContent.slice(0,120),sel:getComputedStyle(document.querySelector('#pdisL')).display,k:powerPlan().map(c=>c.map(x=>x.k))})")
        print('START', json.dumps(r)); ok &= r['n'] == 2 and 'Add a distro' in r['box'] and r['sel'] == 'none'
        before = r['k']
        # add a distro through the button: every wall goes on it, and each wall now starts a new cable
        await ev("()=>document.querySelector('[data-dxa=add]').click()"); await pg.wait_for_timeout(150)
        r = await ev("()=>({d:S.dist,w:walls.map(w=>w.pdis),k:powerPlan().map(c=>c.map(x=>x.k)),sel:getComputedStyle(document.querySelector('#pdisL')).display,cards:document.querySelectorAll('#distBox .dcard').length})")
        print('ADD', json.dumps(r)); ok &= len(r['d']) == 1 and r['w'] == [1, 1] and r['sel'] != 'none' and r['cards'] == 1
        ok &= r['k'] == [[1, 2, 3], [7]]  # wall 2 starts a new cable
        # totals: 40 tiles -> 16+16+8 tiles on A B C, 16 tiles -> 16 on A: A 32, B 16, C 8 A
        r = await ev("()=>{const D=distTotals(powerPlan()).list[0];return{ph:D.ph,used:D.used,part:D.part,lim:D.lim,warn:D.warn}}")
        print('TOTALS', json.dumps(r)); ok &= r['used'] == 2 and r['part'] == [1, 2] and abs(r['lim'] - 320) < 1e-6 and r['ph'] == {'A': 32, 'B': 16, 'C': 8}
        await ev("()=>document.querySelector('[data-dxa=bal]').click()"); await pg.wait_for_timeout(150)
        r = await ev("()=>{const D=distTotals(powerPlan()).list[0];return{ph:D.ph,tail:S.ptail,lab:powerPlan().flat().map(x=>cLabel(x.k)),msg:document.querySelector('#distBox').textContent}}")
        print('BALANCE', json.dumps(r)[:500]); ok &= max(r['ph'].values()) == 24 and 'Busiest phase down 8.0 A' in r['msg'] and r['lab'][3] in ('2-3', '2-6')
        # main breaker and outputs checks
        r = await ev("()=>{S.dist[0].main=5;S.dist[0].outs=1;sync();const D=distTotals(powerPlan()).list[0];return{warn:D.warn,rows:powRowsCanvas(powerPlan()).filter(x=>x[2]=='warn'||x[2]=='head').map(x=>x[0]+': '+x[1])}}")
        print('CHECKS', json.dumps(r)); ok &= any('outputs' in t for t in r['warn']) and any('over the 4 A usable' in t for t in r['warn']) and any(x.startswith('Distro 1') for x in r['rows'])
        # 100% rated breakers lift the 80%; EU system at 120 V warns
        r = await ev("()=>{S.dist[0].main=400;S.dist[0].outs=6;S.dist[0].r100=true;sync();const a=distTotals(powerPlan()).list[0].lim;S.dist[0].sys='eu3';sync();return{a,b:distTotals(powerPlan()).list[0].lim,w:distTotals(powerPlan()).list[0].warn}}")
        print('RULES', json.dumps(r)); ok &= r['a'] == 400 and r['b'] == 400 and any('230' in t for t in r['w'])
        await ev("()=>{S.dist[0].sys='us3';S.dist[0].r100=false;sync()}")
        # second distro; move wall 2 through the per-wall select
        await ev("()=>document.querySelector('[data-dxa=add]').click()"); await pg.wait_for_timeout(100)
        await ev("()=>{selWall(1)}"); await pg.wait_for_timeout(100)
        await ev("()=>{const s=document.querySelector('#pdisSel');s.value='2';s.dispatchEvent(new Event('input',{bubbles:true}))}"); await pg.wait_for_timeout(150)
        r = await ev("()=>{const D=distTotals(powerPlan());return{w:walls.map(w=>w.pdis),a:D.list.map(x=>x.walls),loose:D.loose,wr:wallRows(walls[1],[],powerPlan()[1]).find(x=>x[0]=='Distro')}}")
        print('TWO', json.dumps(r)); ok &= r['w'] == [1, 2] and r['a'] == [['Main'], ['Side']] and r['loose'] == [] and r['wr'][1] == 'Distro 2'
        # remove distro 2: its wall goes back to distro 1
        await ev("()=>document.querySelectorAll('[data-dxa=del]')[1].click()"); await pg.wait_for_timeout(100)
        r = await ev("()=>({d:S.dist.length,w:walls.map(w=>w.pdis)})"); print('DEL', r); ok &= r == {'d': 1, 'w': [1, 1]}
        # save and restore
        await ev("()=>{S.dist[0].name='Stage left';saveNow()}"); await pg.reload(); await pg.wait_for_timeout(700)
        r = await ev("()=>({d:S.dist,w:walls.map(w=>w.pdis),t:S.ptail})"); print('RELOAD', json.dumps(r)); ok &= r['d'][0]['name'] == 'Stage left' and r['w'] == [1, 1]
        # no distros: numbering as before
        await ev("()=>{document.querySelector('[data-dxa=del]').click()}"); await pg.wait_for_timeout(100)
        r = await ev("()=>({k:powerPlan().map(c=>c.map(x=>x.k)),pos:POS.size})"); print('NONE', r); ok &= r['k'] == before and r['pos'] == 0
        # Edison: no distros
        r = await ev("()=>{S.pdt='powerCON to Edison (1 circuit per cable)';sync();return document.querySelector('#distBox').textContent}"); ok &= 'not used' in r
        print('page errors', errs); ok &= not errs
        await ev("()=>{S.pdt='Socapex (6 circuits per cable)';S.pvolt=120;S.pamps=20;sync();document.querySelector('[data-dxa=add]').click();document.querySelector('[data-dxa=add]').click()}"); await pg.wait_for_timeout(200)
        await ev("()=>{let d=document.querySelector('#distBox').closest('details');while(d){d.open=true;d=d.parentElement.closest('details')};document.querySelector('#pwnote').scrollIntoView()}"); await pg.wait_for_timeout(200)
        e = await pg.query_selector('#pwrBox'); await e.screenshot(path='/tmp/distro.png')
        await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
