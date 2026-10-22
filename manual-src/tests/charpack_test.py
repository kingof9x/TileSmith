# Character packs: the built-in Khalid pack, loading your own pack (zip or loose PNGs), storage, projects, per crew member.
import asyncio, sys, os, json, base64, io, zipfile, tempfile
from PIL import Image
from playwright.async_api import async_playwright
APP = '/home/claude/tilesmith-desktop/app/index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + APP); await pg.evaluate("()=>{localStorage.clear();indexedDB.deleteDatabase('tilesmith-packs')}"); await pg.reload(); await pg.wait_for_timeout(800)
        ok = True
        await pg.evaluate("()=>{window.NB=[...PK.values()].filter(r=>r.builtin).length}")
        def chk(c, m):
            nonlocal ok
            print(('PASS ' if c else 'FAIL ') + m); ok = ok and c
        chk('Character pack' in await pg.evaluate("()=>[...document.querySelector('[data-k=tstyle]').options].map(o=>o.value)"), 'style list has Character pack')
        names = await pg.evaluate("()=>[...PK.values()].filter(r=>r.builtin).map(r=>r.name)")
        chk(names == ['Khalid', 'Yuki', 'Kenji', 'Maria'], f'four built-in characters {names}')
        k = await pg.evaluate("()=>{const r=PK.get('builtin-khalid');return r?{n:Object.keys(r.files).filter(x=>!x.includes('~')).length,views:[...new Set(Object.keys(r.files).map(x=>x.split('/')[0]))].sort(),b:!!r.builtin}:null}")
        chk(k and k['n'] == 24 and k['views'] == ['back', 'front', 'three_quarter'] and k['b'], f'built-in Khalid present {k}')
        await pg.evaluate("()=>{const e=document.querySelector('[data-k=tstyle]');e.value='Character pack';e.dispatchEvent(new Event('input',{bubbles:true}))}")
        chk(await pg.evaluate("()=>getComputedStyle(document.getElementById('pkBox')).display!='none'&&S.tpack=='builtin-khalid'"), 'Character pack picks Khalid by default')
        chk(await pg.evaluate("()=>getComputedStyle(document.querySelector('[data-a=pkdel]')).display=='none'"), 'built-in pack cannot be deleted from the menu')
        await pg.evaluate("()=>{S.cols=4;S.rows=3;storeWall();showAll();sync();fit();reset();S.play=true}")
        seen = set()
        for i in range(60):
            await pg.evaluate("()=>{for(let k=0;k<20;k++)step(1/60);forceRen=true}"); await pg.wait_for_timeout(25); seen.add(await pg.evaluate("()=>sims[0].ph"))
        chk(len(seen) >= 4, f'build phases ran with Khalid {sorted(seen)}')
        used = await pg.evaluate("()=>{let n=0;const o=workerPack;window.workerPack=function(){n++;return o.apply(this,arguments)};drawTech(document.createElement('canvas').getContext('2d'),100,100,100,{th:1,mv:0,m:crew[0],ix:0,hands:null});return n}")
        chk(used == 1, 'technician is drawn from the pack')
        chk(await pg.evaluate("()=>Object.keys(pkForProject()).length") == 0, 'built-in pack is not copied into projects')
        # a user pack: Khalid's images re-saved as PNG in a zip with folders per view
        files = await pg.evaluate("()=>Object.fromEntries(Object.entries(PK.get('builtin-khalid').files).filter(([k])=>!k.includes('~')))")
        tmp = tempfile.mkdtemp(); zp = os.path.join(tmp, 'Copy.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for key, url in files.items():
                im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).convert('RGBA'); bb = io.BytesIO(); im.save(bb, 'PNG')
                z.writestr('Copy/' + key + '.png', bb.getvalue())
            z.writestr('Copy/pack.json', '{"name":"Test copy"}')
        n0 = await pg.evaluate('()=>PK.size'); await pg.set_input_files('#pkf', zp); await pg.wait_for_function(f'()=>PK.size>{n0}', timeout=20000); await pg.wait_for_timeout(1500)
        info = await pg.evaluate("()=>{const r=PK.get(S.tpack);return r?{name:r.name,n:Object.keys(r.files).length,b:!!r.builtin}:null}")
        chk(info and info['n'] == 24 and info['name'] == 'Test copy' and not info['b'], f'zip loaded as a new pack {info}')
        chk(await pg.evaluate("()=>getComputedStyle(document.querySelector('[data-a=pkdel]')).display!='none'"), 'your own pack can be deleted')
        await pg.reload(); await pg.wait_for_timeout(1500); await pg.evaluate("()=>{window.NB=[...PK.values()].filter(r=>r.builtin).length}")
        chk(await pg.evaluate("()=>PK.size==NB+1&&PK.has(S.tpack)&&!PK.get(S.tpack).builtin"), 'your pack kept on the device after reload')
        # per crew member
        await pg.evaluate("()=>{S.cd=true;sync();crewUI()}")
        chk(await pg.evaluate("()=>document.querySelectorAll('#crew select[data-f=\"4\"]').length==crew.length"), 'each crew member has a pack picker')
        await pg.evaluate("()=>{const own=S.tpack;S.tpack='builtin-khalid';sync();crewUI();const s=document.querySelector('#crew select[data-f=\"4\"]');s.value=own;s.dispatchEvent(new Event('input',{bubbles:true}));window.OWN=own}")
        chk(await pg.evaluate("()=>pkFor(crew[0])==OWN&&pkFor(crew[1])=='builtin-khalid'"), 'each crew member can have their own pack')
        await pg.evaluate("()=>{S.tstyle='Classic';sync();crewUI()}")
        chk(await pg.evaluate("()=>crew.every(c=>pkFor(c)=='')&&document.querySelectorAll('#crew select[data-f=\"4\"]').length==0"), 'Classic draws the Classic technician for everyone and hides the pack pickers')
        chk(await pg.evaluate("()=>crew[0][4]==OWN"), 'the crew member keeps their pack choice for when Character pack is picked again')
        await pg.evaluate("()=>{S.tstyle='Character pack';sync()}")
        proj = await pg.evaluate("()=>{const o=stateObj();o.rc=rcForProject();o.pk=pkForProject();return JSON.stringify(o)}")
        chk(len(json.loads(proj)['pk']) == 1, 'project carries your pack')
        await pg.evaluate("()=>{indexedDB.deleteDatabase('tilesmith-packs');localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(1000)
        chk(await pg.evaluate("()=>PK.size") == 4, 'clean device has only the four built-in packs')
        await pg.evaluate("()=>{window.NB=[...PK.values()].filter(r=>r.builtin).length}"); await pg.evaluate("(s)=>applyState(JSON.parse(s))", proj); await pg.wait_for_timeout(500)
        chk(await pg.evaluate("()=>PK.size==NB+1&&pkFor(crew[0])!=''"), 'opening the project adds the pack and the crew assignment')
        # loose PNG files with view prefixes
        paths = []
        for key, url in list(files.items())[:12]:
            fn = os.path.join(tmp, key.replace('/', '_') + '.png'); Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).convert('RGBA').save(fn); paths.append(fn)
        n0 = await pg.evaluate('()=>PK.size'); await pg.set_input_files('#pkf', paths); await pg.wait_for_function(f'()=>PK.size>{n0}', timeout=20000)
        chk(await pg.evaluate("()=>PK.size==NB+2&&Object.keys(PK.get(S.tpack).files).length==12"), 'loose PNG files load as a pack')
        await pg.evaluate("()=>pkDel()")
        chk(await pg.evaluate("()=>PK.size==NB+1"), 'delete removes your pack')
        await pg.evaluate("()=>{S.tpack='builtin-khalid';pkDel()}")
        chk(await pg.evaluate("()=>PK.has('builtin-khalid')"), 'built-in pack survives delete')
        await pg.evaluate("()=>{S.tstyle='Character pack';S.tpack='builtin-khalid';S.cd=true;sync();crewUI()}")
        chk(await pg.evaluate("()=>document.querySelectorAll('#crew input[type=color]').length==0&&document.querySelectorAll('#crew [data-face]').length==0"), 'skin, hair and face photo hidden when every crew member uses a pack')
        await pg.evaluate("()=>{S.tstyle='Classic';sync();crewUI()}")
        chk(await pg.evaluate("()=>document.querySelectorAll('#crew input[type=color]').length==crew.length*2"), 'skin and hair shown for every crew member with Classic')
        px = await pg.evaluate("""async()=>{S.tstyle='Character pack';S.tpack='builtin-khalid';const P=pkLoad('builtin-khalid');await new Promise(r=>setTimeout(r,800));
          const f=c=>{S.vest=c;const im=pkTint('builtin-khalid',P,'front','torso',P.img.front.torso),g=document.createElement('canvas');g.width=im.width;g.height=im.height;const x=g.getContext('2d');x.drawImage(im,0,0);
            const d=x.getImageData(0,0,g.width,g.height).data;let r=0,gr=0,n=0;for(let i=0;i<d.length;i+=4)if(d[i+3]>200){r+=d[i];gr+=d[i+1];n++}return[r/n,gr/n]};
          return [f('#ff6a00'),f('#b6ff00')]}""")
        chk(px[1][1] > px[0][1] + 15, f'vest colour setting recolours the pack art {px}')
        chk(not errs, f'no page errors {errs[:3]}')
        await b.close(); print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
asyncio.run(main())
