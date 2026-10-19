"""Processor compatibility: tile limits the processor list, Show all, receiving card, warning, unknown tiles unrestricted, persistence. Prints ALL OK."""
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
        opts = "()=>[...document.querySelectorAll('select[data-k=proc] option')].map(o=>o.value||o.textContent)"
        async def setk(k, v):
            await ev("""([k,v])=>{if(k=='preset'){const bs=document.querySelector('[data-brand]');if(bs&&bs.value!=brandOf(v)){bs.value=brandOf(v);bs.dispatchEvent(new Event('change',{bubbles:true}))}}const e=document.querySelector('[data-k='+k+']');if(e.type=='checkbox')e.checked=v;else e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}""", [k, v]); await pg.wait_for_timeout(150)
        # default tile (Unilumin) is unrestricted
        o = await ev(opts); chk(len(o) == len(await ev("()=>Object.keys(PROC)")) , 'unknown tile lists all ' + str(len(o)))
        chk('not' not in (await ev("()=>document.querySelector('#procInfo').textContent")).lower().split('no processor')[0], 'info')
        # Sierra: Megapixel + NovaStar only
        await setk('preset', 'ROE Sierra SR1.5'); o = await ev(opts); print(o)
        chk(any('HELIOS' in x for x in o) and any('NovaStar' in x for x in o) and not any('Tessera' in x for x in o) and not any('Evision' in x for x in o) and 'Custom' in o and 'None' in o, 'sierra list')
        # Meru: Megapixel + Brompton
        await setk('preset', 'ROE Meru MR2.6'); o = await ev(opts)
        chk(any('Tessera' in x for x in o) and any('HELIOS' in x for x in o) and not any('NovaStar' in x for x in o) and not any('eV4' in x for x in o), 'meru list')
        # Jet: all four
        await setk('preset', 'ROE Jet JT2.6 Half'); o = await ev(opts); chk(any('eV4' in x for x in o) and any('VX400' in x for x in o) and any('HELIOS' in x for x in o) and any('Tessera' in x for x in o), 'jet list')
        # receiving card narrows
        await setk('rcard', 'novastar'); o = await ev(opts); chk(all(('NovaStar' in x or x in ('None', 'Custom')) for x in o) and len(o) > 3, 'card narrows ' + str(o))
        rc = await ev("()=>[...document.querySelectorAll('#rcardSel option')].map(o=>o.value)"); chk(rc[0] == 'any' and len(rc) == 5, 'card options ' + str(rc))
        # tile changes to one without NovaStar: card resets, selected incompatible processor is kept with a warning
        await setk('rcard', 'any'); await setk('proc', 'NovaStar VX1000 Pro'); await setk('preset', 'ROE Meru MR2.6')
        chk(await ev("()=>S.proc")== 'NovaStar VX1000 Pro' and 'NovaStar VX1000 Pro' in await ev(opts), 'kept selected')
        w = await ev("()=>document.querySelector('#procWarn').textContent"); chk('not listed for' in w, 'warning ' + w)
        # show all
        await setk('procAll', True); o = await ev(opts); chk(len(o) == len(await ev("()=>Object.keys(PROC)")), 'show all')
        await setk('procAll', False)
        await setk('proc', 'HELIOS 8K'); chk(await ev("()=>document.querySelector('#procWarn').textContent") == '', 'no warning when compatible')
        # two walls: intersection
        await ev("()=>{document.querySelector('[data-a=wadd]')&&document.querySelector('[data-a=wadd]').click()}"); await pg.wait_for_timeout(200)
        n = await ev("()=>walls.length"); print('walls', n)
        if n > 1:
            await setk('preset', 'ROE Sierra SR1.5'); o = await ev(opts)
            chk(not any('Tessera' in x for x in o) and any('HELIOS' in x for x in o) and any('NovaStar' in x for x in o), 'list follows the selected tile ' + str(o))
            await setk('proc', 'NovaStar VX1000 Pro'); w = await ev("()=>document.querySelector('#procWarn').textContent")
            chk('Meru' in w, 'warning names the other wall ' + w)
        # persistence
        await setk('procAll', True); await setk('rcard', 'any'); await ev("()=>saveNow()"); await pg.reload(); await pg.wait_for_timeout(800)
        chk(await ev("()=>S.procAll===true"), 'persisted')
        chk(not errs, str(errs)); await b.close()
    print('ALL OK' if ok else 'SOME FAILED')
asyncio.run(main())
