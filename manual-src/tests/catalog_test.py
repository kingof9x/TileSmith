# Tile catalog round 1: new INFiLED / AOTO / Gloshine / Absen tiles are in the list with a cited source, pixels agree with
# size / pitch, half tiles pair up, the Model menu groups by series, and "Find a tile" jumps Brand and Model to the pick.
import asyncio, os
from playwright.async_api import async_playwright
APP = os.environ.get('TS_APP', 'file:///home/claude/tilesmith-desktop/app/index.html')
SAMPLE = ['INFiLED ART3.9 outdoor', 'INFiLED AR3.91mk2 Pro outdoor', 'INFiLED GX2.5 mk2', 'INFiLED NX2.5', 'AOTO RM1.5', 'AOTO DL2.6',
          'Gloshine DN2.6 500×1000', 'Gloshine CF Pro2.9', 'Absen Polaris PL3.9 Pro XL V10', 'Absen A27 2.5 (A2725 V3)']
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1100}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        # every catalog tile: sane numbers, pixels match size / pitch within 3%, a source, a known brand
        r = await pg.evaluate("""()=>{const bad=[];let n=0;for(const k in TSER){n++;const q=P[k];if(!q){bad.push([k,'missing']);continue}
          const[wm,hm,pw,ph,pi,kg,W,d]=q;if(!(wm>0&&hm>0&&pw>0&&ph>0&&pi>0&&kg>0&&W>0&&d>0))bad.push([k,'zero']);
          if(Math.abs(wm/pw-pi)/pi>.03||Math.abs(hm/ph-pi)/pi>.03)bad.push([k,'pitch']);
          if(!(PINFO[k]&&PINFO[k].src))bad.push([k,'no source']);if(brandOf(k)=='Custom')bad.push([k,'brand']);if(PEST[k])bad.push([k,'estimated'])}
          return{n,bad,brands:PBR}}""")
        print('CATALOG', r['n'], 'tiles; problems:', r['bad'][:10]); ok &= r['n'] >= 200 and not r['bad'] and 'AOTO' in r['brands'] and 'Gloshine' in r['brands']
        # half tiles: same pitch, half the size along the named side
        r = await pg.evaluate("""()=>Object.entries(HALF).filter(([f])=>TSER[f]).filter(([f,[h,s]])=>{const a=P[f],c=P[h];if(!a||!c)return true;
          return s=='h'?!(a[0]==c[0]&&Math.abs(a[1]-2*c[1])<1e-6&&a[2]==c[2]&&a[3]==2*c[3]):!(a[1]==c[1]&&Math.abs(a[0]-2*c[0])<1e-6&&a[3]==c[3]&&a[2]==2*c[2])})""")
        print('HALF mismatches', r); ok &= not r
        r = await pg.evaluate("(n)=>n.map(k=>[k,!!P[k],PINFO[k]&&PINFO[k].src.slice(0,40)])", SAMPLE); print('SAMPLE', r); ok &= all(x[1] for x in r)
        # the two INFiLED Deep Black 2.6 models now have published figures (no MISSING DATA row)
        r = await pg.evaluate("()=>[P['INFiLED Deep Black DB2.6 Pro'],!!PEST['INFiLED Deep Black DB2.6 Pro'],!!PEST['INFiLED Deep Black DB1.9 Pro']]"); print('DB2.6', r)
        ok &= r[0] == [500, 500, 192, 192, 2.604, 8, 150, 75.5] and r[1] is False and r[2] is True
        # Model menu groups INFiLED by series
        await pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.select_option('[data-brand]', 'INFiLED')
        r = await pg.evaluate("()=>[...document.querySelectorAll('[data-k=preset] optgroup')].map(g=>g.label)"); print('GROUPS', r)
        ok &= 'INFiLED ART' in r and 'INFiLED GXmk2' in r
        # Find a tile: pick an AOTO tile from the search box while INFiLED is showing
        n = await pg.evaluate("()=>document.querySelectorAll('#tFindL option').length"); print('FIND options', n); ok &= n >= 400
        await pg.fill('#tFind', 'AOTO RM1.9'); await pg.dispatch_event('#tFind', 'change'); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>[S.preset,document.querySelector('[data-brand]').value,document.querySelector('[data-k=preset]').value,S.tw,S.wmax,$('#tFind').value]")
        print('FIND pick', r); ok &= r == ['AOTO RM1.9', 'AOTO', 'AOTO RM1.9', 256, 150, '']
        # typing a partial name does nothing; a non-name does nothing
        await pg.fill('#tFind', 'Gloshine DN'); await pg.dispatch_event('#tFind', 'change')
        r = await pg.evaluate("()=>S.preset"); ok &= r == 'AOTO RM1.9'
        # Engineering and PDF rows carry the sheet
        await pg.evaluate("()=>{S.preset='Gloshine CF Pro2.9';applyPreset();S.cols=8;S.rows=6;storeWall();sync()}")
        r = await pg.evaluate("()=>tileRows().filter(x=>x[0]=='Source'||x[0]=='Max hanging height').map(x=>x[0]+': '+x[1].slice(0,50))"); print('ROWS', r)
        ok &= any(x.startswith('Source: Gloshine Curface Pro') for x in r) and any(x.startswith('Max hanging height') for x in r)
        r = await pg.evaluate("()=>{const s=wst(walls[cur]);return[s.px,s.pk,s.kg]}"); print('WALL', r); ok &= r[0] == 168 * 8 * 168 * 6 and abs(r[1] - 6.48) < 1e-6 and abs(r[2] - 408) < 1e-6
        # Spanish: the new labels translate
        await pg.evaluate("()=>setLang('es')"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>[$('#tFind').closest('label').textContent.trim(),$('#tFind').placeholder]"); print('ES', r); ok &= r[0].startswith('Buscar un panel')
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
