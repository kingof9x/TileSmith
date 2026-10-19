# Screenshots for the GitHub README, taken from the running app:
#   python3 make_readme_shots.py <app index.html> <output folder>
# wiring.png (data + power wiring), dvd-smpte.png (DVD screensaver on SMPTEbars), build.gif (LED build half done, a tech placing a row)
import asyncio, sys, os, subprocess, shutil, tempfile
from playwright.async_api import async_playwright
APP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '../tilesmith-desktop/app/index.html'); OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'readme-shots')
os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 960}, device_scale_factor=1)
        await pg.goto('file://' + APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(900)
        ev = pg.evaluate
        open_sec = """(names)=>{for(const n of names){const d=[...document.querySelectorAll('#left details')].find(x=>x.querySelector('summary').textContent.trim().startsWith(n));if(d)for(let e=d;e;e=e.parentElement&&e.parentElement.closest('details'))e.open=true}}"""
        # 1. wiring: two walls, data paths and power circuits
        await ev("""()=>{S.preset='ROE Black Pearl BP2V2';applyPreset();S.name='Main';S.cols=6;S.rows=5;S.ox=0;S.oy=0;S.pat='tileshade';S.ids=true;storeWall();showAll();
          addWall(false);S.name='Side';S.pat='tileshade';S.cols=4;S.rows=5;S.ox=1100;S.oy=0;storeWall();showAll();
          S.proc='Brompton Tessera S8';applySpec();S.showData=true;S.pdist=true;S.showPow=true;walls.forEach(w=>{w.wmode='Snake';w.pmode='Snake';w.pfill='Fewest circuits'});S.wmode='Snake';S.pmode='Snake';storeWall();sync();fit()}""")
        await ev(open_sec, ['Engineering', 'Data wiring', 'Power wiring']); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=os.path.join(OUT, 'wiring.png'))
        # 2. DVD screensaver over SMPTE bars
        await ev("""()=>{selWall(1);delWall();S.showData=false;S.showPow=false;S.ids=false;S.tpos=false;S.cols=10;S.rows=6;S.pat='SMPTEbars';S.dvdOn=true;S.dvdSize=22;storeWall();showAll();sync();fit();
          document.querySelectorAll('#left details').forEach(d=>d.open=false)}""")
        await ev(open_sec, ['Animation Options', 'DVD screensaver']); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=os.path.join(OUT, 'dvd-smpte.png'))
        # 3. the LED build half done: frames of the viewport while a tech places a row
        await ev("""()=>{S.dvdOn=false;S.pat='tileshade';S.ids=true;S.tpos=true;S.cols=8;S.rows=5;storeWall();showAll();sync();fit();document.querySelectorAll('#left details').forEach(d=>d.open=false);
          reset();S.play=true;for(let i=0;i<60*900&&sims[0].i<17;i++)step(1/60);forceRen=true}""")
        await ev(open_sec, ['Animation Options', 'LED build'])
        tmp = tempfile.mkdtemp(); clip = await ev("()=>{const r=document.querySelector('#vp').getBoundingClientRect(),w=walls[0],x=r.left+V.x+(w.ox-20)*V.z,y=r.top+V.y+(w.oy-20)*V.z;return {x:Math.max(r.left,x),y:Math.max(r.top,y),width:Math.min(r.width,(wW(w)+40)*V.z),height:Math.min(r.height,(wH(w)+40)*V.z)}}")
        for i in range(80):
            await pg.screenshot(path=os.path.join(tmp, f'f{i:03d}.png'), clip=clip); await pg.wait_for_timeout(70)
        await b.close()
    pal = os.path.join(tmp, 'pal.png'); vf = 'fps=10,scale=800:-1:flags=lanczos'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', os.path.join(tmp, 'f%03d.png'), '-vf', vf + ',palettegen=max_colors=128', pal], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', os.path.join(tmp, 'f%03d.png'), '-i', pal, '-lavfi', vf + '[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4', os.path.join(OUT, 'build.gif')], check=True)
    shutil.rmtree(tmp)
asyncio.run(main())
