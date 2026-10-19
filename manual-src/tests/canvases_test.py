# Several canvases: add / duplicate / remove, select by click, save + open, undo, New Project, per-canvas outputs (NDI / Syphon mocked), PNG, PDF
import asyncio, json
from playwright.async_api import async_playwright
APP='file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1500,'height':1000},accept_downloads=True); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)
        ev=pg.evaluate; ok=True
        def chk(c,m):
            nonlocal ok
            if not c: ok=False; print('FAILED',m)
        r=await ev("()=>[CVS.length,document.querySelectorAll('#left details[open]').length]"); chk(r==[1,0],'one canvas, all menus collapsed '+str(r))
        await ev("()=>{document.querySelectorAll('#left>details').forEach(d=>d.open=true)}")
        await pg.click('[data-a=cvadd]'); await pg.wait_for_timeout(300)
        await ev("()=>{S.cw=1280;S.ch=720;S.cols=4;S.rows=2;storeWall();showAll();sync()}")
        await pg.fill('#cvName','Side screen'); await pg.wait_for_timeout(200)
        r=await ev("()=>[CVS.length,cc,CVS[1].name,document.querySelector('[data-cvs=\"1\"]').textContent]"); chk(r[0]==2 and r[1]==1 and r[2]=='Side screen' and 'Side screen' in r[3],'add + name '+str(r))
        # click the first canvas in the viewport selects it, keeps its own walls and size
        xy=await ev("()=>{const L=cvLay(),a=L[cc],p=L[0],r=vp.getBoundingClientRect();return [r.left+V.x+(p.x-a.x+p.w*.98)*V.z, r.top+V.y+(p.y-a.y+p.h*.95)*V.z]}")
        await pg.mouse.click(xy[0],xy[1]); await pg.wait_for_timeout(300)
        r=await ev("()=>[cc,S.cw,S.ch,walls[0].cols,CVS[1].cw,CVS[1].walls[0].cols]"); chk(r==[0,1920,1080,6,1280,4],'select by click '+str(r))
        # duplicate, then remove
        await pg.click('[data-a=cvdup]'); r=await ev("()=>[CVS.length,cc,CVS[2].name,walls[0].cols]"); chk(r==[3,2,'Canvas 1 copy',6],'duplicate '+str(r))
        await pg.click('[data-a=cvdel]')
        r=await ev("()=>[CVS.length,cc]"); chk(r[0]==2,'remove '+str(r))
        # every canvas animates and renders
        await ev("()=>{eachCv(()=>reset());S.play=true}"); await pg.wait_for_timeout(1500)
        r=await ev("()=>CVS.map((c,i)=>withCv(i,()=>sims.some(x=>x.inst>0||x.ph!='wait')))"); chk(all(r),'all canvases build '+str(r))
        await ev("()=>{eachCv(()=>showAll())}")
        # save / open round trip keeps both canvases
        st=await ev("()=>JSON.stringify(stateObj())"); o=json.loads(st); chk(len(o['cvs'])==2 and o['cvs'][1]['name']=='Side screen','saved '+str([c['name'] for c in o['cvs']]))
        await ev("()=>newCanvas()"); chk(await ev("()=>CVS.length")==1,'new project = one canvas')
        await ev("(j)=>openProject(JSON.parse(j),'t')",st); await pg.wait_for_timeout(200)
        r=await ev("()=>[CVS.length,CVS.map(c=>c.name),CVS[1].cw,CVS[1].walls[0].cols]"); chk(r==[2,['Canvas 1','Side screen'],1280,4],'open '+str(r))
        # undo the canvas removal
        await ev("()=>{document.querySelectorAll('#left>details').forEach(d=>d.open=true);switchTo(1);CVS[1].open=true;document.querySelector('[data-cvd=\"1\"]').open=true;unBase()}"); await pg.click('[data-a=cvdel]'); await pg.wait_for_timeout(100)
        await ev("()=>unUndo(1)"); r=await ev("()=>[CVS.length,CVS.map(c=>c.name)]"); chk(r[0]==2,'undo remove '+str(r))
        # outputs: one NDI source + one Syphon server per canvas (mocked libraries)
        r=await ev("""()=>{window.Buffer=window.Buffer||{from:x=>x};const names=[],sent=[];NL={destroy(){}};const L={create:o=>{names.push(o.p_ndi_name);return {n:o.p_ndi_name}},send:(i,f)=>sent.push(i.n+' '+f.xres+'x'+f.yres)};
          ndiBegin(L,L.create({p_ndi_name:S.ndiName||'TileSmith-LED-Out'}));forceRen=true;tick(performance.now());ndiFrame();const out={names,sent:[...new Set(sent)],msg:(document.querySelector('#ndis')||{}).textContent};ndiStop();
          const sv=[];SHL={A:{MetalServer:function(n){sv.push(n);this.hasClients=true;this.publishImageData=()=>{};this.dispose=()=>{}}}};
          shOut={kind:'Syphon',name:'TS',n:0,tot:0,per:new Map([[CVS[0],{srv:new SHL.A.MetalServer('TS'),sent:-1,fail:0,tot:0}]])};shFrame();out.sy=sv;shOut.st=0;shStop();return out}""")
        print(r); chk(len(r['names'])==2 and ' - Side screen' in r['names'][1] and len(r['sent'])==2 and r['sy']==['TS','TS - Side screen'],'per-canvas outputs')
        # PNG: one file per canvas
        names=[]
        pg.on('download',lambda d:names.append(d.suggested_filename))
        await pg.evaluate("()=>document.querySelector('[data-a=png]').click()"); await pg.wait_for_timeout(1500)
        print(names); chk(sorted(names)==['tilesmith-canvas-Canvas_1.png','tilesmith-canvas-Side_screen.png'],'png per canvas')
        # PDF: a raster page per canvas
        names.clear()
        async with pg.expect_download() as d: await pg.evaluate("()=>exportPDF()")
        dl=await d.value; data=open(await dl.path(),'rb').read(); n=data.count(b'full raster')
        print('raster pages',n); chk(n==2,'pdf raster per canvas')
        chk(not errs,'errors '+str(errs[:3]))
        print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
