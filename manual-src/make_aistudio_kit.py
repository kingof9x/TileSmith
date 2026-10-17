"""Builds TileSmith-Android-AIStudio-Kit.zip: everything Google AI Studio (and a person) needs to build the Android
app exactly as designed. See kit-docs/00-START-HERE.md for what goes in it.

  python3 make_aistudio_kit.py               full build (screenshots, animations, spec, both manuals' mobile part)
  SKIP_SHOTS=1 python3 make_aistudio_kit.py  reuse kit/shots from the last run
  KIT_ZIP=/path/x.zip                        where the zip goes (default /mnt/user-data/outputs)
"""
import json, os, pathlib, re, shutil, subprocess, sys, zipfile

HERE = pathlib.Path(__file__).parent
PROJ = pathlib.Path('/home/claude/tilesmith-desktop')
AS = PROJ / 'android-aistudio'
SHOTS = HERE / 'kit' / 'shots'
NAME = 'TileSmith-Android-AIStudio-Kit'
KIT = HERE / 'kit' / 'build' / NAME
ZIP = pathlib.Path(os.environ.get('KIT_ZIP', f'/mnt/user-data/outputs/{NAME}.zip'))
VERSION = json.loads((PROJ / 'package.json').read_text())['version'].rsplit('.0', 1)[0]
CODE = ''.join(f'{int(x):02d}' for x in (VERSION.split('.') + ['0'])[:3]).lstrip('0')
GROUP_DIR = {'tablet': 'tablet', 'phone': 'phone', 'panel': 'panels', 'pattern': 'patterns', 'wiring': 'wiring', 'shape': 'shapes', 'animation': 'animations'}
GROUP_TITLE = {'tablet': 'Tablet screens (1280 × 800, landscape)', 'phone': 'Phone screens (412 × 915)', 'panel': 'Panels and dialogs (close-ups)',
               'pattern': 'Test patterns (master canvas)', 'wiring': 'Data and power wiring (master canvas)', 'shape': 'Wall shapes and several walls (master canvas)',
               'animation': 'Animations (frame strips and GIFs)'}


def run(*a, **k):
    subprocess.run(list(a), check=True, **k)


