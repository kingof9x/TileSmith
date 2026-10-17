import asyncio, sys, json
from playwright.async_api import async_playwright
APP='file:///home/claude/tilesmith-desktop/app/index.html'
MOCK=r"""
(()=>{const plat=window.__PLAT;const calls=window.__calls=[];
const fsm={existsSync:p=>/SpoutDX\.dll$|syphon\.node$|Syphon\.framework$/.test(p)&&!window.__NOLIB,readFileSync(){throw Error('nofile')},writeFileSync(){},mkdirSync(){},readdirSync:()=>[],unlinkSync(){}};
const pathm={join:(...a)=>a.join(plat=='win32'?'\\':'/'),dirname:p=>p.replace(/[\\/][^\\/]*$/,''),basename:p=>p.replace(/^.*[\\/]/,'')};
let hc=false;window.__setClients=v=>hc=v;
class MetalServer{constructor(n){this._n=n;calls.push(['syphon.new',n])}publishImageData(d,r,s,f){calls.push(['syphon.pub',d.constructor.name,r.width,r.height,s.width,s.height,f,d.length])}dispose(){calls.push(['syphon.dispose'])}get hasClients(){return hc}get name(){return this._n}}
const lib={func(n,r,a){if(typeof n=='string'&&r===undefined){const m=n.match(/(\w+)\(/);n=m?m[1]:n}
 return (...args)=>{const short=n.replace(/^\?+|@.*$/g,'');calls.push(['fn',short,...args.slice(1).map(x=>x&&x.byteLength!==undefined?'buf'+x.byteLength:x)]);
  if(n=='NDIlib_initialize')return true;if(n=='NDIlib_send_create')return {inst:1};if(/SendImage/.test(n))return !window.__SPOUTFAIL;if(/GetName/.test(n))return 'TileSmith_1';if(/HeapAlloc/.test(n))return {ptr:1};if(/GetProcessHeap/.test(n))return {heap:1};return true}}};
const koffi={load(f){calls.push(['koffi.load',f]);return lib},struct(){}};
window.process={platform:plat,versions:{electron:'44.0.0'},resourcesPath:plat=='win32'?'C:\\res':'/App/Contents/Resources',cwd:()=>plat=='win32'?'C:\\proj':'/proj',env:{}};
class Buf extends Uint8Array{toString(e){if(e=='latin1'||e=='utf8')return String.fromCharCode(...this).replace(/\0+$/,'');return super.toString()}}
window.Buffer={from:(ab,o,l)=>new Uint8Array(ab,o,l),alloc:n=>new Buf(n)};
window.require=m=>{if(m=='fs')return fsm;if(m=='path')return pathm;if(m=='os')return{homedir:()=>'/home/x'};if(m=='koffi')return koffi;
 if(m=='electron')return{ipcRenderer:{send:(c,v)=>calls.push(['ipc',c,v])},shell:{openPath:p=>calls.push(['open',p]),openExternal:u=>calls.push(['ext',u]),showItemInFolder(){}}};
 if(/syphon\.node$/.test(m)){calls.push(['require',m]);return{MetalServer}}if(m=='child_process')return{spawn(){throw Error('no')}};throw Error('no module '+m)};
})();
"""
async def page_for(b, plat=None, nolib=False):
    ctx=await b.new_context(viewport={'width':1500,'height':900})
    pg=await ctx.new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
    if plat:
        await pg.add_init_script(f"window.__PLAT={json.dumps(plat)};window.__NOLIB={json.dumps(nolib)};"+MOCK)
    await pg.goto(APP);await pg.wait_for_timeout(800)
    return ctx,pg,errs
