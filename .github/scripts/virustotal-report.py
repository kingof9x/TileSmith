#!/usr/bin/env python3
"""Writes the scan table of one release into VIRUSTOTAL.md (newest release first; scanning a release again replaces its section).
Usage: virustotal-report.py <tag> <rows file> <VIRUSTOTAL.md>"""
import sys, re, datetime, pathlib
tag, rows, out = sys.argv[1], pathlib.Path(sys.argv[2]).read_text().strip(), pathlib.Path(sys.argv[3])
HEAD = """# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.
"""
sections = {}
if out.exists():
    for part in re.split(r'\n(?=## )', out.read_text()):
        m = re.match(r'## (\S+)', part)
        if m: sections[m.group(1)] = part.strip()
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
sections[tag] = f"## {tag}\n\nScanned {now}.\n\n| File | Result | SHA-256 |\n|---|---|---|\n{rows}"
def key(t):
    n = re.findall(r'\d+', t); return [int(x) for x in n]
order = sorted(sections, key=key, reverse=True)
out.write_text(HEAD + '\n' + '\n\n'.join(sections[t] for t in order) + '\n')
print('wrote', out, 'with', ', '.join(order))
