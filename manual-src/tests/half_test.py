"""Half tiles: Convert top/bottom row buttons (toggle), options under Size of LED Wall, STOP MARKING button, wall area follows
the real tiles. Prints ALL OK."""
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
        async def setk(k, v):
            await ev("([k,v])=>{if(k=='preset'){const bs=document.querySelector('[data-brand]');if(bs&&bs.value!=brandOf(v)){bs.value=brandOf(v);bs.dispatchEvent(new Event('change',{bubbles:true}))}}const e=document.querySelector('[data-k='+k+']');e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}", [k, v])
        async def tap(a): await ev("(a)=>document.querySelector('[data-a='+a+']').click()", a)
        # not shown for a model without a half version
        r = await ev("()=>getComputedStyle(document.querySelector('#halfBox')).display"); chk(r == 'none', 'hidden for plain model'); print('HIDDEN', r)
        await setk('preset', 'ROE Carbon CB3'); await setk('cols', '4'); await setk('rows', '3'); await pg.wait_for_timeout(200)
        r = await ev("()=>({disp:getComputedStyle(document.querySelector('#halfBox')).display,inSize:!!document.querySelector('#halfBox').closest('details').querySelector('[data-k=cols]'),inTile:!!document.querySelector('#halfBox').closest('details').querySelector('[data-k=tw]'),b:document.querySelector('[data-a=hrowb]').textContent,t:document.querySelector('[data-a=hrowt]').textContent})")
        print('SHOWN', r); chk(r['disp'] != 'none' and r['inSize'] and not r['inTile'], 'under Size of LED Wall'); chk(r['b'] == 'Convert bottom row to half tiles' and r['t'] == 'Convert top row to half tiles', 'labels')
        full = await ev("()=>({n:pieces(S).list.length,h:wH(S),w:wW(S),th:S.th})"); print('FULL', full)
        # bottom row
        await tap('hrowb'); await pg.wait_for_timeout(200)
        r = await ev("()=>{const P=pieces(S);return{n:P.list.length,half:P.nh,h:wH(S),ys:[...new Set(P.list.map(x=>x.y+x.h))],lbl:document.querySelector('[data-a=hrowb]').textContent}}"); print('BOTTOM', r)
        chk(r['n'] == 12 and r['half'] == 4 and r['lbl'] == 'Restore bottom row to full tiles', 'bottom converted'); chk(r['h'] == full['h'] - full['th'] / 2, 'height shrinks by half a tile')
        await tap('hrowb'); await pg.wait_for_timeout(200)
        r = await ev("()=>({n:pieces(S).list.length,half:pieces(S).nh,h:wH(S)})"); print('RESTORED', r); chk(r['half'] == 0 and r['h'] == full['h'], 'restored')
        # top row
        await tap('hrowt'); await pg.wait_for_timeout(200)
        r = await ev("()=>{const P=pieces(S);return{n:P.list.length,half:P.nh,h:wH(S),ys:P.list.map(x=>x.y),lbl:document.querySelector('[data-a=hrowt]').textContent}}"); print('TOP', r)
        chk(r['half'] == 4 and r['h'] == full['h'] - full['th'] / 2 and r['lbl'] == 'Restore top row to full tiles' and min(r['ys']) == 0, 'top converted, wall starts at its own top')
        # tiles stay where they are on the canvas, whatever the layout does to the top-left corner
        await tap('hclr'); await pg.wait_for_timeout(100); await ev("()=>{S.ox=100;S.oy=50;storeWall();sync()}")
        abs_before = await ev("()=>{const R=pieces(S).list.find(p=>p.c==1&&p.r==1);return[S.ox+R.x,S.oy+R.y,S.ox,S.oy]}")
        await tap('hrowt'); await pg.wait_for_timeout(200)
        abs_after = await ev("()=>{const R=pieces(S).list.find(p=>p.c==1&&p.r==1);return[S.ox+R.x,S.oy+R.y,S.ox,S.oy,S.gy]}")
        print('ABS', abs_before, abs_after); chk(abs_before[0] == abs_after[0] and abs_before[1] == abs_after[1], 'tile does not move on canvas'); chk(abs_after[3] == 50 + 160 and abs_after[4] == 160, 'wall position follows the tiles')
        # patterns scale to the real tiles
        r = await ev("()=>{const o=pat;window.__c=[];pat=function(c,L,w,h){__c.push([w,h]);return o.apply(this,arguments)};S.pat='circles';storeWall();render();pat=o;return __c}"); print('PATTERN SIZE', r)
        chk(r and r[0] == [640, 800], 'pattern gets the bbox size')
        # spec sheet numbers follow the real tiles
        r = await ev("()=>{const s=wst(S);return[s.pw,s.ph,+s.mh.toFixed(3),s.N]}"); print('SPEC', r); chk(r[0] == 640 and r[1] == 800 and r[2] == 3 and r[3] == 12, 'spec uses real size')
        # in marking mode an empty half above the wall can be filled again (the whole tile grid is clickable), which moves the corner back
        await tap('hedit'); await pg.wait_for_timeout(200)
        pt = await ev("()=>{const q=vp.getBoundingClientRect(),g=unitG(S),gy0=S.oy-pieces(S).Y0,gx0=S.ox-pieces(S).X0;return[q.left+V.x+(gx0+g.uw*1.5)*V.z,q.top+V.y+(gy0+g.uh*0.5)*V.z,pieces(S).list.length]}")
        await pg.mouse.click(pt[0], pt[1]); await pg.wait_for_timeout(250)
        r = await ev("()=>({n:pieces(S).list.length,oy:S.oy,gy:S.gy})"); print('FILL ABOVE', pt[2], r); chk(r['n'] == pt[2] + 1 and r['gy'] == 0 and r['oy'] == 50, 'fill above wall, corner moves back')
        await tap('hedit'); await tap('hclr'); await pg.wait_for_timeout(100)
        await tap('hrowt'); await tap('hrowb'); await pg.wait_for_timeout(200)
        r = await ev("()=>({half:pieces(S).nh,h:wH(S)})"); print('BOTH', r); chk(r['half'] == 8 and r['h'] == full['h'] - full['th'], 'both rows')
        await tap('hclr'); await pg.wait_for_timeout(200)
        # stop button only while marking
        r = await ev("()=>getComputedStyle(document.querySelector('#halfStop')).display"); chk(r == 'none', 'stop hidden'); print('STOP hidden', r)
        await tap('hedit'); await pg.wait_for_timeout(200)
        r = await ev("()=>({d:getComputedStyle(document.querySelector('#halfStop')).display,t:document.querySelector('#halfStop').textContent,top:document.querySelector('#halfStop').getBoundingClientRect().top,vp:vp.getBoundingClientRect().top})"); print('STOP shown', r)
        chk(r['d'] != 'none' and r['t'] == 'STOP MARKING HALF TILES' and r['top'] >= r['vp'] - 2, 'stop shown near top of viewport')
        await pg.click('#halfStop'); await pg.wait_for_timeout(200)
        r = await ev("()=>({d:getComputedStyle(document.querySelector('#halfStop')).display,e:halfEdit})"); print('STOP clicked', r); chk(r['d'] == 'none' and not r['e'], 'stop works')
        await tap('hedit'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        r = await ev("()=>halfEdit"); chk(not r, 'escape stops marking')
        print('errors', errs); chk(not errs, 'errors')
        await b.close()
    print('ALL OK' if ok else 'PROBLEMS')
asyncio.run(main())
