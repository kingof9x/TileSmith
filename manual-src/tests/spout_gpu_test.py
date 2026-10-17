"""Spout graphics-card choice: a stand-in for SpoutDX.dll (two graphics cards, like a laptop with Intel + NVIDIA) and
for Electron's require(), then the real page. Checks the Graphics card list, Automatic (Windows high-performance card,
or the first card that is not Intel/Microsoft), switching cards while running, a failed DirectX device, the status
line, the log file, and that the Mac and web versions are unchanged. Prints ALL OK."""
import asyncio, json, sys
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
MOCK = r"""
(()=>{const plat=window.__PLAT;const calls=window.__calls=[];const O=window.__OPT||{};
const fsm={existsSync:p=>/SpoutDX\.dll$|syphon\.node$|Syphon\.framework$/.test(p),readFileSync(){if(O.state)return O.state;throw Error('nofile')},writeFileSync(){},mkdirSync(){},readdirSync:()=>[],unlinkSync(){}};
const pathm={join:(...a)=>a.join(plat=='win32'?'\\':'/'),dirname:p=>p.replace(/[\\/][^\\/]*$/,''),basename:p=>p.replace(/^.*[\\/]/,'')};
class MetalServer{constructor(n){this._n=n}publishImageData(){}dispose(){}get hasClients(){return true}get name(){return this._n}}
// SpoutDX stand-in: adapters, device, sender
const GPUS=O.gpus||['Intel(R) UHD Graphics 630','NVIDIA GeForce RTX 3060 Laptop GPU'];
const sp=window.__sp={idx:0,dev:null,sending:false};
const short=n=>n.replace(/^\?+|@.*$/g,'');
const impl={
 spoutDX:()=>true, OpenDirectX11:()=>{sp.dev=O.nodevice?null:{gpu:sp.idx};return true}, CloseDirectX11:()=>{sp.dev=null},
 GetDX11Device:()=>sp.dev, GetNumAdapters:()=>GPUS.length, GetAdapter:()=>sp.idx,
 GetAdapterName:(o,i,b,n)=>{if(i<0||i>=GPUS.length)return false;const t=GPUS[i];for(let k=0;k<t.length;k++)b[k]=t.charCodeAt(k);b[t.length]=0;return true},
 SetAdapter:(o,i)=>{if(i<0||i>=GPUS.length)return false;sp.idx=i;return true},
 SetPreferredAdapter:(o,p)=>{if(O.nopref)return false;sp.idx=GPUS.findIndex(g=>/NVIDIA|AMD|Radeon/.test(g));if(sp.idx<0)sp.idx=0;return true},
 EnableSpoutLogFile:(o,p,a)=>{sp.log=p}, SetSenderFormat:()=>{}, SetSenderName:()=>true, GetName:()=>'TileSmith',
 SendImage:()=>{if(!sp.dev)return false;sp.sending=true;sp.sentOn=sp.dev.gpu;return !O.sendfail}, ReleaseSender:()=>{sp.sending=false},
 HeapAlloc:()=>({ptr:1}), GetProcessHeap:()=>({heap:1}), NDIlib_initialize:()=>true, NDIlib_send_create:()=>({inst:1})};
const lib={func(n,r,a){if(typeof n=='string'&&r===undefined){const m=n.match(/(\w+)\(/);n=m?m[1]:n}const s=short(n),f=impl[s]||(()=>true);
 return (...args)=>{calls.push([s,...args.slice(1).map(x=>x&&x.byteLength!==undefined?'buf':x)]);return f(...args)}}};
const koffi={load(f){return lib},struct(){}};
window.process={platform:plat,versions:{electron:'44.0.0'},resourcesPath:plat=='win32'?'C:\\res':'/App/Contents/Resources',cwd:()=>plat=='win32'?'C:\\proj':'/proj',env:{APPDATA:'C:\\Users\\x\\AppData\\Roaming'}};
class Buf extends Uint8Array{toString(e){if(e=='latin1'||e=='utf8')return String.fromCharCode(...this);return super.toString()}}
window.Buffer={from:(ab,o,l)=>new Uint8Array(ab,o,l),alloc:n=>new Buf(n)};
window.require=m=>{if(m=='fs')return fsm;if(m=='path')return pathm;if(m=='os')return{homedir:()=>'C:\\Users\\x'};if(m=='koffi')return koffi;
 if(m=='electron')return{ipcRenderer:{send(){}},shell:{openPath(){},openExternal(){},showItemInFolder(){}}};
 if(/syphon\.node$/.test(m))return{MetalServer};if(m=='child_process')return{spawn(){throw Error('no')}};throw Error('no module '+m)};
})();
"""


async def page_for(b, plat=None, opt=None):
    ctx = await b.new_context(viewport={'width': 1500, 'height': 900})
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    if plat:
        await pg.add_init_script(f"window.__PLAT={json.dumps(plat)};window.__OPT={json.dumps(opt or {})};" + MOCK)
    await pg.goto(APP); await pg.wait_for_timeout(700)
    return ctx, pg, errs


