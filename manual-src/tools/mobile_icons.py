# Makes the Android and iOS app icons and splash screens for mobile/ from build/icon.png (1024 px).
import pathlib
from PIL import Image, ImageDraw
ROOT = pathlib.Path('/home/claude/tilesmith-desktop'); M = ROOT / 'mobile'
src = Image.open(ROOT / 'build' / 'icon.png').convert('RGBA')
W = src.width
top, bot = src.getpixel((W // 2, 40))[:3], src.getpixel((W // 2, W - 40))[:3]
mid = tuple((a + b) // 2 for a, b in zip(top, bot)); hexmid = '#%02X%02X%02X' % mid
def grad(n):
    g = Image.new('RGBA', (n, n)); d = ImageDraw.Draw(g)
    for y in range(n):
        t = y / (n - 1); d.line([(0, y), (n, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bot)) + (255,))
    return g
# the tile grid alone: pixels close to the background gradient become transparent
px = src.load(); grid = Image.new('RGBA', src.size, (0, 0, 0, 0)); gp = grid.load()
for y in range(W):
    t = y / (W - 1); bg = [a + (b - a) * t for a, b in zip(top, bot)]
    for x in range(W):
        r, g, b, a = px[x, y]
        if a < 250: continue
        d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
        if d > 18: gp[x, y] = (r, g, b, 255 if d > 60 else int(255 * (d - 18) / 42))
box = grid.getbbox(); grid = grid.crop(box); print('grid box', box, 'bg', top, bot, hexmid)
full = grad(W); full.alpha_composite(src)                              # full-bleed square (iOS masks the corners itself)
def on(size, frac, bgcol=None):                                        # grid centred at frac of the size
    im = Image.new('RGBA', (size, size), bgcol + (255,) if bgcol else (0, 0, 0, 0))
    s = round(size * frac); g = grid.resize((s, s), Image.LANCZOS); im.alpha_composite(g, ((size - s) // 2, (size - s) // 2)); return im
res = M / 'android/app/src/main/res'
for d, n in {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}.items():
    src.resize((n, n), Image.LANCZOS).save(res / f'mipmap-{d}/ic_launcher.png')
    r = on(n * 4, .58, mid); mask = Image.new('L', r.size, 0); ImageDraw.Draw(mask).ellipse([0, 0, r.width - 1, r.height - 1], fill=255)
    r.putalpha(mask); r.resize((n, n), Image.LANCZOS).save(res / f'mipmap-{d}/ic_launcher_round.png')
    f = round(n * 108 / 48); on(f * 2, .44).resize((f, f), Image.LANCZOS).save(res / f'mipmap-{d}/ic_launcher_foreground.png')
(res / 'values/ic_launcher_background.xml').write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{hexmid}</color>\n</resources>\n')
SPL = (13, 18, 23)
def splash(w, h):
    im = Image.new('RGBA', (w, h), SPL + (255,)); s = round(min(w, h) * .28); im.alpha_composite(src.resize((s, s), Image.LANCZOS), ((w - s) // 2, (h - s) // 2)); return im.convert('RGB')
for p in sorted(res.glob('drawable*/splash.png')):
    w, h = Image.open(p).size; splash(w, h).save(p)
ios = M / 'ios/App/App/Assets.xcassets'
full.convert('RGB').save(ios / 'AppIcon.appiconset/AppIcon-512@2x.png')
sp = splash(2732, 2732)
for n in ('splash-2732x2732.png', 'splash-2732x2732-1.png', 'splash-2732x2732-2.png'): sp.save(ios / 'Splash.imageset' / n)
print('done')
