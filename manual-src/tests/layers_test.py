# Layered pixel map export (top bar › Export layers): SVG with editable shapes and text, PSD with Photoshop layers
import asyncio, base64, io, os, xml.etree.ElementTree as ET
from PIL import Image, ImageChops
from playwright.async_api import async_playwright
APP = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tilesmith-desktop', 'app', 'index.html'))
SHOT = os.environ.get('LAYERS_SHOT')
INK = '{http://www.inkscape.org/namespaces/inkscape}'
SV = '{http://www.w3.org/2000/svg}'
ENC = "async b=>{const a=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<a.length;i+=32768)s+=String.fromCharCode.apply(null,a.subarray(i,i+32768));return btoa(s)}"

def png(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')
def bad(a, b, t=40):  # share of pixels that differ by more than t
    h = ImageChops.difference(a, b).convert('L').histogram(); return sum(h[t:]) / sum(h)

async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}, accept_downloads=True); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # two walls with tile IDs, positions, data and power runs, every tile built
        await pg.evaluate("""()=>{S.cols=8;S.rows=4;S.name='Main';storeWall();S.proc='NovaStar VX1000 Pro';applySpec();S.wmode='Snake';S.pdist=true;S.pmode='Snake';S.showData=true;S.showPow=true;S.ids=true;S.tpos=true;storeWall();
          addWall(false);S.name='Side';S.cols=3;S.rows=4;S.ox=1600;S.oy=0;storeWall();sync();sims.forEach(s=>{s.done=true});render()}""")
        r = await pg.evaluate("()=>({av:lyrAvail(),ports:portPlan().map(x=>x.length),circ:powerPlan().map(x=>x.length),flat:M.toDataURL('image/png')})")
        print('avail', r['av'], r['ports'], r['circ']); ok &= r['av'] == ['bg', 'pat', 'grid', 'lab', 'data', 'pow'] and all(r['ports']) and all(r['circ'])
        flat = png(r['flat'])
        for g, want in (('A', ['Background', 'Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths']),
                        ('B', ['Background', '</Layer group>', 'Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths', 'Main', '</Layer group>', 'Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths', 'Side']),
                        ('C', ['Background'] + sum([['</Layer group>', 'Main', 'Side', n] for n in ['Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths']], []))):
            r = await pg.evaluate(f"async()=>{{const e={ENC};return{{psd:await e(lyrPSD(lyrAvail(),'{g}')),svg:await lyrSVG(lyrAvail(),'{g}').text(),after:M.toDataURL('image/png')}}}}")
            im = Image.open(io.BytesIO(base64.b64decode(r['psd'])))
            names = [L[0] for L in im.layers]; empty = [L[0] for L in im.layers if L[2][2] <= L[2][0] and not L[0].startswith('</')]
            comp = im.convert('RGB'); d = bad(comp, flat, 30)
            print(g, 'psd', len(names), names == want, 'composite diff', d, 'size', len(r['psd']) * 3 // 4)
            ok &= names == want and comp.size == flat.size and d == 0
            if g == 'A': ok &= not empty  # every leaf draws something
            # each PSD layer lines up with the flat PNG where it is opaque (spot check: the grid layer)
            # the canvas is put back after the export
            ok &= bad(png(r['after']), flat, 1) == 0
            # SVG: top-level layers named like the PSD, editable shapes and text, the pattern as a picture
            root = ET.fromstring(r['svg']); top = [e for e in root if e.tag == SV + 'g']
            labs = [e.get(INK + 'label') for e in top]
            print(g, 'svg layers', labs)
            ok &= all(e.get(INK + 'groupmode') == 'layer' for e in root.iter(SV + 'g'))
            leaves = {e.get(INK + 'label'): e for e in root.iter(SV + 'g') if not e.findall(SV + 'g')}
            if g == 'A':
                ok &= labs == ['Background', 'Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths']
                ok &= len(leaves['Test pattern'].findall(SV + 'image')) == 1 and not leaves['Tile grid'].findall(SV + 'image')
                txt = [t.text for t in leaves['Tile labels'].iter(SV + 'text')]
                ok &= 'W1 T01 [C1:R1]' in txt and 'W2 T12 [C3:R4]' in txt
                ok &= any(t.text == 'P1' for t in leaves['Data paths'].iter(SV + 'text')) and len(list(leaves['Power paths'].iter(SV + 'path'))) > 10
                # the SVG drawn by the browser looks like the PNG (text anti-aliasing differs a little)
                v = await b.new_page(viewport={'width': flat.size[0], 'height': flat.size[1]})
                await v.set_content('<style>body{margin:0}</style>' + r['svg'].split('?>', 1)[1]); await v.wait_for_timeout(300)
                sv = Image.open(io.BytesIO(await v.screenshot())).convert('RGB'); await v.close(); d = bad(sv, flat)
                print('svg vs png', d); ok &= d < .03
            if g == 'B': ok &= labs == ['Background', 'Main', 'Side'] and len(top[1].findall(SV + 'g')) == 5
            if g == 'C': ok &= labs[1:] == ['Test pattern', 'Tile grid', 'Tile labels', 'Data paths', 'Power paths'] and all(len(e.findall(SV + 'g')) == 2 for e in top[1:])
        # the menu and dialog: turn Data off when the canvas does not show it; untick a layer; Save downloads the PSD
        await pg.evaluate("()=>{S.showData=false;sync()}")
        await pg.click('[data-a=lyrm]'); await pg.click('[data-a=lyr][data-v=psd]'); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({on:$('#lyrDlg').classList.contains('on'),boxes:[...document.querySelectorAll('#lyrList input')].map(i=>[i.dataset.ly,i.checked,i.disabled]),fmt:document.querySelector('[data-lf=psd]').classList.contains('on')})")
        print('dialog', r); ok &= r['on'] and r['fmt'] and ['data', False, True] in r['boxes'] and ['pow', True, False] in r['boxes']
        if SHOT: await pg.screenshot(path=SHOT)
        await pg.uncheck('#lyrList input[data-ly=lab]')
        async with pg.expect_download() as dl: await pg.click('[data-a=lyrgo]')
        f = await (await dl.value).path(); n = (await dl.value).suggested_filename
        im = Image.open(f); names = [L[0] for L in im.layers]; print('download', n, names)
        ok &= n == 'tilesmith-layers.psd' and names == ['Background', 'Test pattern', 'Tile grid', 'Power paths']
        r = await pg.evaluate("()=>({off:S.lyrOff,on:$('#lyrDlg').classList.contains('on')})"); print('remembered', r); ok &= r['off'] == ['lab'] and not r['on']
        # Spanish layer names (accents kept in the Unicode name Photoshop shows)
        r = await pg.evaluate(f"async()=>{{LG='es';TR_C.clear();const e={ENC};const s=await lyrSVG(['bg','grid','pow'],'A').text();const p=await e(lyrPSD(['bg','grid','pow'],'A'));LG='en';TR_C.clear();return{{s,p}}}}")
        labs = [e.get(INK + 'label') for e in ET.fromstring(r['s']) if e.tag == SV + 'g']; print('es', labs); ok &= labs == ['Fondo', 'Cuadrícula de paneles', 'Rutas de alimentación']
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