def main():
    py = sys.executable
    if not os.environ.get('SKIP_SHOTS'):
        if SHOTS.exists(): shutil.rmtree(SHOTS)
        run(py, str(HERE / 'make_kit_shots.py'), cwd=HERE)
        run(py, str(HERE / 'make_kit_anims.py'), cwd=HERE)
    run(py, str(HERE / 'make_spec.py'), cwd=HERE)
    run(py, str(HERE / 'make_mobile_manual.py'), cwd=HERE)
    if KIT.exists(): shutil.rmtree(KIT)
    KIT.mkdir(parents=True)

    # the page for the Android app, and the complete Android Studio project with it inside
    run('node', str(AS / 'prepare-assets.js'), str(KIT / 'android-assets'))
    shutil.copytree(AS / 'android', KIT / 'android-project', ignore=shutil.ignore_patterns('build', '.gradle', '.idea', 'local.properties', 'assets'))
    run('node', str(AS / 'prepare-assets.js'), str(KIT / 'android-project' / 'app' / 'src' / 'main' / 'assets'))
    (KIT / 'android-project' / '.gitignore').write_text('.gradle/\nbuild/\nlocal.properties\n.idea/\n*.iml\n')
    (KIT / 'android-project' / 'README.txt').write_text((AS / 'README.txt').read_text().replace(
        'BUILD IT IN ANDROID STUDIO\n  1) In this folder:      node prepare-assets.js\n     (it fills android/app/src/main/assets/tilesmith with the current TileSmith page)\n  2) Android Studio > Open > the "android" folder,',
        'BUILD IT IN ANDROID STUDIO\n  The TileSmith page is already in app/src/main/assets/tilesmith.\n  Android Studio > Open > this folder,'))

    # source: exact app, readable split, Android and Capacitor files
    src = KIT / 'source'; src.mkdir()
    shutil.copy(PROJ / 'app' / 'index.html', src / 'index.html')
    sys.path.insert(0, str(HERE)); import make_readable_source as R
    R.main(src / 'readable')
    js_lines = len((src / 'readable' / 'app.js').read_text().split('\n'))
    a = src / 'android'
    shutil.copytree(AS / 'android' / 'app' / 'src' / 'main', a / 'app' / 'src' / 'main', ignore=shutil.ignore_patterns('assets', 'mipmap-*'))
    for f in ('webview-bridge.js', 'prepare-assets.js', 'README.txt'): shutil.copy(AS / f, a / f)
    shutil.copy(AS / 'android' / 'app' / 'build.gradle.kts', a / 'app' / 'build.gradle.kts')
    c = src / 'capacitor'; c.mkdir()
    for f in ('src/mobile-bridge.js', 'scripts/sync-web.js', 'capacitor.config.json', 'package.json'): shutil.copy(PROJ / 'mobile' / f, c / pathlib.Path(f).name)
    (c / 'README.txt').write_text('How the Capacitor build (project folder "mobile", BUILD-ANDROID.txt / BUILD-IOS.txt) connects the same page:\n'
                                  'sync-web.js copies app/index.html into www/ and loads capacitor.js and mobile-bridge.js in front of the app script;\n'
                                  'mobile-bridge.js gives the page window.TSM through the Filesystem, Share, Browser and KeepAwake plugins.\n'
                                  'The AI Studio build gives the page the same window.TSM through webview-bridge.js and Kotlin (source/android).\n')

    # screenshots, grouped
    idx = json.loads((SHOTS / 'index.json').read_text())
    for s in idx:
        d = KIT / 'screenshots' / GROUP_DIR[s['group']]; d.mkdir(parents=True, exist_ok=True)
        shutil.copy(SHOTS / s['file'], d / s['file'])
        s['path'] = f"screenshots/{GROUP_DIR[s['group']]}/{s['file']}"

    # documents
    shutil.copy(PROJ / 'TileSmith-App-Spec.md', KIT / 'TileSmith-App-Spec.md')
    shutil.copy(PROJ / 'TileSmith-Mobile-Manual.pdf', KIT / 'TileSmith-Mobile-Manual.pdf')
    fns = {}
    for i, line in enumerate((src / 'readable' / 'app.js').read_text().split('\n'), 1):
        m = re.match(r'^(?:async )?function (\w+)\s*\(', line) or re.match(r'^\s*(?:const |let |var )?(\w+) = (?:\(|function)', line)
        if m and m.group(1) not in fns: fns[m.group(1)] = i
    rd = lambda p: (AS / 'android' / p).read_text().rstrip('\n')
    gradle = rd('app/build.gradle.kts')
    vals = {'VERSION': VERSION, 'VERSION_CODE': CODE, 'JS_LINES': f'{js_lines:,}', 'N_SHOTS': str(len(idx)),
            'MANIFEST': rd('app/src/main/AndroidManifest.xml'), 'FILE_PATHS': rd('app/src/main/res/xml/file_paths.xml'),
            'THEMES': rd('app/src/main/res/values/themes.xml'), 'THEMES_NIGHT': rd('app/src/main/res/values-night/themes.xml'),
            'COLORS': rd('app/src/main/res/values/colors.xml'), 'COLORS_NIGHT': rd('app/src/main/res/values-night/colors.xml'),
            'MAIN_KT': rd('app/src/main/java/com/tilesmith/android/MainActivity.kt'), 'BRIDGE_KT': rd('app/src/main/java/com/tilesmith/android/TileSmithBridge.kt'),
            'GRADLE_APP': gradle[gradle.index('android {'):], 'BRIDGE_JS': (AS / 'webview-bridge.js').read_text().rstrip('\n')}
    def fill(t):
        def lf(m):
            assert m.group(1) in fns, f'function {m.group(1)} not found in app.js'
            return f'(line {fns[m.group(1)]})'
        t = re.sub(r'\{\{L:(\w+)\}\}', lf, t)
        t = re.sub(r'\{\{(\w+)\}\}', lambda m: vals[m.group(1)], t)
        assert '{{' not in t, 'unfilled placeholder'
        return t
    for f in sorted((HERE / 'kit-docs').glob('*.md')):
        (KIT / f.name).write_text(fill(f.read_text()))
    # 03-SCREENS.md, from the screenshot index
    out = [f'# TileSmith {VERSION}: every screen, panel, pattern and animation\n',
           f'{len(idx)} pictures of the real app running as the Android app (dark mode unless noted). Tablet screens are '
           '1280 × 800 at 1.5× pixel density, phone screens 412 × 915 at 2×. Canvas pictures (patterns, wiring, shapes, '
           'animation frames) are the master canvas itself: exactly what the app outputs. Paths are relative to this file.\n',
           '**How to reach each screen:** sections and submenus open by tapping their title in the settings panel (left on a tablet, top on a phone). '
           'The top bar buttons are named in each title. Editing modes (Wire tiles, Remove tiles, Mark half tiles) are buttons inside their submenus.\n']
    for g in GROUP_DIR:
        items = [s for s in idx if s['group'] == g]
        if not items: continue
        out.append(f'\n## {GROUP_TITLE[g]}\n')
        for s in items:
            note = f"\n\n{s['notes']}" if s['notes'] else ''
            if s['file'].endswith('.gif'):
                out.append(f"### {s['title']}\n\n![{s['title']}]({s['path']}) (animated GIF: `{s['path']}`){note}\n")
            else:
                out.append(f"### {s['title']}\n\n![{s['title']}]({s['path']}){note}\n")
    (KIT / '03-SCREENS.md').write_text('\n'.join(out))
    # route B: the 12 rewrite prompts, assembled with their spec sections and code (needs the filled docs above)
    import make_route_b_prompts as RB
    RB.main(KIT)

    # zip
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(KIT.rglob('*')):
            if p.is_file():
                info = zipfile.ZipInfo.from_file(p, f'{NAME}/{p.relative_to(KIT)}')
                if p.name == 'gradlew': info.external_attr = 0o100755 << 16
                with open(p, 'rb') as fh: z.writestr(info, fh.read(), zipfile.ZIP_DEFLATED)
    n = sum(1 for p in KIT.rglob('*') if p.is_file())
    print(f'[ok] {ZIP} ({ZIP.stat().st_size / 1e6:.1f} MB, {n} files)')


if __name__ == '__main__':
    main()
