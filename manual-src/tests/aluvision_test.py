# Aluvision Hi-LED 55 tiles: every model is in the list with its sheet, pixels agree with size / pitch, the Model menu
# groups flat and curved tiles, and only NovaStar processors are offered (the brochure names NovaStar boxes only).
import os
from _paths import TS_APP_URL, TS_DESK
import asyncio, os
from playwright.async_api import async_playwright
APP = os.environ.get('TS_APP', TS_APP_URL)
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1100}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""()=>{const ks=Object.keys(P).filter(k=>k.startsWith('Aluvision ')),bad=[];
          ks.forEach(k=>{const[wm,hm,pw,ph,pi,kg,W,d]=P[k];if(!(wm>0&&hm>0&&pw>0&&ph>0&&pi>0&&kg>0&&W>0&&d>0))bad.push([k,'zero']);
           if(Math.abs(wm/pw-pi)/pi>.03||Math.abs(hm/ph-pi)/pi>.03)bad.push([k,'pitch']);if(!(PINFO[k]&&PINFO[k].src))bad.push([k,'source']);
           if(brandOf(k)!='Aluvision')bad.push([k,'brand']);if(!TSER[k])bad.push([k,'series']);if(String(tileFam(k))!='novastar')bad.push([k,'proc'])});
          return{n:ks.length,bad}}""")
        print('ALUVISION', r); ok &= r['n'] == 12 and not r['bad']
        r = await pg.evaluate("()=>P['Aluvision Hi-LED 55 2.5']"); print('2.5', r); ok &= r == [496, 496, 192, 192, 2.58, 9.5, 150, 55]
        await pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.select_option('[data-brand]', 'Aluvision')
        r = await pg.evaluate("()=>[S.preset,[...document.querySelectorAll('[data-k=preset] optgroup')].map(g=>g.label)]"); print('MENU', r)
        ok &= r[0].startswith('Aluvision ') and 'Aluvision Hi-LED 55' in r[1] and 'Aluvision Hi-LED 55 curved' in r[1]
        await pg.fill('#tFind', 'Aluvision Hi-LED 55 2.5'); await pg.dispatch_event('#tFind', 'change'); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>[S.preset,S.tw,S.th,S.wmm,S.wmax]"); print('FIND', r); ok &= r == ['Aluvision Hi-LED 55 2.5', 192, 192, 496, 150]
        r = await pg.evaluate("()=>{procRefresh();return[...document.querySelectorAll('[data-k=proc] optgroup')].map(g=>g.label)}"); print('PROCS', r)
        ok &= 'NovaStar' in r and not any(x in r for x in ('Brompton', 'Megapixel HELIOS', 'Evision'))
        await pg.evaluate("()=>{S.cols=8;S.rows=4;storeWall();sync()}")
        r = await pg.evaluate("()=>tileRows().filter(x=>['Receiving card','Source','Power (sheet)'].includes(x[0])).map(x=>x[0]+': '+x[1].slice(0,40))"); print('ROWS', r)
        ok &= any(x.startswith('Source: Aluvision Hi-LED 55 brochure') for x in r) and any('A8S' in x for x in r)
        r = await pg.evaluate("()=>{const s=wst(walls[cur]);return[s.px,s.kg]}"); print('WALL', r); ok &= r[0] == 192 * 8 * 192 * 4 and abs(r[1] - 304) < 1e-6
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
