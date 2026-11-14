# UI languages: Spanish, Portuguese (Brazil), German, French, Simplified Chinese, Japanese, Korean, Italian and Dutch.
# Checks every TR entry has all nine translations with the same {0} placeholders as the English (a placeholder right after
# a letter, like the plural "s" in tile{1}, may be left out or repeated), the Info > Preferences picker lists every language, each
# language loads without errors and translates the main panels, the browser language picks the first-visit language,
# Chinese / Japanese / Korean get a CJK system font after the UI font, and the PDF binder stays in Latin text (it is
# written with the PDF's built-in Helvetica, which has no CJK glyphs, so nothing translated may reach it).
# Needs Playwright with Chromium, pdftotext and pypdf. Screenshots go to $I18N_SHOTS when it is set.
import asyncio, collections, json, os, re, subprocess, sys, tempfile
from playwright.async_api import async_playwright
APP = 'file:///home/claude/tilesmith-desktop/app/index.html'
SHOTS = os.environ.get('I18N_SHOTS')
LANGS = ['es', 'pt-BR', 'de', 'fr', 'zh-CN', 'ja', 'ko', 'it', 'nl']
ok = True
def chk(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(800)

        # --- the table: nine strings per entry, placeholders kept ---
        tr = await pg.evaluate("()=>({TR,LIX,LANGS})")
        chk(list(tr['LIX'].keys()) == LANGS and list(tr['LIX'].values()) == list(range(9)), f"LIX lists the nine languages in TR order {tr['LIX']}")
        chk(set(tr['LANGS']) == set(['en'] + LANGS), 'LANGS names English and the nine translations')
        short = [k for k, v in tr['TR'].items() if len(v) < 9 or not all(isinstance(x, str) and x.strip() for x in v[:9])]
        chk(not short, f'every TR entry has nine non-empty translations ({len(tr["TR"])} entries; incomplete: {short[:5]})')
        bad = []
        for k, v in tr['TR'].items():
            a = collections.Counter(re.findall(r'\{\d+\}', k)); plural = set(re.findall(r'(?<=[a-z])(\{\d+\})', k))
            for i, t in enumerate(v):
                c = collections.Counter(re.findall(r'\{\d+\}', t))
                if any(x not in plural for x in c - a) or any(x not in plural for x in a - c): bad.append((LANGS[i], k[:50], t[:50]))
        chk(not bad, f'placeholders match the English in every language {bad[:5]}')
        cjk = re.compile(r'[぀-ヿ㐀-鿿가-힯]')
        latin_in_cjk = [(LANGS[i], v[i][:40]) for v in tr['TR'].values() for i in (4, 5, 6) if len(v[i]) > 25 and not cjk.search(v[i])]
        chk(len(latin_in_cjk) < 40, f'Chinese, Japanese and Korean entries are written in their own script (untouched long lines: {latin_in_cjk[:5]})')

        # --- the picker ---
        await pg.click('[data-a=about]'); await pg.wait_for_timeout(300)
        opts = await pg.evaluate("()=>[...document.querySelector('select[data-lang]').options].map(o=>[o.value,o.textContent])")
        chk([o[0] for o in opts] == ['en', 'es', 'pt-BR', 'de', 'fr', 'it', 'nl', 'zh-CN', 'ja', 'ko'], f'the Language picker lists every language {opts}')
        chk(dict(opts)['zh-CN'] == '简体中文' and dict(opts)['ja'] == '日本語' and dict(opts)['ko'] == '한국어' and dict(opts)['de'] == 'Deutsch', 'each language is named in its own language')
        await pg.click('#cls')

        # --- each language: switch, no errors, panels translated, html lang, fonts ---
        want = {'de': 'Wand hinzufügen', 'fr': 'Ajouter un mur', 'zh-CN': '添加屏体', 'ja': 'ウォールを追加', 'ko': '월 추가', 'it': 'Aggiungi ledwall', 'nl': 'Ledwall toevoegen', 'es': None, 'pt-BR': None}
        for i, l in enumerate(LANGS):
            await pg.click('[data-a=about]'); await pg.wait_for_timeout(200)
            await pg.select_option('select[data-lang]', l); await pg.wait_for_timeout(250); await pg.click('#cls'); await pg.wait_for_timeout(150)
            r = await pg.evaluate("""l=>({lang:document.documentElement.lang,LG,saved:localStorage.getItem('tilesmith-lang'),
              add:[...document.querySelectorAll('button')].map(b=>b.textContent.trim()),font:getComputedStyle(document.body).fontFamily,
              eng:[...document.querySelectorAll('#right summary')].slice(0,3).map(s=>s.textContent.trim()),
              left:document.getElementById('app').innerText.slice(0,4000)})""", l)
            chk(r['lang'] == l and r['LG'] == l and r['saved'] == l, f'{l}: html lang, LG and the saved choice follow the picker')
            exp = want[l] or tr['TR']['Add wall'][i]
            chk(exp in r['add'], f'{l}: "Add wall" reads "{exp}"')
            words = re.findall(r'[A-Za-z]{5,}', r['left']); print('   ', l, 'English-looking words left on screen:', len(words), collections.Counter(words).most_common(8))
            if l in ('zh-CN', 'ja', 'ko'):
                fam = {'zh-CN': 'Microsoft YaHei', 'ja': 'Yu Gothic', 'ko': 'Malgun Gothic'}[l]
                chk('JetBrains Mono' in r['font'] and fam in r['font'], f'{l}: the UI font stays first and a {l} system font follows it')
                w = await pg.evaluate("()=>{const c=document.createElement('canvas').getContext('2d');c.font='20px '+getComputedStyle(document.body).fontFamily;return [c.measureText('箱体회로パネル').width,c.measureText('\\u0378\\u0379').width]}")
                chk(w[0] > 100, f'{l}: CJK text has real glyphs (7 characters measure {w[0]:.0f}px)')
            else:
                chk('JetBrains Mono' in r['font'] and 'YaHei' not in r['font'], f'{l}: Latin languages keep the plain UI font')
            if SHOTS:
                os.makedirs(SHOTS, exist_ok=True); await pg.screenshot(path=os.path.join(SHOTS, f'{l}.png'))
        chk(not errs, f'no page errors while switching languages {errs[:3]}')

        # reload keeps the language; back to English restores the English text
        await pg.reload(); await pg.wait_for_timeout(800)
        chk(await pg.evaluate("()=>LG") == 'nl' and await pg.evaluate("()=>document.documentElement.lang") == 'nl', 'the last language comes back after a reload')
        await pg.evaluate("()=>setLang('en')"); await pg.wait_for_timeout(200)
        chk('Add wall' in await pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.textContent.trim())"), 'English comes back when English is picked')

        # --- the binder PDF stays Latin in Japanese (Helvetica has no CJK) ---
        await pg.evaluate("()=>{localStorage.clear()}"); await pg.reload(); await pg.wait_for_timeout(700)
        await pg.evaluate("""()=>{S.cols=8;S.rows=4;S.proc='NovaStar VX1000 Pro';applySpec();S.pdist=true;S.bShow='Tour';sync();setLang('ja')}"""); await pg.wait_for_timeout(300)
        out = tempfile.mkdtemp(prefix='i18n')
        async with pg.expect_download() as d: await pg.click('[data-a=binder]:visible')
        dl = await d.value; f = os.path.join(out, dl.suggested_filename); await dl.save_as(f)
        t = subprocess.run(['pdftotext', '-layout', f, '-'], capture_output=True, text=True).stdout
        chk(len(t) > 500 and not cjk.search(t) and '??' not in t, f'Japanese UI: the binder PDF has its English text and no ? boxes ({len(t)} chars)')
        await b.close()
    print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)

asyncio.run(main())
