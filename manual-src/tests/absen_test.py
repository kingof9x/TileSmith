# New Absen tiles: in the tile list, pixels match size / pitch, half tiles for PR 500x1000, wall maths sane
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
NEW = ['Absen Saturn SA2.6','Absen Saturn SA2.6 1000×500','Absen Saturn SA3.9','Absen Saturn SA3.9 1000×500','Absen PR1.9','Absen PR2.5','Absen PR2.5 500×1000',
       'Absen PR3.9','Absen PR3.9 500×1000','Absen PR5.2','Absen PR5.2 500×1000','Absen Polaris PL1.9 Pro V10','Absen Polaris PL2.9 Lite','Absen Polaris PL3.9 V10',
       'Absen KL1.5 II','Absen A27 1.5 (A2715 V3)','Absen NX2.5']
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""(n)=>n.map(k=>{const q=P[k];if(!q)return[k,'missing'];const[wm,hm,pw,ph,pi,kg,W,d]=q;return[k,Math.abs(wm/pw-pi)<.08&&Math.abs(hm/ph-pi)<.08,brandOf(k),HALF[k]||null,kg>0&&W>0&&d>0]})""", NEW)
        for x in r: print(x); ok &= x[1] is True and x[2] == 'Absen' and x[4] is True
        r = await pg.evaluate("()=>{S.preset='Absen Saturn SA2.6 1000×500';applyPreset();S.cols=10;S.rows=6;storeWall();sync();const s=wst(walls[cur]);return{px:s.px,kW:s.pk,kg:s.kg,opt:[...document.querySelectorAll('option')].some(o=>o.textContent=='Absen Saturn SA2.6 1000×500')}}")
        print('WALL', r); ok &= r['px'] == 3840 * 1152 and abs(r['kW'] - 15.3) < 1e-6 and abs(r['kg'] - 570) < 1e-6
        r = await pg.evaluate("()=>{S.preset='Absen PR2.5 500×1000';applyPreset();storeWall();sync();return halfOf(S)}"); print('HALF', r); ok &= r == ['Absen PR2.5', 'h']
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
