# Shared lists stay merge-friendly (see "Parallel PRs without merge conflicts" in manual-src/WORKFLOW.md):
# TR, S, WK and LIM in app/index.html and KEYDESC in make_spec.py have one entry per line, ending in a comma,
# under "// Feature" (or "# Feature") headers, with Core first and the feature groups in A to Z order.
# No browser needed. Run `npm install` in manual-src/tools once (acorn).
import ast, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE)
ROOT = os.environ.get('TILESMITH_ROOT') or os.path.dirname(SRC)
APP = os.path.join(ROOT, 'tilesmith-desktop', 'app', 'index.html')
ok = True
def bad(msg):
    global ok; ok = False; print('FAIL', msg)
def groups_ok(name, heads):
    feats = [h for h in heads if h != 'Core']
    if not heads or heads[0] != 'Core': bad(f'{name}: first group must be "Core", got {heads[:1]}')
    if feats != sorted(feats, key=str.lower): bad(f'{name}: feature groups not in A to Z order: {feats}')
    if len(set(heads)) != len(heads): bad(f'{name}: a group header appears twice: {heads}')

html = open(APP, encoding='utf8').read()
d = json.loads(subprocess.run(['node', os.path.join(SRC, 'tools', 'lists.js'), APP], capture_output=True, text=True, check=True).stdout)
for name in ['TR', 'S', 'WK', 'LIM']:
    if name not in d: bad(f'{name} not found'); continue
    v = d[name]; body = html[v['start']:v['end']]; lines = body.split('\n')
    if lines[0] not in ('{', '[') or lines[-1] not in ('}', ']'): bad(f'{name}: opening/closing bracket must be on its own line')
    items = set(i['src'] + ',' for i in v['items']); heads = []
    for ln in lines[1:-1]:
        if ln.startswith('// '):
            if not ln.startswith('// ' + {'TR': 'Translations', 'S': 'Settings', 'WK': 'Per-wall', 'LIM': 'Number'}[name]): heads.append(ln[3:].strip())
        elif ln not in items: bad(f'{name}: line is not exactly one entry with a trailing comma: {ln[:100]}')
    keys = [i['key'] for i in v['items']]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup: bad(f'{name}: duplicate keys {dup[:5]}')
    groups_ok(name, heads)
    print(name, len(keys), 'entries,', len(heads), 'groups')

spec = open(os.path.join(SRC, 'make_spec.py'), encoding='utf8').read(); t = ast.parse(spec)
kd = [n for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'KEYDESC'][0].value
rows = [k.lineno for k in kd.keys]
if len(rows) != len(set(rows)): bad('KEYDESC: more than one key on a line')
for k, v in zip(kd.keys, kd.values):
    if v.end_lineno != k.lineno: bad(f'KEYDESC: {k.value} spans several lines')
print('KEYDESC', len(rows), 'keys')
print('ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
