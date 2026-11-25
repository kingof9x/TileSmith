#!/usr/bin/env python3
"""Measure how much memory a running app uses, counting EVERY process it starts.

Why this exists
---------------
An Electron app is not one process. TileSmith (Electron) starts a main process, a GPU process, a network/utility
process, a zygote and one renderer per window. Task Manager, Activity Monitor and `top` each show one line per
process, so looking at one line under-counts the app. A native app (for example a Rust rewrite) is usually a single
process. To compare the two fairly this script adds up every process in the app's process tree.

It reports three numbers, all from Linux /proc:

  RSS  Resident Set Size: pages in RAM, shared pages counted again in every process that maps them. Over-counts
       when several processes share libraries (Electron's do). This is roughly the "Memory" column in `top`.
  PSS  Proportional Set Size: each shared page divided between the processes that share it. Summing PSS over the
       tree gives the fairest single "how much RAM does this app cost" number. This is the headline figure.
  USS  Unique Set Size (Private_Clean + Private_Dirty): pages only this process uses, the RAM you would get back if
       you quit the app. Closest to Windows Task Manager's default "Memory (active private working set)".

Usage
-----
  python3 measure_memory.py --label "TileSmith 3.10 AppImage" --wait 20,60,120 -- <command to start the app> [args]
  python3 measure_memory.py --pid 12345 --json -      (one sample of a tree that is already running, as JSON)

The script starts the command, waits, and samples the whole process tree at each time in --wait (seconds after
start). It prints a table and, with --json FILE, writes the raw numbers. Run it under `xvfb-run -a` on a machine with
no screen. Linux only (it reads /proc/<pid>/smaps_rollup, Linux 4.14+).
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time


def children_of(pid):
    """All descendant pids of pid (the whole process tree below it), read from /proc/*/stat."""
    parent = {}
    for d in os.listdir('/proc'):
        if not d.isdigit():
            continue
        try:
            with open(f'/proc/{d}/stat') as f:
                # field 4 is the parent pid; the command name (field 2) can contain spaces, so split after ')'
                parent[int(d)] = int(f.read().rsplit(')', 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            pass
    tree, todo = [], [pid]
    while todo:
        p = todo.pop()
        tree.append(p)
        todo.extend(c for c, pp in parent.items() if pp == p)
    return tree


def mem_of(pid):
    """(rss, pss, uss) of one process in KiB from /proc/<pid>/smaps_rollup, or None if it has gone."""
    try:
        with open(f'/proc/{pid}/smaps_rollup') as f:
            v = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[0].endswith(':') and parts[1].isdigit():
                    v[parts[0][:-1]] = int(parts[1])
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            # Chromium rewrites its argv as one space-separated string, so split on both NUL and spaces
            cmd = f.read().replace(b'\0', b' ').decode(errors='replace').split()
        # Chromium child processes say what they are with --type=renderer / gpu-process / utility / zygote
        kind = next((a[7:] for a in cmd if a.startswith('--type=')), 'main')
        return kind, v.get('Rss', 0), v.get('Pss', 0), v.get('Private_Clean', 0) + v.get('Private_Dirty', 0)
    except OSError:
        return None


def sample(root):
    rows = [r for r in (mem_of(p) for p in children_of(root)) if r]
    return {
        'processes': len(rows),
        'kinds': sorted(r[0] for r in rows),
        'rss_mib': round(sum(r[1] for r in rows) / 1024, 1),
        'pss_mib': round(sum(r[2] for r in rows) / 1024, 1),
        'uss_mib': round(sum(r[3] for r in rows) / 1024, 1),
        'per_process': [{'kind': r[0], 'rss_mib': round(r[1] / 1024, 1), 'pss_mib': round(r[2] / 1024, 1),
                         'uss_mib': round(r[3] / 1024, 1)} for r in rows],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--label', default='app')
    ap.add_argument('--wait', default='20,60', help='comma separated seconds after start to sample at')
    ap.add_argument('--json', help='write the samples to this file')
    ap.add_argument('--shot', help='save a screenshot of the X display at the last sample (needs ImageMagick import), '
                    'to check the app really loaded')
    ap.add_argument('--pid', type=int, help='sample the already running process tree under this pid once, then exit')
    ap.add_argument('cmd', nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.pid:
        s = sample(a.pid)
        print(json.dumps(s) if a.json == '-' else
              f"{a.label:32} {s['processes']:2d} processes  PSS {s['pss_mib']:7.1f} MiB  USS {s['uss_mib']:7.1f} MiB  "
              f"RSS {s['rss_mib']:7.1f} MiB")
        return
    cmd = a.cmd[1:] if a.cmd[:1] == ['--'] else a.cmd
    if not cmd:
        ap.error('give the command that starts the app after --')
    waits = [float(x) for x in a.wait.split(',')]
    # own process group, so the whole tree can be stopped at the end
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    t0, out = time.time(), []
    try:
        for w in waits:
            time.sleep(max(0, t0 + w - time.time()))
            if proc.poll() is not None:
                sys.exit(f'{a.label}: the app exited (code {proc.returncode}) before {w:.0f} s')
            s = sample(proc.pid)
            s['at_s'] = w
            out.append(s)
            if a.shot and w == waits[-1]:
                subprocess.run(['import', '-window', 'root', a.shot], check=False)
            print(f"{a.label:32} {w:5.0f} s  {s['processes']:2d} processes  PSS {s['pss_mib']:7.1f} MiB  "
                  f"USS {s['uss_mib']:7.1f} MiB  RSS {s['rss_mib']:7.1f} MiB")
    finally:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
    if a.json:
        with open(a.json, 'w') as f:
            json.dump({'label': a.label, 'cmd': cmd, 'samples': out}, f, indent=1)


if __name__ == '__main__':
    main()
