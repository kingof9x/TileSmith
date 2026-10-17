"""Cable labels: menu hidden until wiring is defined, shows below Animation Options, label counts, both ends, sheet geometry,
copies/skip/keep-together, mobile save, no page errors. Prints ALL OK."""
import asyncio, sys, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.wait_for_timeout(600)
        vis = "()=>{const d=document.querySelector('#lblBox').closest('details');return getComputedStyle(d).display!='none'}"
        VIS = "(()=>{const d=document.querySelector('#lblBox').closest('details');return getComputedStyle(d).display!='none'})()"
        r = await pg.evaluate(vis); print('HIDDEN when nothing wired:', not r); ok &= not r
        await pg.evaluate("()=>{S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.ret=true;sync()}")
        await pg.evaluate("()=>{storeWall();sync()}"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({vis:"+VIS+",n:labelList().length,stat:document.querySelector('#lblStat').textContent,after:!!(document.querySelector('#lblBox').closest('details').previousElementSibling&&/Animation/.test(document.querySelector('#lblBox').closest('details').previousElementSibling.textContent.slice(0,40))),first:labelList()[0],pl:portPlan().flat().length})")
        print('DATA wired', json.dumps(r)[:700]); ok &= r['vis'] and r['n'] == 2 * r['pl'] and r['after']
        # power
        await pg.evaluate("()=>{S.pdist=true;S.pmode='Snake';sync()}"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({n:labelList().length,pw:powerPlan().flat().length,pl:portPlan().flat().length,p:labelList().filter(x=>x[0].kind=='p')[0]})")
        print('DATA+POWER', json.dumps(r)[:500]); ok &= r['n'] == 2 * r['pl'] + r['pw'] and r['p'][0]['big'] == 'S1-1' and 'phase A' in r['p'][0]['lines'][0]
        await pg.evaluate("()=>{S.lblWhat='Power only';sync()}"); r = await pg.evaluate("()=>labelList().every(x=>x[0].kind=='p')"); print('POWER ONLY', r); ok &= r
        await pg.evaluate("()=>{S.lblWhat='Data and power';S.lblJump=true;sync()}"); r = await pg.evaluate("()=>labelList().length")
        tiles = await pg.evaluate("()=>portPlan().flat().reduce((a,x)=>a+x.tiles.length-1,0)+powerPlan().flat().reduce((a,x)=>a+x.tiles.length-1,0)")
        base = await pg.evaluate("()=>portPlan().flat().length*2+powerPlan().flat().length")
        print('JUMPERS', r, base, tiles); ok &= r == base + tiles
        await pg.evaluate("()=>{S.lblJump=false;sync()}")
        # sheet maths
        for size, per in (('Avery 5160 (30 per US Letter sheet)', 30), ('Avery 5163 (10 per US Letter sheet)', 10), ('Avery L7160 (21 per A4 sheet)', 21)):
            await pg.evaluate("(z)=>{S.lblSize=z;S.lblSkip=1;S.lblCopies=1;sync()}", size)
            r = await pg.evaluate("()=>{const L=labelList(),P=labelPages(L),h=labelsHTML();return{pages:P.length,total:P.flat().filter(Boolean).length,need:L.length*2,per:LBL[S.lblSize].c*LBL[S.lblSize].r,cells:(h.match(/class=\"l\"/g)||[]).length}}")
            print(size, r); ok &= r['per'] == per and r['total'] == r['need'] and r['cells'] == r['need']
        # keep-together on 3 across: pair never straddles a row
        await pg.evaluate("()=>{S.lblSize='Avery 5160 (30 per US Letter sheet)';S.lblKeep=true;S.lblCopies=1;S.lblSkip=2;sync()}")
        r = await pg.evaluate("()=>{const P=labelPages(labelList()).flat(),bad=[];for(let i=0;i<P.length;i+=1){}let c=0;const rows=[];P.forEach((x,i)=>{});for(let i=0;i<P.length;i++){if(P[i]&&P[i].tag.startsWith('1/2')){const col=i%3;if(col==2)bad.push(i)}}return{first:P[0],bad}}")
        print('KEEP', r); ok &= r['first'] is None and not r['bad']
        await pg.evaluate("()=>{S.lblKeep=false;S.lblSkip=1;S.lblCopies=2;sync()}")
        r = await pg.evaluate("()=>labelPages(labelList()).flat().filter(Boolean).length==labelList().length*4"); print('COPIES x2', r); ok &= r
        # roll / custom: one per page
        await pg.evaluate("()=>{S.lblCopies=1;S.lblSize='Custom label roll (one per page)';S.lblW=50;S.lblH=20;sync()}")
        r = await pg.evaluate("()=>({pages:labelPages(labelList()).length,n:labelList().length*2,css:/size:50mm 20mm/.test(labelsHTML()),cust:getComputedStyle(document.querySelector('#lblCustom')).display})")
        print('CUSTOM', r); ok &= r['pages'] == r['n'] and r['css'] and r['cust'] != 'none'
        # screenshot of an Avery sheet for a look
        await pg.evaluate("()=>{S.lblSize='Avery 5160 (30 per US Letter sheet)';S.lblKeep=true;S.lblSkip=1;sync()}")
        h = await pg.evaluate("()=>labelsHTML()"); open('/tmp/claude-0/-home-claude/bbcc68aa-c062-5897-954c-d77804faf3e4/scratchpad/labels.html', 'w').write(h)
        # print action opens a window (desktop path)
        async with pg.expect_popup() as pop:
            await pg.evaluate("()=>printLabels()")
        w = await pop.value; await w.wait_for_timeout(300); t = await w.content(); print('POPUP', 'cable labels' in t); ok &= 'cable labels' in t
        await b.close()
        # mobile: saves a file via TSM
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 400, 'height': 800}); pg = await ctx.new_page()
        saved = []
        await pg.add_init_script("window.Capacitor={isNativePlatform:()=>true,getPlatform:()=>'android'};window.TSM={platform:'android',saveFile:(b,n,t)=>{window.__saved=[n,t];return Promise.resolve(true)},keepAwake(){},openUrl(){}};")
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.wait_for_timeout(600)
        mob = await pg.evaluate("()=>typeof MOBILE!='undefined'&&MOBILE"); print('MOBILE flag', mob)
        if mob:
            await pg.evaluate("()=>{S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';sync()}"); await pg.evaluate("()=>printLabels()"); await pg.wait_for_timeout(300)
            r = await pg.evaluate("()=>window.__saved"); print('MOBILE saved', r); ok &= bool(r) and r[0] == 'tilesmith-cable-labels.html'
            btn = await pg.evaluate("()=>document.querySelector('[data-a=lbl]').textContent"); ok &= btn == 'Save label sheet'
        await b.close()
    print('errors', errs); ok &= not errs
    print('ALL OK' if ok else 'PROBLEMS'); return ok
if __name__ == '__main__': sys.exit(0 if asyncio.run(main()) else 1)
