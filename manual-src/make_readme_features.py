# Feature screenshots for the README "What's new" section, taken from the running app:
#   python3 make_readme_features.py <app index.html> <output folder>
# Writes one PNG per feature (power-distros, cable-fibre, redundancy, rigging, cabinet-ids, locations, tile-faults, tile-catalog).
import asyncio, sys, os
from playwright.async_api import async_playwright
APP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '../tilesmith-desktop/app/index.html')
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'readme-shots')
os.makedirs(OUT, exist_ok=True)

# open the side-panel sections whose titles start with these names (and their parents); close all others
OPEN = """(names)=>{document.querySelectorAll('#left details').forEach(d=>d.open=false);
 for(const n of names){const d=[...document.querySelectorAll('#left details')].find(x=>x.querySelector(':scope>summary').textContent.trim().startsWith(n));
  if(d)for(let e=d;e;e=e.parentElement)if(e.tagName=='DETAILS')e.open=true}}"""
# scroll the side panel so the first open section with this title is at the top
SCROLL = """(n)=>{const d=[...document.querySelectorAll('#left details')].find(x=>x.querySelector(':scope>summary').textContent.trim().startsWith(n));if(d)d.scrollIntoView({block:'start'})}"""
# the same two-wall show every shot starts from
BASE = """()=>{S.cw=3000;S.ch=1500;S.preset='ROE Black Pearl BP2V2';applyPreset();S.name='Main';S.cols=12;S.rows=6;S.ox=850;S.oy=220;S.pat='tileshade';S.ids=true;storeWall();
 addWall(false);S.name='IMAG Left';S.cols=4;S.rows=6;S.ox=60;S.oy=220;S.pat='tileshade';storeWall();
 S.proc='NovaStar VX1000 Pro';applySpec();walls.forEach(w=>{w.wmode='Snake';w.pmode='Snake'});S.wmode='Snake';S.pmode='Snake';S.showData=true;storeWall();
 selWall(0);showAll();sync();fit()}"""

async def shot(pg, name, setup, open_names, scroll=None, wait=1200, eng=None):
    await pg.evaluate(setup)
    await pg.evaluate(OPEN, open_names)
    if scroll: await pg.evaluate(SCROLL, scroll)
    await pg.evaluate("()=>{sync();fit()}")
    await pg.wait_for_timeout(wait)
    if eng: await pg.evaluate("(q)=>{const e=document.querySelector(q);if(e)e.scrollIntoView({block:'start'})}", eng); await pg.wait_for_timeout(300)
    await pg.screenshot(path=os.path.join(OUT, name + '.png'))
    print('wrote', name + '.png')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        async def fresh():
            pg = await b.new_page(viewport={'width': 1600, 'height': 960}, device_scale_factor=1)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(900)
            await pg.evaluate(BASE); return pg
        pg = await fresh()
        await shot(pg, 'power-distros', """()=>{S.pdist=true;S.showPow=true;S.showData=false;distAct('dadd');distAct('dadd');S.phaseView=true;S.autoBal=true;storeWall();sync()}""",
                   ['Power', 'Distros'], 'Distros')
        await pg.close(); pg = await fresh()
        await shot(pg, 'cable-fibre', """()=>{S.cabOn=true;S.cunit='m';S.cslack=10;selWall(0);S.cdD=140;S.cdP=20;S.wfib='Auto';storeWall();selWall(1);S.cdD=30;S.cdP=15;storeWall();selWall(0);sync()}""",
                   ['Cable lengths'], 'Cable lengths')
        await pg.close(); pg = await fresh()
        await shot(pg, 'redundancy', """()=>{S.cabOn=true;selWall(0);S.wred='Full';S.cdD=140;storeWall();selWall(1);S.wred='Loop';storeWall();selWall(0);S.gOn=false;sync()}""",
                   ['LED processor'], 'LED processor', eng='details[data-eng="sig"]')
        await pg.close(); pg = await fresh()
        await shot(pg, 'rigging', """()=>{selWall(1);delWall();selWall(0);S.ox=200;S.rigOn=true;S.bmode='Flown from truss';S.tsec='1, 2, 3';S.thn=3;S.tex=0.5;storeWall();sync()}""",
                   ['Rigging'], 'Rigging')
        await pg.close(); pg = await fresh()
        await shot(pg, 'cabinet-ids', """()=>{S.pports=4;storeWall();walls.forEach(w=>w.pat='cabinet IDs');S.pat='cabinet IDs';storeWall();sync()}""",
                   ['Cabinet IDs'], 'Cabinet IDs')
        await pg.close(); pg = await fresh()
        await shot(pg, 'locations', """()=>{zAdd();zAdd();S.zones[0].name='Stage';S.zones[1].name='FOH';selWall(0);S.zone=S.zones[0].id;storeWall();selWall(1);S.zone=S.zones[1].id;storeWall();S.zProc=S.zones[1].id;selWall(0);sync()}""",
                   ['Locations'], 'Locations')
        await pg.close(); pg = await fresh()
        await shot(pg, 'tile-faults', """()=>{S.glType='Random mix';S.glPick='Random';S.glN=6;sync();glGo();sync()}""",
                   ['Tile faults'], 'Tile faults', wait=2000)
        await pg.close(); pg = await fresh()
        await pg.evaluate(OPEN, ['Tile model'])
        await pg.evaluate(SCROLL, 'Tile model')
        await pg.fill('#tFind', 'AR3.9'); await pg.wait_for_timeout(300)
        await shot(pg, 'tile-catalog', "()=>{}", ['Tile model'], 'Tile model')
        await b.close()
        assert not errs, errs
asyncio.run(main())
