# Rigging (Engineering › Rigging): hang method = Build mode, bumpers / truss / ground bases, parts rules, loads, pull sheet
import asyncio, json
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1500, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(600)
        # off by default: no rigging rows or pull sheet lines
        r = await pg.evaluate("()=>{S.cols=12;S.rows=6;storeWall();sync();return{rows:rigRows(walls[0]).length,dep:pullItems().map(d=>d[0]),eng:document.querySelector('#right').innerHTML.includes('Total weight with rigging')}}")
        print('off', r); ok &= r['rows'] == 0 and 'Rigging' not in r['dep'] and not r['eng']
        # flown from motors: 6 two-tile bumpers, 12 hoists, load shared evenly
        r = await pg.evaluate("""()=>{S.rigOn=true;S.bmode='Flown from motors';S.rbw=2;S.rpts=2;S.rbkg=9;S.rwll=500;storeWall();sync();const w=walls[0],c=rigCalc(w),st=wst(w);
          return{hp:c.hp,kg:c.kg,tk:st.kg,pull:c.pull,rows:c.rows,eng:document.querySelector('#right').innerHTML.includes('Total weight with rigging'),fly:isFly(w)}}""")
        print('motors', json.dumps({k: r[k] for k in ['hp', 'kg', 'tk', 'pull']}))
        ok &= r['hp'] == 12 and r['kg'] == 54 and r['eng'] and r['fly'] and ['Bumper, 2 tiles wide', 6] in r['pull'] and ['Hoist / chain motor (500 kg)', 12] in r['pull']
        load = [x[1] for x in r['rows'] if x[0] == 'Load per hoist'][0]; exp = (r['tk'] + 54) / 12; print(' ', load); ok &= load.startswith(f'{exp:.1f} kg')
        # over the hoist rating: warning
        r = await pg.evaluate("()=>{S.rwll=20;storeWall();return rigCalc(walls[0]).rows.filter(x=>x[2]=='warn').map(x=>x[0])}"); print('over', r); ok &= r == ['Hoist over its rating']
        # flown from truss: span 6 m + 2 x 0.5 m = 7 m from 3, 3, 1; 3 hoists; slings and shackles per pickup
        r = await pg.evaluate("""()=>{S.rwll=500;S.bmode='Flown from truss';S.tsec='1, 2, 3';S.tkgm=8;S.thn=3;S.tex=0.5;storeWall();sync();const c=rigCalc(walls[0]);return{hp:c.hp,kg:c.kg,pull:c.pull,isFly:isFly(walls[0]),
          note:document.querySelector('#bmodeNote').textContent,truss:document.querySelector('#rigTruss').style.display}}""")
        print('truss', json.dumps(r)); ok &= r['hp'] == 3 and abs(r['kg'] - (54 + 7 * 8)) < 1e-9 and ['Truss section 3 m', 2] in r['pull'] and ['Truss section 1 m', 1] in r['pull'] and ['Round sling / spanset (bumper to truss)', 12] in r['pull'] and r['isFly'] and 'truss' in r['note'] and r['truss'] == ''
        # parts rules per tile model: per tile / column / hoist point, Add part and Remove buttons, typing in the table
        r = await pg.evaluate("""()=>{rigSet(S.preset,[['Clamp',2,'tile',0.2],['Safety',1,'hoist point',0.5],['Brace',1,'column',2.5]]);sync();const c=rigCalc(walls[0]);
          const a=document.querySelector('[data-a=rpadd]');a.closest('details').open=true;a.click();const n1=rigParts(S.preset).length;const inp=document.querySelector('#rigParts input[data-rp="3"][data-f="0"]');inp.value='Spanset';inp.dispatchEvent(new Event('input',{bubbles:true}));
          const n2=rigParts(S.preset)[3][0];document.querySelector('#rigParts button[data-v="3"]').click();return{pull:c.pull,kg:c.kg,n1,n2,n3:rigParts(S.preset).length}}""")
        print('parts', json.dumps(r)); ok &= ['Clamp', 144, True] in r['pull'] and ['Safety', 3, False] in r['pull'] and ['Brace', 12, False] in r['pull'] and r['n1'] == 4 and r['n2'] == 'Spanset' and r['n3'] == 3
        ok &= abs(r['kg'] - (54 + 56 + 144 * .2 + 3 * .5 + 12 * 2.5)) < 1e-9
        # ground stack: bases, per-hoist-point parts not counted
        r = await pg.evaluate("()=>{S.bmode='Ground stack';S.rgbw=2;S.rgkg=14;storeWall();sync();const c=rigCalc(walls[0]);return{hp:c.hp,pull:c.pull,rows:c.rows.map(x=>x[0]),fly:isFly(walls[0])}}")
        print('ground', json.dumps(r)); ok &= r['hp'] == 0 and ['Ground base, 2 tiles wide', 6] in r['pull'] and 'Parts per hoist point' in r['rows'] and not r['fly']
        # pull sheet: a Rigging department, clamps get tile spares
        r = await pg.evaluate("()=>{S.spT=5;const d=pullItems().find(x=>x[0]=='Rigging');return d&&d[1]}"); print('pull', r)
        ok &= r is not None and ['Clamp', 144, 8] in r and ['Brace', 12, 0] in r
        # spec sheet section has the rigging rows; saved and reopened; bad saved parts are cleaned
        r = await pg.evaluate("""()=>{const sp=specSections()[1][1].some(x=>x[0]=='Total weight with rigging');const o=JSON.parse(JSON.stringify(stateObj()));o.S.rparts.X=[['a','x','nope',-1],5];o.walls[0].tsec='2, 4';applyCore(o);sync();
          return{sp,parts:rigParts(S.preset).length,x:rigParts('X'),tsec:walls[0].tsec,on:S.rigOn}}""")
        print('save', r); ok &= r['sp'] and r['parts'] == 3 and r['x'] == [['a', 0, 'tile', 0]] and r['tsec'] == '2, 4' and r['on']
        # a second wall keeps its own hang method; the LED build select shows the truss option too
        r = await pg.evaluate("()=>{addWall(false);S.bmode='Flown from motors';storeWall();sync();return{m:walls.map(w=>w.bmode),opts:[...document.querySelectorAll('select[data-k=bmode]')].map(s=>s.options.length)}}")
        print('walls', r); ok &= r['m'] == ['Ground stack', 'Flown from motors'] and r['opts'] == [3, 3]
        await pg.evaluate("()=>{S.play=true;sync()}"); await pg.wait_for_timeout(800)
        print('page errors', errs); ok &= not errs; await b.close()
    print('ALL OK' if ok else 'FAILED')
asyncio.run(main())
