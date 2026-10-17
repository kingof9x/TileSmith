import re, sys, json, datetime, pathlib
v=sys.argv[1]; root=pathlib.Path('/home/claude/tilesmith-desktop'); today=datetime.date.today().isoformat()
def sub(path, pat, rep, count=1):
    p=root/path; s=p.read_text(encoding='utf-8'); s2,n=re.subn(pat, rep, s)
    assert n>=count, (path, pat, n); p.write_text(s2, encoding='utf-8')
sub('app/index.html', r'<title>TileSmith v[\d.]+ - LED Wall Builder</title>', f'<title>TileSmith v{v} - LED Wall Builder</title>')
sub('app/index.html', r'color:var\(--am\)">v[\d.]+</span></h1>', f'color:var(--am)">v{v}</span></h1>')
sub('app/index.html', r'>Version [\d.]+ ·[^<]*</div>', f'>Version {v} · build {today}</div>')
sub('main.js', r"title: 'TileSmith v[\d.]+ - LED Wall Builder'", f"title: 'TileSmith v{v} - LED Wall Builder'")
sub('package.json', r'"version": "[\d.]+"', f'"version": "{v}.0"')
for f in ('BUILD-WINDOWS.txt','BUILD-MAC.txt'):
    sub(f, r'TILESMITH v[\d.]+', f'TILESMITH v{v}')
    sub(f, r'header say "v[\d.]+"', f'header say "v{v}"')
sub('BUILD-MAC.txt', r'TileSmith-[\d.]+-mac-universal\.dmg', f'TileSmith-{v}.0-mac-universal.dmg')
print('version', v, today)
# mobile app (Capacitor): package version, Android versionName/versionCode, iOS marketing version/build number
code = ''.join(f'{int(x):02d}' for x in (v.split('.') + ['0'])[:3]).lstrip('0') or '1'   # 3.3 -> 30300
sub('mobile/package.json', r'"version": "[\d.]+"', f'"version": "{v}.0"')
sub('mobile/android/app/build.gradle', r'versionCode \d+', f'versionCode {code}')
sub('mobile/android/app/build.gradle', r'versionName "[^"]*"', f'versionName "{v}"')
sub('mobile/ios/App/App.xcodeproj/project.pbxproj', r'MARKETING_VERSION = [\d.]+;', f'MARKETING_VERSION = {v};', 2)
sub('mobile/ios/App/App.xcodeproj/project.pbxproj', r'CURRENT_PROJECT_VERSION = \d+;', f'CURRENT_PROJECT_VERSION = {code};', 2)
for f in ('BUILD-ANDROID.txt', 'BUILD-IOS.txt'):
    sub(f, r'TILESMITH v[\d.]+', f'TILESMITH v{v}')
    sub(f, r'TileSmith v[\d.]+ \.\.\.', f'TileSmith v{v} ...')
print('mobile version', v, code)
# Google AI Studio / Kotlin Android app (android-aistudio): versionCode and versionName
sub('android-aistudio/android/app/build.gradle.kts', r'versionCode = \d+', f'versionCode = {code}')
sub('android-aistudio/android/app/build.gradle.kts', r'versionName = "[^"]*"', f'versionName = "{v}"')
print('AI Studio Android version', v, code)
