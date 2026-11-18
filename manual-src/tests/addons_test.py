# Info > Add-ons (desktop app): shows whether the NDI(R) Runtime and ffmpeg are found, offers NDI's own Runtime download
# (opened in the browser) and downloads ffmpeg into TileSmith's own folder. The browser test cannot be the desktop app,
# so it checks the hidden-on-web layout, the translations and the pieces that are plain logic, and runs the real
# download/unpack/find code under Node with a local test server (no internet needed).
import asyncio, json, os, re, subprocess, sys, tempfile, zipfile, http.server, threading, shutil
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
DESKDIR = os.path.join(os.environ.get('TILESMITH_ROOT') or os.path.dirname(os.path.dirname(HERE)), 'tilesmith-desktop')
APP = 'file://' + os.path.join(DESKDIR, 'app', 'index.html')
ok = True
def chk(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)

async def m():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1000)
        chk(await pg.evaluate("()=>S.addonAsk===true"), 'add-on reminder at start is on by default')
        await pg.click('[data-a=about]'); await pg.wait_for_timeout(300)
        chk(await pg.evaluate("()=>!!document.getElementById('addonBox')"), 'Info window has an Add-ons section')
        chk(not await pg.is_visible('#addonBox'), 'Add-ons is hidden in the web page (desktop only)')
        # what the desktop app would draw: run addonUI with stand-ins for the desktop checks
        html = await pg.evaluate("""()=>{const src=addonUI.toString().replace(/!DESK/g,'false');
          const f=new Function('addonScan','addonDir','process','SH_OK','NDI_FROM','WIN','MAC','NDI_RT','FF_SRC','$','return ('+src+')()');
          const L=document.getElementById('addonList'),out=[];
          const run=(scan,pl,sh)=>{f(()=>scan,()=>'C:/Users/x/AppData/Roaming/TileSmith/addons',{platform:pl,arch:'x64'},sh,'installed NDI® Runtime',pl=='win32',pl=='darwin',NDI_RT,FF_SRC,$);out.push(L.innerHTML)};
          run({ndi:null,ff:null},'win32',true);run({ndi:'x',ff:{path:'y',hap:true}},'win32',true);run({ndi:'x',ff:{path:'y',hap:false}},'darwin',false);run({ndi:null,ff:null},'linux',false);return out}""")
        miss, ready, nohap, lin = html
        chk('Install NDI® Runtime' in miss and 'Download ffmpeg' in miss and miss.count('Not installed') == 2, 'nothing found: NDI Runtime and ffmpeg offered')
        chk('Spout output' in miss and 'Built in' in miss, 'Windows shows Spout as built in')
        chk('data-ad' not in ready and ready.count('Ready') == 2, 'everything found: no download buttons')
        chk('Ready (no HAP encoder)' in nohap and 'Download ffmpeg' in nohap and 'Syphon output' in nohap and 'Not in this build' in nohap, 'ffmpeg without HAP offers the full download; Mac shows Syphon')
        chk('Get NDI® Tools' in lin and 'sudo apt install ffmpeg' in lin and 'Download ffmpeg' not in lin, 'Linux: NDI Tools page and package manager hint')
        chk(await pg.evaluate("()=>NDI_RT.win32.startsWith('https://ndi.link/')&&NDI_RT.darwin.startsWith('https://ndi.link/')"), 'NDI Runtime links point at NDI’s own ndi.link')
        await pg.evaluate("()=>setLang('de')"); await pg.wait_for_timeout(200)
        await pg.evaluate("()=>{document.getElementById('addonList').innerHTML='<div class=\"addon\"><b>Video export (ffmpeg)</b><span class=\"st no\">Not installed</span><div class=\"nt\">Downloading ffmpeg from gyan.dev… 42%</div></div>'}"); await pg.wait_for_timeout(200)
        t = await pg.text_content('#addonList')
        chk('Videoexport (ffmpeg)' in t and 'Nicht installiert' in t and 'ffmpeg wird von gyan.dev heruntergeladen… 42%' in t, f'add-on texts are translated ({t})')
        await pg.evaluate("()=>setLang('en')")
        chk(not errs, f'no page errors {errs}')
        await b.close()

    # the real download + unpack + find code under Node, against a local server with a zip holding bin/ffmpeg
    tmp = tempfile.mkdtemp()
    try:
        fake = os.path.join(tmp, 'ffmpeg'); open(fake, 'w').write('#!/bin/sh\necho "ffmpeg version test"\n')
        z = os.path.join(tmp, 'ff.zip')
        with zipfile.ZipFile(z, 'w') as zf: zf.write(fake, 'ffmpeg-7.1/bin/ffmpeg')
        html = open(os.path.join(DESKDIR, 'app', 'index.html'), encoding='utf8').read()
        fns = ''.join(re.search(r'\n(function ' + n + r'\(.*?\n)(?=function |let |const |\$\(|if\()', html, re.S).group(1) for n in ['addonGet', 'addonFindFile'])
        js = os.path.join(tmp, 't.js')
        open(js, 'w').write(fns + r'''
const http=require('http'),fs=require('fs'),path=require('path'),cp=require('child_process');
// http stand-in for https (same API), with one redirect like real download hosts
const srv=http.createServer((q,r)=>{if(q.url=='/go'){r.writeHead(302,{Location:'/ff.zip'});return r.end()}const b=fs.readFileSync(process.argv[2]);r.writeHead(200,{'Content-Length':b.length});r.end(b)});
srv.listen(0,async()=>{const base='http://127.0.0.1:'+srv.address().port,Module=require('module'),orig=Module.prototype.require;
 Module.prototype.require=function(n){return n=='https'?http:orig.apply(this,arguments)};
 const out=path.join(process.argv[3],'dl.zip'),pr=[];await addonGet(base+'/go',out,f=>pr.push(f));
 const un=path.join(process.argv[3],'x');fs.mkdirSync(un);cp.spawnSync('unzip',['-q',out,'-d',un]);
 const f=addonFindFile(un,'ffmpeg');console.log(JSON.stringify({size:fs.statSync(out).size,last:pr[pr.length-1],found:!!f&&f.endsWith(path.join('bin','ffmpeg'))}));srv.close()})''')
        r = subprocess.run(['node', js, z, tmp], capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        chk(res.get('size') == os.path.getsize(z) and res.get('last') == 1, f'addonGet follows a redirect and saves the whole file with progress ({res} {r.stderr[:300]})')
        chk(res.get('found'), 'addonFindFile finds ffmpeg inside the unpacked folders')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    nsh = open(os.path.join(DESKDIR, 'build', 'installer.nsh'), encoding='utf8').read()
    chk('!macro customInstall' in nsh and 'IfSilent' in nsh and 'https://ndi.link/NDIRedistV6' in nsh, 'Windows installer handles add-ons at the end of setup (not when silent)')
    chk(all(ord(ch) < 128 for ch in nsh), 'installer script is plain ASCII (NSIS)')
    chk('ExecShellWait' in nsh and '/verysilent' in nsh and 'ndi.link/NDIRedistV6' in nsh, 'installer installs the NDI Runtime itself (silently, after the admin prompt) instead of opening a browser')
    chk('ExecShell "open" "https' not in nsh and 'powershell' not in nsh.lower(), 'installer opens no browser and runs no PowerShell')
    chk(nsh.count('inetc::get /POPUP') == 2 and '$PLUGINSDIR' in nsh, 'downloads show a progress window and go to the temporary setup folder (deleted after setup)')
    chk('NDI_RUNTIME_DIR_V5' in nsh and 'HKCU "Environment"' in nsh and '$PROGRAMFILES64\\NDI\\*' in nsh and 'Runtime\\${TS_NDI_DLL}' in nsh, 'NDI check looks at v5 and v6, machine and user variables, and every folder under Program Files\\NDI')
    chk('Nsis7z::ExtractWithDetails' in nsh and '$APPDATA\\TileSmith\\addons' in nsh, 'ffmpeg .7z is unpacked by the installer and copied to the add-ons folder')
    html = open(os.path.join(DESKDIR, 'app', 'index.html'), encoding='utf8').read()
    chk("-Verb RunAs -Wait" in html and "'/verysilent','/norestart'" in html and "open',['-W'" in html, 'app: Install NDI Runtime runs NDI’s installer (Windows silently as admin, Mac in Installer)')
    chk('7-zip.org/a/7zr.exe' in html, 'app: .7z falls back to 7-Zip’s 7zr.exe when Windows tar cannot unpack it')
    print('ALL OK' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
asyncio.run(m())
