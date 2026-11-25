"""Runs every manual-src/tests/*_test.py and prints one line per test, then a summary. Exit code 0 only when every test
passed. A test passes when it exits 0 AND its output does not say FAILED / PROBLEMS / SOME FAILED (several older tests
print a verdict but always exit 0, so the exit code alone is not trusted).

  python3 manual-src/tests/run_all.py              every test
  python3 manual-src/tests/run_all.py cable labels only the named ones (cable_test.py, labels_test.py)
  python3 manual-src/tests/run_all.py -j 4         four at a time (default: number of CPUs, at most 6)

Needs Python Playwright with Chromium (pip install playwright; python -m playwright install chromium). Some tests also
use Pillow, pypdf and pdftotext (binder, layers, pdf); android_test.py needs Node. Each test's full output is written to
<temp>/tilesmith-tests/<name>.log."""
import os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
BAD = re.compile(r'^(FAILED|SOME FAILED|PROBLEMS)\b|\bTraceback \(most recent call last\)', re.M)
CHK = re.compile(r'^FAIL ', re.M)   # a failed check line; android_test also prints "FAIL toast" for a tested error message
def run(name):
    log = os.path.join(tempfile.gettempdir(), 'tilesmith-tests', name + '.log'); t = time.time()
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, name + '.py')], cwd=HERE, capture_output=True, text=True, timeout=600)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or b'').decode(errors='replace') + '\nTIMED OUT after 600 s', -1
    open(log, 'w').write(out)
    last = [l for l in out.strip().split('\n') if l.strip()][-1:] or ['']
    ok = rc == 0 and not BAD.search(out) and (not CHK.search(out) or last[0].strip() == 'ALL OK')
    return name, ok, time.time() - t, last[0][:110], log
def main():
    a = sys.argv[1:]; jobs = min(6, os.cpu_count() or 2)
    if '-j' in a: i = a.index('-j'); jobs = int(a[i + 1]); del a[i:i + 2]
    names = sorted(f[:-3] for f in os.listdir(HERE) if f.endswith('_test.py'))
    if a: names = [n for n in names if n[:-5] in a or n in a]
    os.makedirs(os.path.join(tempfile.gettempdir(), 'tilesmith-tests'), exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex: res = list(ex.map(run, names))
    for n, ok, s, last, log in res: print(f"{'ok  ' if ok else 'FAIL'} {n:<22} {s:5.1f}s  {'' if ok else last}")
    bad = [r for r in res if not r[1]]
    print(f'\n{len(res) - len(bad)} of {len(res)} passed' + (''.join(f'\n  {r[0]}: see {r[4]}' for r in bad)))
    sys.exit(1 if bad else 0)
if __name__ == '__main__': main()
