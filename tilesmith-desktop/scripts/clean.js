// Cross-platform cleanup (works in Command Prompt, PowerShell, Terminal): npm run clean
// Also removes package-lock.json so the next npm install resolves fresh, patched versions instead of old pinned ones.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const targets = ['node_modules', 'dist', 'package-lock.json', 'TileSmith-Portable.exe'];
for (const f of fs.readdirSync(root)) if (/^TileSmith-.*\.dmg$/.test(f)) targets.push(f);
for (const t of targets) {
  const p = path.join(root, t);
  if (fs.existsSync(p)) { fs.rmSync(p, { recursive: true, force: true }); console.log('removed ' + t); }
}
console.log('clean done');
