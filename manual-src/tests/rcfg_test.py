# NovaStar receiving card files: add to the library under Tile details, per-wall pick, vendor/revision, library survives reload,
# saved project carries the file, a fresh app imports it, the processor config zip includes it, delete
import asyncio, json, zipfile, io, os
from playwright.async_api import async_playwright
APP='file:///home/claude/tilesmith-desktop/app/index.html'
RC=os.environ.get('RCFG','/tmp/res/novastar/cfg/Q8_ICND2153_40x40.rcfgx')
async def main():
    ok=True
    def chk(c,m):
        nonlocal ok
        if not c: ok=False; print('FAILED',m)
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1500,'height':1100},accept_downloads=True); pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("async()=>{localStorage.clear();await new Promise(r=>{const q=indexedDB.deleteDatabase('tilesmith-rcfg');q.onsuccess=q.onerror=q.onblocked=()=>r()})}"); await pg.reload(); await pg.wait_for_timeout(800)
        ev=pg.evaluate
        await ev("()=>{S.preset='ROE Black Pearl BP2V2';applyPreset();S.cols=4;S.rows=3;storeWall();showAll();sync();document.querySelectorAll('#left details').forEach(d=>d.open=true)}")
        await pg.set_input_files('#rcf',RC); await pg.wait_for_timeout(600)
        r=await ev("()=>[S.rcfg.length,[...RC.values()].map(x=>[x.name,x.models,x.size]),document.querySelector('#rcSel').value===S.rcfg]"); print(r); chk(r[0]==64 and r[1][0][1]==['ROE Black Pearl BP2V2'] and r[2],'added + selected')
        await pg.fill('#rcVend','Acme Rentals'); await pg.fill('#rcRev','B'); await pg.wait_for_timeout(600)
        chk(await ev("()=>{const x=RC.get(S.rcfg);return x.vendor=='Acme Rentals'&&x.revision=='B'&&wallRows(walls[cur]).some(r=>r[0]=='Receiving card file'&&r[1].includes('Acme'))}"),'metadata + engineering row')
        # second wall of the same model picks None, then the same file
        await ev("()=>{addWall(false);S.rcfg='';storeWall();sync()}"); chk(await ev("()=>[...document.querySelectorAll('#rcSel option')].length==2"),'per-wall list')
        # library survives a reload (IndexedDB)
        await ev("()=>saveNow()"); await pg.reload(); await pg.wait_for_timeout(1200)
        r=await ev("()=>[RC.size,walls[0].rcfg.length,[...RC.values()][0].vendor]"); print('after reload',r); chk(r==[1,64,'Acme Rentals'],'library persisted')
        # saved project carries the file
        async with pg.expect_download() as d: await ev("()=>saveProject()")
        proj=json.loads(open(await (await d.value).path()).read()); chk(len(proj.get('rc',{}))==1 and len(list(proj['rc'].values())[0]['data'])>1000,'project carries the file')
        # a fresh app (empty library) opening the project imports it
        pg2=await ctx.new_page(); await pg2.goto(APP); await pg2.evaluate("async()=>{await new Promise(r=>{const q=indexedDB.deleteDatabase('tilesmith-rcfg');q.onsuccess=q.onerror=q.onblocked=()=>r()})}"); await pg2.reload(); await pg2.wait_for_timeout(800)
        # (same origin shares IndexedDB in this test, so clear the in-memory library to simulate another computer)
        r=await pg2.evaluate("async(j)=>{RC.clear();openProject(JSON.parse(j),'t');await new Promise(r=>setTimeout(r,500));const x=RC.get(walls[0].rcfg);return [RC.size,x&&x.vendor,x&&x.data.length]}",json.dumps(proj)); print('imported',r); chk(r[0]==1 and r[1]=='Acme Rentals' and r[2]>1000,'imported into library')
        # processor config zip includes it
        await ev("()=>{S.proc='Brompton Tessera S8';applySpec();walls.forEach(w=>w.wmode='Snake');S.wmode='Snake';storeWall();sync()}")
        async with pg.expect_download() as d: await ev("()=>exportConfig()")
        z=zipfile.ZipFile(io.BytesIO(open(await (await d.value).path(),'rb').read())); n=z.namelist(); print(n)
        rc=[x for x in n if x.endswith('.rcfgx')]; chk(len(rc)==1 and z.read(rc[0])==open(RC,'rb').read() and 'receiving-card-files/README.txt' in n,'config zip has the file byte-identical')
        # delete
        await ev("()=>{loadWall(0);sync();document.querySelector('[data-a=rcdel]').click()}"); chk(await ev("()=>RC.size==0&&walls.every(w=>!w.rcfg)"),'deleted')
        chk(not errs,str(errs)); print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
