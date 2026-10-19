"""ROE presets: every ROE preset is complete and self-consistent (pixels x pitch = size), every model with a half panel gets the half
controls and converts a row correctly, the preset menu is grouped by series. Prints ALL OK."""
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    def chk(c, name=''):
        nonlocal ok
        if not c: print('FAILED', name)
        ok = ok and bool(c)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev = pg.evaluate
        r = await ev("""()=>{const roe=Object.keys(P).filter(k=>k.startsWith('ROE '));const bad=[],pit=[];
          for(const k of roe){const v=P[k];if(v.length!=8||v.some(x=>!(x>0)))bad.push(k);const a=v[0]/v[2],c=v[1]/v[3];if(Math.abs(a-c)>.02*a||Math.abs(a-v[4])>.04*v[4])pit.push([k,a,c,v[4]])}
          const grp=[...document.querySelectorAll('select[data-k=preset] optgroup')].map(o=>o.label);
          const hb=Object.entries(HALF).filter(([f,h])=>f.startsWith('ROE ')&&(!P[f]||!P[h[0]]||P[f][0]!=P[h[0]][0]||P[f][1]!=2*P[h[0]][1]||P[f][2]!=P[h[0]][2]||P[f][3]!=2*P[h[0]][3]));
          return{n:roe.length,bad,pit,hb,grp,names:new Set(roe).size}}""")
        print(json.dumps(r)[:600]); chk(r['n'] >= 120 and not r['bad'] and not r['pit'] and not r['hb'] and r['names'] == r['n'], 'preset data')
        chk(all(x in r['grp'] for x in ('ROE Carbon', 'ROE Carbon MkII', 'ROE Graphite', 'ROE Vanish ST', 'ROE Meru', 'ROE Black Quartz', 'ROE Jet')), 'series groups')
        # every ROE model with a half panel: controls show, bottom row converts to half tiles of the half preset
        models = await ev("()=>Object.keys(HALF).filter(k=>k.startsWith('ROE '))"); print(len(models), 'ROE models with half panels')
        for m in models:
            r = await ev("""(m)=>{S.preset=m;applyPreset();S.cols=4;S.rows=3;S.half=[];S.lay={};storeWall();sync();const box=getComputedStyle(document.querySelector('#halfBox')).display,full=wH(S),th=S.th;
              document.querySelector('[data-a=hrowb]').click();const Q=pieces(S);return{box,n:Q.list.length,nh:Q.nh,hs:full-wH(S),th}}""", m)
            chk(r['box'] != 'none' and r['n'] == 12 and r['nh'] == 4 and abs(r['hs'] - r['th'] / 2) < 1e-6, m + ' ' + json.dumps(r))
        # a half model itself shows no half controls
        r = await ev("()=>{S.preset='ROE Jet JT2.6 Half';applyPreset();storeWall();sync();return getComputedStyle(document.querySelector('#halfBox')).display}"); chk(r == 'none', 'half model hides controls')
        print('errors', errs); chk(not errs, 'page errors'); await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