async def main():
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # Windows laptop, Automatic -> the NVIDIA card through Windows' high-performance preference
        ctx, pg, errs = await page_for(b, 'win32')
        r = await pg.evaluate("()=>({opts:[...document.querySelectorAll('[data-k=shGpu] option')].map(o=>o.value),val:document.querySelector('[data-k=shGpu]').value,S:S.shGpu,log:__sp.log})")
        print('LIST', r); ok &= r['opts'] == ['Automatic', 'Intel(R) UHD Graphics 630', 'NVIDIA GeForce RTX 3060 Laptop GPU'] and r['val'] == 'Automatic' and r['log'].endswith('TileSmith\\spout-log.txt')
        await pg.click('#shBtn'); await pg.wait_for_timeout(1300)
        r = await pg.evaluate("()=>({live:!!shOut,gpu:__sp.dev&&__sp.dev.gpu,sentOn:__sp.sentOn,status:document.querySelector('#shs').textContent,order:__calls.map(c=>c[0]).filter(n=>/Adapter|DirectX|SetSender|Release/.test(n)&&!/GetAdapterName|GetNumAdapters/.test(n))})")
        print('AUTO', r); ok &= r['live'] and r['gpu'] == 1 and r['sentOn'] == 1 and 'NVIDIA GeForce RTX 3060' in r['status'] and r['order'][:3] == ['SetPreferredAdapter', 'OpenDirectX11', 'GetAdapter']
        # switch to the Intel card while running: release, close, new device on card 0, still live
        await pg.evaluate("()=>{__calls.length=0;for(let e=document.querySelector('[data-k=shGpu]');e;e=e.parentElement)if(e.tagName=='DETAILS')e.open=true}"); await pg.select_option('[data-k=shGpu]', 'Intel(R) UHD Graphics 630'); await pg.wait_for_timeout(1300)
        r = await pg.evaluate("()=>({live:!!shOut,gpu:__sp.dev&&__sp.dev.gpu,sentOn:__sp.sentOn,status:document.querySelector('#shs').textContent,order:__calls.map(c=>c[0]).filter(n=>/SetAdapter|DirectX|ReleaseSender|SetPreferred/.test(n))})")
        print('SWITCH', r); ok &= r['live'] and r['gpu'] == 0 and r['sentOn'] == 0 and 'Intel(R) UHD Graphics 630' in r['status'] and 'CloseDirectX11' in r['order'] and r['order'].index('CloseDirectX11') < r['order'].index('SetAdapter')
        # stop and start again on the same card: the device is kept
        await pg.click('#shBtn'); await pg.wait_for_timeout(200); await pg.evaluate("__calls.length=0"); await pg.click('#shBtn'); await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>({live:!!shOut,closes:__calls.filter(c=>c[0]=='CloseDirectX11').length,opens:__calls.filter(c=>c[0]=='OpenDirectX11').length,gpu:__sp.sentOn})")
        print('RESTART SAME', r); ok &= r['live'] and r['closes'] == 0 and r['opens'] == 0 and r['gpu'] == 0
        await pg.click('#shBtn'); print('errors', errs); ok &= not errs
        await ctx.close()
        # no Windows graphics preference: Automatic picks the first card that is not Intel or Microsoft
        ctx, pg, errs = await page_for(b, 'win32', {'nopref': True, 'gpus': ['Intel(R) Iris(R) Xe Graphics', 'AMD Radeon RX 6600', 'Microsoft Basic Render Driver']})
        await pg.click('#shBtn'); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("()=>({gpu:__sp.sentOn,status:document.querySelector('#shs').textContent})")
        print('NOPREF', r); ok &= r['gpu'] == 1 and 'AMD Radeon RX 6600' in r['status'] and not errs
        await ctx.close()
        # DirectX 11 cannot start: clear message with the log path, not live
        ctx, pg, errs = await page_for(b, 'win32', {'nodevice': True})
        await pg.click('#shBtn'); await pg.wait_for_timeout(600)
        r = await pg.evaluate("()=>({live:!!shOut,status:document.querySelector('#shs').textContent,cls:document.querySelector('#shs').className,btn:document.querySelector('#shBtn').textContent})")
        print('NODEVICE', r); ok &= not r['live'] and 'could not start DirectX 11' in r['status'] and 'spout-log.txt' in r['status'] and r['btn'] == 'Start Spout'
        await ctx.close()
        # sends keep failing: stops with the card named
        ctx, pg, errs = await page_for(b, 'win32', {'sendfail': True})
        await pg.click('#shBtn'); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("()=>({live:!!shOut,status:document.querySelector('#shs').textContent})")
        print('SENDFAIL', r); ok &= not r['live'] and 'could not send frames on NVIDIA' in r['status']
        await ctx.close()
        # a saved card this PC does not have -> Automatic
        st = json.dumps({'sv': 23, 'S': {'shGpu': 'Some Other GPU'}, 'walls': [{}], 'cur': 0})
        ctx, pg, errs = await page_for(b, 'win32', {'state': st})
        r = await pg.evaluate("()=>({S:S.shGpu,val:document.querySelector('[data-k=shGpu]').value})")
        print('SAVED UNKNOWN', r); ok &= r['S'] == 'Automatic' and r['val'] == 'Automatic' and not errs
        await ctx.close()
        # Mac and web: no Graphics card setting, no errors
        for plat in ('darwin', None):
            ctx, pg, errs = await page_for(b, plat)
            r = await pg.evaluate("()=>({sel:!!document.querySelector('[data-k=shGpu]'),S:S.shGpu})")
            print('OTHER', plat, r, errs); ok &= not r['sel'] and not errs
            await ctx.close()
        await b.close()
    print('ALL OK' if ok else 'PROBLEMS'); return ok

if __name__ == '__main__':
    sys.exit(0 if asyncio.run(main()) else 1)
