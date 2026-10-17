// Runs before a build: reports whether a HAP-capable ffmpeg is available for this platform.
const fs = require('fs'), path = require('path'), cp = require('child_process');
const mac = process.platform === 'darwin';
const check = f => { try { return /^\s*V\S*\s+hap\s/m.test(cp.spawnSync(f, ['-hide_banner', '-encoders'], { encoding: 'utf8' }).stdout || ''); } catch (e) { return false; } };
const root = path.join(__dirname, '..');
if (mac) {
  const list = [path.join(root, 'bin', 'mac', 'ffmpeg'), '/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/opt/local/bin/ffmpeg'].filter(f => fs.existsSync(f));
  const ok = list.find(check);
  if (ok) console.log('[ok] HAP-capable ffmpeg found: ' + ok + (ok.includes('bin/mac') ? ' (will be bundled in the app)' : ' (the app will use it from this location at run time)'));
  else console.log('[WARN] No ffmpeg with the HAP encoder found on this Mac.\n  Video export will not work until you install one. See BUILD-MAC.txt step 5. The build itself will still succeed.');
} else {
  const mine = path.join(root, 'bin', 'ffmpeg.exe');
  if (fs.existsSync(mine)) console.log(check(mine) ? '[ok] bin/ffmpeg.exe has the HAP encoder and will be bundled.' : '[WARN] bin/ffmpeg.exe has NO HAP encoder. Use the gyan.dev "full" build.');
  else console.log('[WARN] No ffmpeg.exe in the bin folder.\n  Download the "full" build from https://www.gyan.dev/ffmpeg/builds/ , copy ffmpeg.exe into the bin folder, then run npm run dist again.');
}
