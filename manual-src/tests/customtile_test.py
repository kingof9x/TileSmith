import asyncio, json
from playwright.async_api import async_playwright
APP='file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1500,'height':1100}); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        ev=pg.evaluate
        # editing a built-in model turns it into Custom, brand menu says Custom, save box shows
        await ev("()=>{brandPick('Absen');const e=document.querySelector('[data-k=kg]');e.value='9.9';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
        r=await ev("()=>[S.preset,document.querySelector('[data-brand]').value,getComputedStyle(document.querySelector('#utBox')).display,!!UT[S.preset],JSON.parse(localStorage.getItem('tilesmith-tiles-v1'))[S.preset]]"); print(r)
        assert r[0]=='Polaris PL2.5 Pro (custom)' and r[1]=='Custom' and r[2]!='none' and r[3] and r[4][5]==9.9,r
        # a second change updates the same tile instead of making another
        await ev("()=>{const e=document.querySelector('[data-k=wmax]');e.value='150';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
        assert await ev("()=>Object.keys(UT).length==1&&UT[S.preset][6]==150")
        # rename it
        await ev("()=>{const e=document.querySelector('#utName');e.value='Venue Panel 2.9';document.querySelector('[data-a=utsave]').click()}"); await pg.wait_for_timeout(200)
        assert await ev("()=>!UT['Polaris PL2.5 Pro (custom)']&&walls[cur].preset=='Venue Panel 2.9'")
        await ev("()=>{const e=document.querySelector('[data-k=wmax]');e.value='128';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
        r=await ev("()=>[S.preset,P['Venue Panel 2.9'],JSON.parse(localStorage.getItem('tilesmith-tiles-v1'))['Venue Panel 2.9'][5],[...document.querySelectorAll('[data-k=preset] option')].map(o=>o.value)]"); print(r)
        assert r[0]=='Venue Panel 2.9' and r[2]==9.9 and 'Venue Panel 2.9' in r[3]
        # built-in name refused / brand prefix gets My
        await ev("()=>{S.preset='Custom';sync();const e=document.querySelector('#utName');e.value='ROE Foo';document.querySelector('[data-a=utsave]').click()}")
        assert await ev("()=>!!UT['My ROE Foo']")
        # project carries the tile
        proj=await ev("()=>{S.preset='Venue Panel 2.9';applyPreset();storeWall();return JSON.stringify(stateObj())}"); o=json.loads(proj); assert 'Venue Panel 2.9' in o['ut'] and 'My ROE Foo' not in o['ut'],o['ut'].keys()
        # a fresh instance (empty storage) opens the project
        pg2=await ctx.new_page(); await pg2.goto(APP); await pg2.evaluate("()=>localStorage.clear()"); await pg2.reload(); await pg2.wait_for_timeout(800)
        r=await pg2.evaluate("(j)=>{openProject(JSON.parse(j),'t');return [S.preset,S.kg,!!UT[S.preset],document.querySelector('[data-brand]').value,[...document.querySelectorAll('[data-k=preset] option')].map(o=>o.value)]}",proj); print(r)
        assert r[0]=='Venue Panel 2.9' and r[1]==9.9 and r[2] and r[3]=='Custom' and 'Venue Panel 2.9' in r[4]
        # name clash with a different local preset: both kept
        o2=json.loads(proj); o2['ut']['Venue Panel 2.9']=[500,500,128,128,3.9,5.5,100,60]
        o2['S']['preset']='Venue Panel 2.9'; o2['walls'][0]['preset']='Venue Panel 2.9'
        r=await ev("(j)=>{openProject(JSON.parse(j),'t');return [S.preset,S.kg,Object.keys(UT)]}",json.dumps(o2)); print(r)
        assert r[0]=='Venue Panel 2.9 (from project)' and r[1]==5.5 and 'Venue Panel 2.9' in r[2]
        # delete
        await ev("()=>{S.preset='Venue Panel 2.9';sync();document.querySelector('[data-a=utdel]').click()}")
        assert await ev("()=>!UT['Venue Panel 2.9']&&S.preset=='Custom'")
        assert not errs,errs
        print('ALL OK'); await b.close()
asyncio.run(main())
