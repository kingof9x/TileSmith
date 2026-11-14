# One-time helper for a feature branch that still has the old long-line lists (TR / S / WK / LIM in app/index.html,
# KEYDESC in make_spec.py) when it merges a main that has them one entry per line in "// Feature" groups
# (see "Parallel PRs without merge conflicts" in manual-src/WORKFLOW.md).
#
#   git fetch origin main && git merge origin/main      # stops with conflicts in index.html and/or make_spec.py
#   python3 manual-src/tools/regroup_merge.py "Your feature"
#
# For each of the two files it redoes the merge with the lists taken from main and this branch's new entries added as a
# "// Your feature" (or "# Your feature") group at its A to Z place; entries this branch changed are changed in place.
# Anything else that conflicts (ordinary code) is left with the usual conflict markers for you to fix.
# Then: fix those, run tests/lists_test.py and your feature's test, git add, git commit.
import ast, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
TMP = os.path.join(ROOT, '.git', 'regroup')
if len(sys.argv) < 2: sys.exit('usage: regroup_merge.py "Feature name"')
group = sys.argv[1].strip(); os.makedirs(TMP, exist_ok=True)

def js_lists(text):
    p = os.path.join(TMP, 'x.html'); open(p, 'w', encoding='utf8').write(text)
    return json.loads(subprocess.run(['node', os.path.join(HERE, 'lists.js'), p], capture_output=True, text=True, check=True).stdout)
def py_lists(text):
    lines = text.split('\n'); off = [0]
    for l in lines: off.append(off[-1] + len(l) + 1)
    pos = lambda ln, col: off[ln - 1] + len(lines[ln - 1].encode('utf8')[:col].decode('utf8'))
    d = [n for n in ast.parse(text).body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'KEYDESC'][0].value
    items = [{'key': k.value, 'src': text[pos(k.lineno, k.col_offset):pos(v.end_lineno, v.end_col_offset)]} for k, v in zip(d.keys, d.values)]
    return {'KEYDESC': {'start': pos(d.lineno, d.col_offset), 'end': pos(d.end_lineno, d.end_col_offset), 'items': items}}
FILES = [('tilesmith-desktop/app/index.html', js_lists, '', '// '), ('manual-src/make_spec.py', py_lists, '  ', '  # ')]

def norm(s):  # ignore whitespace outside string literals (a branch may have re-spaced entries while fixing a conflict)
    return re.sub(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|\s+', lambda m: m.group(1) or '', s)
def show(n, rel):
    r = subprocess.run(['git', '-C', ROOT, 'show', f':{n}:{rel}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

for rel, get, ind, cm in FILES:
    B, O, T = show(1, rel), show(2, rel), show(3, rel)
    if B is None or O is None or T is None: print(f'{rel}: not in conflict, skipped'); continue
    LB, LO, LT = get(B), get(O), get(T)
    def body(name, extra, changed):
        v = LT[name]; lines = T[v['start']:v['end']].split('\n'); src = {ind + i['src'] + ',': i['key'] for i in v['items']}
        if len(lines) < 3 or any(l.strip() and l not in src and not l.startswith(cm.rstrip()) and l not in '{}[]' for l in lines[1:-1]):
            sys.exit(f'{rel}: {name} on main is not one entry per line yet; merge main as usual')
        lines = [ind + changed[src[l]] + ',' if l in src and src[l] in changed else l for l in lines]
        if extra:
            heads = [(i, l[len(cm):]) for i, l in enumerate(lines) if l.startswith(cm) and i > 1]
            if any(h == group for _, h in heads): sys.exit(f'{name} already has a "{cm.strip()} {group}" group; pick another name')
            at = next((i for i, h in heads if h not in ('Core', 'per wall') and h.lower() > group.lower()), len(lines) - 1)
            lines[at:at] = [cm + group] + [ind + s + ',' for s in extra]
        return '\n'.join(lines)
    def swap(text, data, bodies):
        for name in sorted(bodies, key=lambda n: -data[n]['start']):
            v = data[name]; text = text[:v['start']] + bodies[name] + text[v['end']:]
        return text
    ob, bb = {}, {}
    for name in LT:
        if name not in LO or name not in LB: continue
        bk = {i['key']: i['src'] for i in LB[name]['items']}; tk = {i['key']: i['src'] for i in LT[name]['items']}
        ok = {i['key'] for i in LO[name]['items']}
        extra = [i['src'] for i in LO[name]['items'] if i['key'] not in bk and i['key'] not in tk]
        changed = {i['key']: i['src'] for i in LO[name]['items'] if i['key'] in bk and norm(bk[i['key']]) != norm(i['src']) and i['key'] in tk and norm(tk[i['key']]) == norm(bk[i['key']])}
        gone = [k for k in bk if k in tk and k not in ok]
        if gone: print(f'note: {name}: this branch removed {gone[:5]}; they are kept from main, remove them by hand if needed')
        ob[name] = body(name, extra, changed); bb[name] = T[LT[name]['start']:LT[name]['end']]
        print(f'{name}: {len(extra)} new entries in "{cm.strip()} {group}", {len(changed)} changed in place')
    o2, b2, t2 = (os.path.join(TMP, x) for x in ('ours', 'base', 'theirs'))
    open(o2, 'w', encoding='utf8').write(swap(O, LO, ob)); open(b2, 'w', encoding='utf8').write(swap(B, LB, bb)); open(t2, 'w', encoding='utf8').write(T)
    r = subprocess.run(['git', 'merge-file', '-p', '-L', 'this branch', '-L', 'merge base', '-L', 'origin/main', o2, b2, t2], capture_output=True, text=True)
    open(os.path.join(ROOT, rel), 'w', encoding='utf8').write(r.stdout)
    print(f'{rel}: merged cleanly, git add it' if r.returncode == 0 else f'{rel}: {r.returncode} conflict(s) left outside the lists: fix them, then git add')