async def main():
    ok=True
    async with async_playwright() as p:
        b=await p.chromium.launch()
        # ---- web preview
        ctx,pg,errs=await page_for(b)
        r=await pg.evaluate("""()=>({btn:getComputedStyle(document.querySelector('#shBtn')).display,row:getComputedStyle(document.querySelector('#shRow')).display,
          sub:[...document.querySelectorAll('details.subd>summary')].map(x=>x.textContent).filter(t=>/Spout|Syphon|NDI/.test(t)),
          keys:['shName','shFps','shIdle'].map(k=>[k,S[k]]),lic:!!document.querySelector('#shlic'),about:document.querySelector('#shs').closest('.sec').textContent.slice(0,160)})""")
        print('WEB',r,errs);ok&=r['btn']=='none' and r['row']=='none' and not errs
        await ctx.close()
        # ---- Windows desktop with Spout built in
        ctx,pg,errs=await page_for(b,'win32')
        r=await pg.evaluate("""()=>({btn:getComputedStyle(document.querySelector('#shBtn')).display,txt:document.querySelector('#shBtn').textContent,
          sub:[...document.querySelectorAll('details.subd>summary')].map(x=>x.textContent).filter(t=>/Spout|Syphon|NDI/.test(t)),label:document.querySelector('[data-k=shName]').parentNode.textContent})""")
        print('WIN',r);ok&=r['btn']!='none' and r['txt']=='Start Spout'
        await pg.click('#shBtn');await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""()=>{const c=__calls;return{label:document.querySelector('#shBtn').textContent,live:document.querySelector('#shBtn').classList.contains('live'),
          oc:OC.on,first:c.filter(x=>x[0]=='fn'&&!/SendImage/.test(x[1])).map(x=>x.join(' ')),sends:c.filter(x=>x[0]=='fn'&&x[1]=='SendImage').length,
          sample:c.filter(x=>x[0]=='fn'&&x[1]=='SendImage').slice(0,1),status:document.querySelector('#shs').textContent,ipc:c.filter(x=>x[0]=='ipc')}}""")
        print('WIN started',json.dumps(r,indent=0));ok&=r['live'] and r['oc'] and r['sends']>0
        # still picture with Save CPU: few sends; then start NDI too
        await pg.evaluate("__calls.length=0");await pg.click('#bar [data-a=ndi]');await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""()=>{const c=__calls;return{ndi:c.filter(x=>x[1]=='NDIlib_send_send_video_v2').length,spout:c.filter(x=>x[1]=='SendImage').length,ndiLabel:document.querySelector('#bar [data-a=ndi]').textContent,oc:OC.on,rate:outRate()}}""")
        print('WIN +NDI',r)
        await pg.click('#bar [data-a=ndi]');await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>({oc:OC.on,ndi:!!nd,share:!!shOut,rate:outRate()})");print('WIN NDI stopped',r);ok&=r['oc'] and r['share']
        # moving picture: switch play on so frames change
        await pg.evaluate("__calls.length=0;S.dvdOn=true");await pg.wait_for_timeout(1000)
        r=await pg.evaluate("()=>({spout:__calls.filter(x=>x[1]=='SendImage').length,status:document.querySelector('#shs').textContent})");print('WIN moving',r)
        await pg.evaluate("S.dvdOn=false")
        await pg.click('#shBtn');await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>({oc:OC.on,label:document.querySelector('#shBtn').textContent,release:__calls.filter(x=>x[1]=='ReleaseSender').length,ipc:__calls.filter(x=>x[0]=='ipc').map(x=>x[2]),status:document.querySelector('#shs').textContent})")
        print('WIN stopped',r,errs);ok&=(not r['oc']) and r['release']==1 and not errs
        # licence button opens local files (none in mock) then the web page
        await pg.evaluate("__calls.length=0;document.querySelector('#shlic').click()");r=await pg.evaluate("__calls");print('WIN lic',r)
        # failure path
        await pg.evaluate("window.__SPOUTFAIL=true;__calls.length=0");await pg.click('#shBtn');await pg.wait_for_timeout(800)
        r=await pg.evaluate("()=>({live:!!shOut,status:document.querySelector('#shs').textContent,toast:document.querySelector('#toast').textContent})");print('WIN fail',r);ok&=not r['live']
        await ctx.close()
        # ---- Windows desktop built WITHOUT Spout
        ctx,pg,errs=await page_for(b,'win32',True)
        r=await pg.evaluate("()=>({btn:getComputedStyle(document.querySelector('#shBtn')).display,row:getComputedStyle(document.querySelector('#shRow')).display,state:document.querySelector('#shs').textContent})")
        print('WIN nolib',r,errs);ok&=r['btn']=='none' and r['row']=='none'
        await ctx.close()
        # ---- Mac desktop with Syphon
        ctx,pg,errs=await page_for(b,'darwin')
        r=await pg.evaluate("()=>({txt:document.querySelector('#shBtn').textContent,sub:[...document.querySelectorAll('details.subd>summary')].map(x=>x.textContent).filter(t=>/Spout|Syphon/.test(t)),label:document.querySelector('[data-k=shName]').parentNode.textContent})")
        print('MAC',r)
        await pg.click('#shBtn');await pg.wait_for_timeout(1200)
        r=await pg.evaluate("()=>({pubs:__calls.filter(x=>x[0]=='syphon.pub').length,first:__calls.filter(x=>x[0].startsWith('syphon')||x[0]=='require').slice(0,3),status:document.querySelector('#shs').textContent})")
        print('MAC no clients',r);ok&=r['pubs']==1
        await pg.evaluate("__setClients(true);__calls.length=0");await pg.wait_for_timeout(1200)
        r=await pg.evaluate("()=>({pubs:__calls.filter(x=>x[0]=='syphon.pub').length,status:document.querySelector('#shs').textContent})");print('MAC client',r);ok&=r['pubs']>=1
        await pg.click('#shBtn');await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>({d:__calls.filter(x=>x[0]=='syphon.dispose').length,oc:OC.on})");print('MAC stop',r,errs);ok&=r['d']==1 and not errs
        await ctx.close()
        await b.close()
    print('ALL OK' if ok else 'PROBLEMS')
if __name__=="__main__": asyncio.run(main())
