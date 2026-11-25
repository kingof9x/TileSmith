# Locations (Engineering › Locations; code name zones): named places the show stages its gear. Walls, distros and the processor pick a zone;
# Engineering totals each zone, the pull sheet has a block per zone, the binder orders wall pages by zone and adds a zone map,
# and the strip above the viewport hides a zone's walls in the viewport only.
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, json, os, re, subprocess, tempfile
from playwright.async_api import async_playwright
APP = TS_APP_URL
OUT = os.environ.get('ZONES_OUT') or tempfile.mkdtemp(prefix='zones')
SHOT = os.environ.get('ZONES_SHOT')
def txt(path, first=None, last=None):
    a = ['pdftotext', '-layout'] + (['-f', str(first)] if first else []) + (['-l', str(last)] if last else []) + [path, '-']
    return subprocess.run(a, capture_output=True, text=True).stdout
def tiles(items):
    return sum(x[1] for d, rows in items if d == 'Video' for x in rows if x[0].endswith('tile'))
def row(items, dept, start):
    return sum(x[1] for d, rows in items if d == dept for x in rows if x[0].startswith(start))
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # three walls, processor, Socapex power with two distros
        await pg.evaluate("""()=>{S.cw=3840;S.ch=2160;S.cols=12;S.rows=6;S.name='Centre';S.ox=600;storeWall();addWall(false);S.name='IMAG L';S.cols=4;S.rows=4;S.ox=0;S.oy=0;storeWall();
          addWall(false);S.name='IMAG R';S.cols=4;S.rows=4;S.ox=3000;S.oy=0;storeWall();sync();
          S.proc='NovaStar VX1000 Pro';applySpec();S.pdt='Socapex (6 circuits per cable)';walls.forEach(w=>{w.wmode='Snake';w.pmode='Snake'});loadWall(0);
          distAct('dadd');distAct('dadd');S.showData=false;sync()}""")
        # no zones yet: nothing changes
        r = await pg.evaluate("()=>({on:zOn(),strip:document.querySelector('#zstrip').hidden,eng:document.querySelector('#right').innerText.includes('Locations')})")
        print('off', r); ok &= r == {'on': False, 'strip': True, 'eng': False}
        # add three zones with the buttons, rename them, assign walls and gear through the selects
        await pg.evaluate("()=>{const p=document.querySelector('#zoneBox');p.closest('details').open=true;p.closest('details').parentElement.closest('details').open=true}")
        for _ in range(3): await pg.click('[data-zact=add]')
        names = ['Stage left', 'Stage right', 'Upstage']
        for i, n in enumerate(names):
            await pg.fill(f'#zoneBox input[type=text] >> nth={i}', n)
        await pg.evaluate("()=>document.activeElement.blur()")
        ids = await pg.evaluate("()=>S.zones.map(z=>z.id)"); sl, sr, us = ids
        async def pick(sel, v): await pg.select_option(sel, str(v))
        await pick('[data-zw="0:0"]', us); await pick('[data-zw="0:1"]', sl); await pick('[data-zw="0:2"]', sr)
        await pick('[data-zg=proc]', us); await pick('[data-zg="0"]', sl); await pick('[data-zg="1"]', sr)
        r = await pg.evaluate("()=>({z:S.zones.map(z=>z.name),w:walls.map(w=>w.zone),p:S.zProc,d:S.dists.map(d=>d.zone),cols:S.zones.map(z=>z.c)})"); print('set', r)
        ok &= r['z'] == names and r['w'] == [us, sl, sr] and r['p'] == us and r['d'] == [sl, sr] and len(set(r['cols'])) == 3
        # Engineering: a Zones section; per-zone totals add up to the whole show
        r = await pg.evaluate("()=>{const T=zTotals(),all=walls.map(wst);return{T:T.map(t=>[t.z.name,t.walls,t.N,+t.kg.toFixed(3),t.dp,t.pc]),N:all.reduce((a,s)=>a+s.N,0),kg:+all.reduce((a,s)=>a+s.kg,0).toFixed(3),dp:(()=>{const pl=portPlan(),RP=redPlan(pl);return pl.reduce((a,x,i)=>a+x.length*(hasR(RP.got[i])?2:1),0)})(),pc:powerPlan().flat().length,txt:document.querySelector('#right').innerText}}")
        print('totals', r['T']); T = {t[0]: t for t in r['T']}
        ok &= T['Upstage'][2] == 72 and T['Stage left'][2] == 16 and T['Stage right'][2] == 16 and T['No location'][1] == 0
        ok &= sum(t[2] for t in r['T']) == r['N'] and abs(sum(t[3] for t in r['T']) - r['kg']) < 1e-6 and sum(t[4] for t in r['T']) == r['dp'] and sum(t[5] for t in r['T']) == r['pc']
        ok &= 'Gear staged here' in r['txt'] and 'Stage left' in r['txt']
        # pull sheet: each zone's block holds its own walls and gear; blocks add up to the whole show
        for cab in (False, True):
            r = await pg.evaluate(f"()=>{{S.cabOn={'true' if cab else 'false'};sync();return{{all:pullItems(),z:S.zones.map(z=>pullItems(z.id)),none:pullItems(0)}}}}")
            Z = dict(zip(names, r['z'])); print('pull', cab, json.dumps(Z)[:900])
            ok &= tiles(Z['Upstage']) == 72 and tiles(Z['Stage left']) == 16 and tiles(Z['Stage right']) == 16 and r['none'] == []
            ok &= sum(tiles(z) for z in r['z']) == tiles(r['all'])
            for d, s in (('Data', 'Data jumper'), ('Power', 'Power jumper'), ('Power', 'Socapex (6 circuits per cable) breakout')):
                ok &= sum(row(z, d, s) for z in r['z']) == row(r['all'], d, s)
            pz = lambda z: [x[0] for d, rows in z for x in rows]
            ok &= 'NovaStar VX1000 Pro' in pz(Z['Upstage']) and 'NovaStar VX1000 Pro' not in pz(Z['Stage left'])
            ok &= any(x.startswith('Distro: Distro 1') for x in pz(Z['Stage left'])) and not any(x.startswith('Distro: Distro 1') for x in pz(Z['Stage right']))
            if cab:
                ok &= sum(row(z, 'Data', 'Data cable') for z in r['z']) == row(r['all'], 'Data', 'Data cable')
                ok &= sum(row(z, 'Power', 'Socapex (6 circuits per cable) cable') for z in r['z']) == row(r['all'], 'Power', 'Socapex (6 circuits per cable) cable')
        # a wall with no zone goes in the No zone block
        r = await pg.evaluate(f"()=>{{walls[2].zone=0;if(cur==2)S.zone=0;sync();return{{n:tiles(pullItems(0)),t:zTotals().find(t=>t.z.id==0).walls}}}}".replace('tiles(pullItems(0))', "pullItems(0).find(d=>d[0]=='Video')[1].reduce((a,x)=>a+(x[0].endsWith('tile')?x[1]:0),0)"))
        print('none', r); ok &= r == {'n': 16, 't': 1}
        await pick('[data-zw="0:2"]', sr)
        # viewport: hiding a zone covers its walls, keeps them in the output and stops clicks selecting them
        await pg.click(f'#zstrip [data-zact=hide][data-v="{sl}"]')
        r = await pg.evaluate("""()=>{const a=M.getContext('2d').getImageData(20,20,1,1).data,w=walls[1];vpDraw();const R=vp.getBoundingClientRect(),x=R.left+V.x+(w.ox+20)*V.z,y=R.top+V.y+(w.oy+20)*V.z;
          return{hide:S.zHide,hit:hitWall({clientX:x,clientY:y}),out:a[3],strip:!document.querySelector('#zstrip').hidden,off:document.querySelector(`#zstrip [data-v="${S.zHide[0]}"]`).classList.contains('off'),all:!!document.querySelector('#zstrip [data-zact=showall]')}}""")
        print('hide', r); ok &= r['hide'] == [sl] and r['hit'] == -1 and r['out'] == 255 and r['strip'] and r['off'] and r['all']
        await pg.click('#zstrip [data-zact=showall]'); ok &= await pg.evaluate("()=>S.zHide.length==0")
        # move a zone up: the pull sheet follows the new order
        await pg.click(f'[data-zact=up][data-v="{us}"]'); r = await pg.evaluate("()=>S.zones.map(z=>z.name)"); print('order', r); ok &= r == ['Stage left', 'Upstage', 'Stage right']
        if SHOT:
            await pg.evaluate("()=>{const e=document.querySelector('#zoneBox');e.scrollIntoView({block:'start'});fit()}"); await pg.wait_for_timeout(400); await pg.screenshot(path=SHOT)
        # binder: zone map page, wall pages grouped by zone in zone order, pull sheet blocks
        await pg.evaluate("()=>{S.bShow='Zone Test';sync()}")
        async with pg.expect_download() as d: await pg.click('[data-a=binder]:visible')
        dl = await d.value; f = os.path.join(OUT, dl.suggested_filename); await dl.save_as(f)
        t2 = txt(f, 2, 2); toc = [(m.group(1).strip(), int(m.group(2))) for m in re.finditer(r'^\s*(\S[^\n]*?)\s{2,}[ .]*(\d+)\s*$', t2, re.M)]; print('toc', toc)
        names_toc = [x[0] for x in toc]; D = dict(toc)
        ok &= names_toc[:6] == ['Canvas', 'Location map', 'LED walls', 'Stage left', 'Upstage', 'Stage right']
        ok &= 'Location map' in txt(f, D['Location map'], D['Location map']) and 'IMAG L' in txt(f, D['Stage left'], D['Stage left']) and 'Centre' in txt(f, D['Upstage'], D['Upstage'])
        ps = txt(f, D['Pull sheet'], D['Spec sheet'] - 1); print(ps[:1800])
        i1, i2, i3 = ps.find('STAGE LEFT'), ps.find('UPSTAGE'), ps.find('STAGE RIGHT'); ok &= -1 < i1 < i2 < i3 and 'NO LOCATION' not in ps
        # saved and opened again; an old project without zones opens with none; removing a zone frees its walls and gear
        r = await pg.evaluate("""()=>{const o=JSON.parse(JSON.stringify(stateObj()));S.zones=[];walls.forEach(w=>w.zone=0);applyCore(o);sync();const a={z:S.zones.map(z=>z.name),w:walls.map(w=>w.zone),p:S.zProc,d:S.dists.map(d=>d.zone)};
          const o2=JSON.parse(JSON.stringify(o));delete o2.S.zones;delete o2.S.zProc;delete o2.S.zHide;o2.walls.forEach(w=>delete w.zone);S.zones=[];applyCore(o2);sync();const b={on:zOn(),w:walls.map(w=>w.zone)};
          applyCore(o);sync();const id=S.zones.find(z=>z.name=='Upstage').id;zAct('del',id);return{a,b,c:{z:S.zones.map(z=>z.name),w:walls.map(w=>w.zone),p:S.zProc}}}""")
        print('save', r); ok &= r['a'] == {'z': ['Stage left', 'Upstage', 'Stage right'], 'w': [us, sl, sr], 'p': us, 'd': [sl, sr]}
        ok &= r['b'] == {'on': False, 'w': [0, 0, 0]} and r['c'] == {'z': ['Stage left', 'Stage right'], 'w': [0, sl, sr], 'p': 0}
        # Spanish: the panel text is translated
        r = await pg.evaluate("()=>{setLang&&setLang('es');sync();return document.querySelector('#zoneBox').closest('details').querySelector('summary').innerText}") if await pg.evaluate("()=>typeof setLang=='function'") else 'skip'
        print('es', r); ok &= r in ('skip', 'Ubicaciones')
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
