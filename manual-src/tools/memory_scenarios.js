// Memory use of the TileSmith desktop app (Electron) in a few everyday states.
//
// Starts the app with Playwright's Electron driver, puts it in each state (idle, LED build running, DVD screensaver
// running), waits for memory to settle, and samples the whole process tree with measure_memory.py --pid.
// See measure_memory.py for what RSS, PSS and USS mean and why every process is counted.
//
//   xvfb-run -a -s "-screen 0 1920x1080x24" node memory_scenarios.js <path to the TileSmith or electron binary> [app dir]
//
// Give the extracted AppImage binary (squashfs-root/tilesmith) to measure a release exactly as users get it, or
// node_modules/.bin/electron plus tilesmith-desktop to measure the source tree. Writes memory-results.json next to this script.
// Linux only. HOME and XDG_CONFIG_HOME should point at an empty folder so saved settings do not change the result.
const { _electron } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const [bin, appDir] = process.argv.slice(2);
if (!bin) { console.error('usage: node memory_scenarios.js <binary> [app dir]'); process.exit(2); }
const SETTLE_MS = Number(process.env.SETTLE_MS || 45000); // time in each state before sampling
const measure = (pid) => JSON.parse(execFileSync('python3', [path.join(__dirname, 'measure_memory.py'), '--pid', String(pid), '--json', '-']).toString());

(async () => {
  const app = await _electron.launch({ executablePath: bin, args: [...(appDir ? [appDir] : []), '--no-sandbox'] });
  const pid = app.process().pid;
  const page = await app.firstWindow();
  await page.waitForSelector('[data-a=bldgo]');
  // the "free software from other companies" note at start is not part of any state; close it if it shows
  await page.getByText('Not now').click({ timeout: 5000 }).catch(() => {});
  const out = [];
  const run = async (name, start, stop) => {
    if (start) await page.click(start);
    await page.waitForTimeout(SETTLE_MS);
    const s = measure(pid);
    s.state = name;
    out.push(s);
    console.log(`${name.padEnd(40)} ${s.processes} processes  PSS ${s.pss_mib} MiB  USS ${s.uss_mib} MiB  RSS ${s.rss_mib} MiB`);
    if (stop) await page.click(stop);
    await page.waitForTimeout(3000);
  };
  await run('Idle, default project');
  await run('LED build animation running', '[data-a=bldgo]', '[data-a=bldgo]');
  await run('DVD screensaver running', '[data-a=dvdgo]', '[data-a=dvdgo]');
  await run('Idle again after both', null, null);
  // a bigger show: four 20 x 10 walls (800 tiles) on a 4K canvas with data and power wiring shown
  await page.evaluate(() => {
    S.cw = 3840; S.ch = 2160; S.cols = 20; S.rows = 10; S.ox = 0; S.oy = 0; storeWall();
    for (let i = 1; i < 4; i++) { addWall(false); S.cols = 20; S.rows = 10; S.ox = (i % 2) * 1920; S.oy = Math.floor(i / 2) * 1080; storeWall(); }
    S.proc = 'NovaStar VX1000 Pro'; applySpec(); S.showData = true; distAct('dadd'); S.showPow = true; storeWall(); sync(); fit();
  });
  await run('Big show, idle (4 walls, 800 tiles, 4K)', null, null);
  await run('Big show, LED build running', '[data-a=bldgo]', '[data-a=bldgo]');
  const version = await page.evaluate(() => (document.querySelector('.ver') || document.title || {}).textContent || document.title);
  fs.writeFileSync(path.join(__dirname, 'memory-results.json'), JSON.stringify({ bin, version, settle_ms: SETTLE_MS, samples: out }, null, 1));
  await app.close();
})().catch((e) => { console.error(e); process.exit(1); });
