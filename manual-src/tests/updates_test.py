# Check for updates (Info window > Updates): asks the GitHub API for the latest release, compares it with
# APP_VERSION and offers Download / Release notes; at start the desktop and phone apps check at most once a day
# and show a note when a newer release exists. GitHub is mocked here (page.route), so no network is needed.
# Also checks scripts/set-version.js stamps APP_VERSION, and the Windows/Mac installer build settings.
import asyncio, json, os, shutil, subprocess, sys, tempfile
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
DESKDIR = os.path.join(os.environ.get('TILESMITH_ROOT') or os.path.dirname(os.path.dirname(HERE)), 'tilesmith-desktop')
APP = 'file://' + os.path.join(DESKDIR, 'app', 'index.html')
ok = True
def chk(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)

def release(tag, names=()):
    return {'tag_name': tag, 'html_url': f'https://github.com/kingof9x/TileSmith/releases/tag/{tag}',
            'assets': [{'name': n, 'browser_download_url': f'https://github.com/kingof9x/TileSmith/releases/download/{tag}/{n}'} for n in names]}

async def m():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1400, 'height': 900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        reply = {'status': 200, 'body': release('v9.9', ['TileSmith-windows-setup.exe', 'TileSmith-mac-universal.dmg'])}
        calls = []
        async def handle(route):
            calls.append(route.request.url)
            await route.fulfill(status=reply['status'], content_type='application/json', body=json.dumps(reply['body']),
                                headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://api.github.com/**', handle)
        opened = []
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{window.open=(u)=>{window.__opened=(window.__opened||[]).concat([u])}}")
        ver = await pg.evaluate("()=>APP_VERSION")
        chk(ver and all(x.isdigit() for x in ver.split('.')), f'APP_VERSION is a version number ({ver})')
        chk(await pg.evaluate("()=>S.updAuto===true"), 'check at start is on by default')
        chk(await pg.evaluate("()=>[verNewer('v3.10','3.9'),verNewer('3.7','3.7.0'),verNewer('v3.6','3.7'),verNewer('4','3.9.9')].join()") == 'true,false,false,true',
            'version compare handles v-prefix, 3.10 > 3.9 and equal versions')
        await pg.wait_for_timeout(4500)
        chk(not calls, 'the browser page does not check GitHub by itself at start (only the desktop and phone apps do)')

        await pg.click('[data-a=about]'); await pg.wait_for_timeout(300)
        chk(await pg.is_visible('#updChk'), 'Info window has a Check for updates button')
        chk(await pg.evaluate("()=>{const u=document.getElementById('updBox'),p=[...document.querySelectorAll('#about div')].find(d=>d.textContent=='Preferences');return !!(u&&p&&u.compareDocumentPosition(p)&Node.DOCUMENT_POSITION_FOLLOWING)}"),
            'Updates sits above Preferences')
        await pg.click('#updChk'); await pg.wait_for_timeout(500)
        chk(calls and calls[-1] == 'https://api.github.com/repos/kingof9x/TileSmith/releases/latest', f'asks the GitHub latest-release API ({calls[-1:]})')
        msg = await pg.text_content('#updMsg')
        chk(msg == f'TileSmith v9.9 is available. You have v{ver}.', f'newer release is announced: {msg}')
        chk(await pg.is_visible('#updDl') and await pg.text_content('#updDl') == 'Download v9.9', 'Download v9.9 button shows')
        await pg.click('#updDl'); await pg.click('#updNotes')
        op = await pg.evaluate("()=>window.__opened||[]")
        chk(op == ['https://github.com/kingof9x/TileSmith/releases/tag/v9.9'] * 2, f'in a browser, Download and Release notes open the release page {op}')

        reply['body'] = release('v' + ver); await pg.click('#updChk'); await pg.wait_for_timeout(400)
        msg = await pg.text_content('#updMsg')
        chk(msg == f'You have the latest version (v{ver}).' and not await pg.is_visible('#updDl'), f'same version: up to date, no Download ({msg})')
        reply['status'] = 500; reply['body'] = {}; await pg.click('#updChk'); await pg.wait_for_timeout(400)
        chk('Could not reach GitHub' in await pg.text_content('#updMsg'), 'GitHub error is reported plainly')
        reply['status'] = 404; await pg.click('#updChk'); await pg.wait_for_timeout(400)
        chk(await pg.text_content('#updMsg') == 'No release found on GitHub yet.', 'no release yet is reported')

        # platform downloads: pretend to be the desktop app on each system
        reply['status'] = 200; reply['body'] = release('v9.9', ['TileSmith-windows-setup.exe', 'TileSmith-windows-portable.exe', 'TileSmith-mac-universal.dmg', 'TileSmith-linux-x64.AppImage'])
        # DESK is a const in the page, so test updAssetName's logic by calling it with a stand-in for DESK
        names = await pg.evaluate("""()=>{const src=updAssetName.toString().replace(/\\bDESK\\b/g,'true').replace(/\\bMOBILE\\b/g,'false');
          const f=new Function('process','navigator','return ('+src+')()');
          return [f({platform:'win32',env:{}}),f({platform:'win32',env:{PORTABLE_EXECUTABLE_FILE:'C:/x.exe'}}),f({platform:'darwin',env:{}}),
                  f({platform:'linux',env:{APPIMAGE:'/x'}}),f({platform:'linux',env:{}})]}""")
        chk(names == ['TileSmith-windows-setup.exe', 'TileSmith-windows-portable.exe', 'TileSmith-mac-universal.dmg', 'TileSmith-linux-x64.AppImage', None],
            f'installed Windows gets the installer, portable gets the portable exe, Mac the .dmg, AppImage the AppImage, other Linux the page {names}')

        # the note at start (what the desktop app shows when a newer release exists)
        await pg.click('#cls')
        await pg.evaluate("()=>checkUpdates(true)"); await pg.wait_for_timeout(400)
        chk(await pg.is_visible('#updToast'), 'a newer release found at start shows a note')
        t = await pg.text_content('#updToast')
        chk('TileSmith v9.9 is available.' in t and 'Download v9.9' in t and 'Not now' in t, f'note offers Download, Release notes and Not now ({t})')
        chk(await pg.evaluate("()=>+localStorage.getItem('tilesmith-upd-last')>0"), 'the time of the check is remembered (once a day)')
        await pg.click('#updToast [data-u=x]'); await pg.wait_for_timeout(200)
        chk(not await pg.is_visible('#updToast'), 'Not now closes the note')
        reply['body'] = release('v' + ver); await pg.evaluate("()=>checkUpdates(true)"); await pg.wait_for_timeout(300)
        chk(not await pg.query_selector('#updToast'), 'no note at start when already up to date')

        # Spanish
        await pg.evaluate("()=>setLang('es')"); await pg.wait_for_timeout(300)
        reply['body'] = release('v9.9'); await pg.click('[data-a=about]'); await pg.click('#updChk'); await pg.wait_for_timeout(400)
        es = await pg.text_content('#updMsg')
        chk(es == f'TileSmith v9.9 está disponible. Tienes v{ver}.', f'message is translated ({es})')
        chk(await pg.text_content('#updChk') == 'Buscar actualizaciones', 'button is translated')
        await pg.evaluate("()=>setLang('en')")

        # phone width: Info window still fits
        await pg.set_viewport_size({'width': 400, 'height': 800}); await pg.wait_for_timeout(300)
        w = await pg.evaluate("()=>document.documentElement.scrollWidth")
        chk(w <= 400, f'no sideways scroll at phone width ({w})')
        await pg.screenshot(path=os.path.join(tempfile.gettempdir(), 'updates-phone.png'))
        chk(not errs, f'no page errors {errs}')
        await b.close()

    # set-version.js stamps APP_VERSION (on a copy, so the repo is not changed)
    d = tempfile.mkdtemp()
    try:
        cp = os.path.join(d, 'tilesmith-desktop')
        shutil.copytree(DESKDIR, cp, ignore=shutil.ignore_patterns('node_modules', 'dist', 'mobile', 'android-aistudio', 'bin', '*.pdf', 'crew'))
        r = subprocess.run(['node', os.path.join(cp, 'scripts', 'set-version.js'), '9.8'], capture_output=True, text=True)
        html = open(os.path.join(cp, 'app', 'index.html'), encoding='utf8').read()
        chk(r.returncode == 0 and "const APP_VERSION='9.8';" in html, f'set-version.js stamps APP_VERSION ({r.stdout.strip().splitlines()[-1:]}{r.stderr.strip()[:200]})')
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # installer build settings
    pk = json.load(open(os.path.join(DESKDIR, 'package.json')))
    chk('nsis' in pk['scripts']['dist'] and 'portable' in pk['scripts']['dist'], 'npm run dist builds the Windows installer and the portable app')
    chk(pk['build']['nsis']['artifactName'] == 'TileSmith-${version}-windows-setup.${ext}', 'Windows installer is named TileSmith-<version>-windows-setup.exe')
    chk({t['target'] for t in pk['build']['mac']['target']} == {'dmg', 'pkg'}, 'Mac builds a .dmg and a .pkg installer')
    chk(pk['build']['pkg']['installLocation'] == '/Applications', 'the .pkg installs into Applications')
    print('ALL OK' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
asyncio.run(m())
