"""The desktop app in real Electron (not a browser page): window security, the update download check and autosave recovery.
Needs tilesmith-desktop/node_modules (npm install there) and, on Linux without a screen, xvfb-run. Without them it prints
SKIPPED and exits 0.
  windows.js       an output window on a display draws the canvas; a blank print window works; window.open of a web
                   address is refused and a clicked web link does not take over the app window (both go to the browser)
  update_digest.js Update now installs only a download whose SHA-256 matches the digest GitHub lists for the release file
  autosave.js      a damaged state.json is kept as state.json.unreadable-<time>, the app starts fresh and says so, and
                   the next autosave writes a complete state.json"""
import json, os, shutil, subprocess, sys, tempfile
from _paths import TS_DESK
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'electron')
EL = os.path.join(TS_DESK, 'node_modules', '.bin', 'electron')
def run(script, env=None):
    cmd = ([shutil.which('xvfb-run'), '-a'] if sys.platform.startswith('linux') and not os.environ.get('DISPLAY') else []) + \
          [EL, '--no-sandbox', '--disable-gpu', os.path.join(HERE, 'harness.js')]
    # a throw-away settings folder, so the test never touches your own saved TileSmith session
    t = tempfile.mkdtemp(); e = dict(os.environ, ETEST_DIR=TS_DESK, ETEST_JS=open(os.path.join(HERE, script)).read(), XDG_CONFIG_HOME=t, APPDATA=t)
    if sys.platform == 'darwin': e['HOME'] = t
    e.update(env or {})
    out = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=120).stdout
    for l in out.split('\n'):
        if l.startswith('RESULT {'): return json.loads(l[7:])
    print(out[-2000:]); return None
def main():
    if not os.path.exists(EL) or (sys.platform.startswith('linux') and not os.environ.get('DISPLAY') and not shutil.which('xvfb-run')):
        print('SKIPPED: needs npm install in tilesmith-desktop (and xvfb-run on Linux without a screen)'); return
    ok = True
    def chk(c, m):
        nonlocal ok; print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
    r = run('windows.js') or {}; print(r)
    chk(r.get('outOpen') and r.get('outPx', [0])[3] == 255, 'output window opens on the display and shows the canvas')
    chk(r.get('blank') == 'hello', 'blank child window (print preview) works')
    chk(r.get('webWindow') == 'denied' and r.get('stillApp'), 'web pages never open inside the app')
    r = run('update_digest.js') or {}; print(r)
    chk('does not match' in r.get('bad', {}).get('msg', '') and r['bad']['sent'] == 0, 'a download with the wrong SHA-256 is not installed')
    chk(r.get('good', {}).get('sent') == [['ts-update-run', '/bin/sh']] if sys.platform.startswith('linux') else r.get('good'), 'a matching download is installed')
    chk(r.get('none', {}).get('sent') == 1, 'a release without a digest still installs')
    cfg = tempfile.mkdtemp(); os.makedirs(os.path.join(cfg, 'TileSmith'))
    open(os.path.join(cfg, 'TileSmith', 'state.json'), 'w').write('{"S":{"cols":5},"walls":[{"cols":')
    r = run('autosave.js', {'XDG_CONFIG_HOME': cfg, 'APPDATA': cfg}) or {}; print(r)
    files = os.listdir(os.path.join(cfg, 'TileSmith'))
    chk(any(f.startswith('state.json.unreadable-') for f in files), f'damaged save kept {files}')
    chk('could not be restored' in r.get('toast', ''), 'the user is told')
    chk(json.load(open(os.path.join(cfg, 'TileSmith', 'state.json')))['walls'][0]['name'] == 'Saved wall' and 'state.json.tmp' not in files, 'next autosave is complete, no temp file left')
    print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
main()
