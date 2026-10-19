# NovaStar .scr writer: rebuilding the real NovaLCT sample (sarakusha/novastar cfg/test.scr) must give the same bytes; a generated file
# must decode (checksums, lengths, regions) the way the open-source decoder reads it; the config zip must hold .scr + CSV + JSON
import asyncio, struct, json, os, zipfile, io, sys
from playwright.async_api import async_playwright
SAMPLE=os.environ.get('SCR_SAMPLE','/tmp/res/novastar/cfg/test.scr')
def decode(b):
    h,crc,dl,sl,al=struct.unpack_from('<4sHIIH',b,0); assert h==b'DSCI'; base=54
    assert sum(b[6:base+dl+sl])&0xffff==crc,'header crc'
    d=b[base:]; dvi=d[:dl]; assert sum(dvi[4:])&0xffff==struct.unpack_from('<H',dvi,2)[0],'dvi crc'
    gw,gh=struct.unpack_from('<HH',dvi,6)
    si=d[dl:dl+sl]; assert sum(si[4:])&0xffff==struct.unpack_from('<H',si,2)[0],'screen crc'
    n=si[132]; pos=133+4*n; screens=[]
    for i in range(n):
        L=struct.unpack_from('<I',si,133+4*i)[0]; t,vm,x,y,c,r=struct.unpack_from('<BBHHHH',si,pos); assert t==1
        regs=[struct.unpack_from('<BBHHHHHHHB',si,pos+10+17*k) for k in range((L-10)//17)]
        screens.append(dict(x=x,y=y,cols=c,rows=r,regions=[dict(s=a[0],p=a[1],ci=a[2],x=a[3],y=a[4],xi=a[5],yi=a[6],w=a[7],h=a[8]) for a in regs])); pos+=L
    ep=struct.unpack_from('<I',si,28)[0]; el=struct.unpack_from('<H',si,ep)[0]; json.loads(si[ep+2:ep+2+el])
    ad=d[dl+sl:dl+sl+al]; assert sum(ad[4:])&0xffff==struct.unpack_from('<H',ad,2)[0],'adjust crc'; assert ad[132]==n
    return gw,gh,screens
async def main():
    ok=True
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(accept_downloads=True); pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/tilesmith-desktop/app/index.html'); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(700)
        if os.path.exists(SAMPLE):
            raw=open(SAMPLE,'rb').read(); gw,gh,sc=decode(raw)
            out=await pg.evaluate("([w,h,s])=>Array.from(scrBytes(w,h,s))",[gw,gh,sc]); same=bytes(out)==raw
            print('sample rebuild identical:',same,len(out),len(raw)); ok=ok and same
        else: print('sample not found, skipped')
        await pg.evaluate("""()=>{S.preset='ROE Black Pearl BP2V2';applyPreset();S.cols=6;S.rows=4;S.ox=0;S.oy=0;storeWall();showAll();addWall(false);S.cols=4;S.rows=4;S.ox=1100;S.oy=100;storeWall();showAll();
          S.proc='NovaStar VX1000 Pro';applySpec();walls.forEach(w=>w.wmode='Snake');S.wmode='Snake';storeWall();sync()}""")
        lbl=await pg.evaluate("()=>[document.querySelector('[data-a=pcfg]').textContent,getComputedStyle(document.querySelector('#cfgBox')).display]"); print(lbl); ok=ok and 'NovaStar' in lbl[0] and lbl[1]!='none'
        async with pg.expect_download() as d: await pg.evaluate("()=>exportConfig()")
        z=zipfile.ZipFile(io.BytesIO(open(await (await d.value).path(),'rb').read())); names=z.namelist(); print(names)
        scr=[n for n in names if n.endswith('.scr')]; ok=ok and len(scr)==1 and 'wiring.csv' in names and 'wiring.json' in names
        gw,gh,sc=decode(z.read(scr[0])); rows=json.loads(z.read('wiring.json'))['tiles']
        print('canvas',gw,gh,'screens',[(s['x'],s['y'],s['cols'],s['rows'],len(s['regions'])) for s in sc])
        ok=ok and (gw,gh)==(1920,1080) and len(sc)==2 and len(sc[0]['regions'])==24 and len(sc[1]['regions'])==16 and sc[1]['x']==1100
        r0=[r for r in sc[0]['regions'] if r['ci']==0 and r['p']==0][0]; print('first cabinet',r0); ok=ok and r0['w']==176 and r0['x']==0
        await pg.evaluate("()=>{S.proc='Brompton Tessera S8';applySpec();sync()}")
        t=await pg.evaluate("()=>document.querySelector('[data-a=pcfg]').textContent"); print(t); ok=ok and t=='Download wiring sheet'
        ok=ok and not errs; print('errs',errs)
        print('ALL OK' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
