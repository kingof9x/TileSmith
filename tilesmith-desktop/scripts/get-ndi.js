// Runs before a build. Puts the NDI® runtime library and its license notices into bin/ndi (Windows) or
// bin/mac/ndi (Mac) so electron-builder packs them inside TileSmith, and nobody who runs the app has to
// install NDI® Tools or the NDI® Runtime. The files come from the free NDI® SDK installed on this computer
// (https://ndi.video/for-developers/ndi-sdk/). You can also copy them into that folder yourself.
// NDI® is a registered trademark of Vizrt NDI AB.
const fs = require('fs'), path = require('path'), os = require('os');
const mac = process.platform === 'darwin';
const root = path.join(__dirname, '..');
const dest = mac ? path.join(root, 'bin', 'mac', 'ndi') : path.join(root, 'bin', 'ndi');
const LIB = mac ? 'libndi.dylib' : 'Processing.NDI.Lib.x64.dll';
const isNotice = n => /licen[cs]e/i.test(n) && /\.(txt|rtf|md|pdf)$/i.test(n);
const rel = p => path.relative(root, p);
fs.mkdirSync(dest, { recursive: true });

function walk(dir, depth, test, hits) {
  if (depth < 0) return hits;
  let ents; try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { return hits; }
  for (const e of ents) { const p = path.join(dir, e.name); if (e.isDirectory()) walk(p, depth - 1, test, hits); else if (test(e.name, p)) hits.push(p); }
  return hits;
}

let from = null;
if (!fs.existsSync(path.join(dest, LIB))) {
  const roots = (mac
    ? ['/Library/NDI SDK for Apple', path.join(os.homedir(), 'Library', 'NDI SDK for Apple'), '/Library/NDI Advanced SDK for Apple']
    : [process.env.NDI_SDK_DIR, process.env.ProgramFiles && path.join(process.env.ProgramFiles, 'NDI'), process.env.ProgramW6432 && path.join(process.env.ProgramW6432, 'NDI'), 'C:\\Program Files\\NDI']
  ).filter(r => r && fs.existsSync(r));
  const hits = [];
  for (const r of roots) walk(r, 6, n => n === LIB, hits);
  // prefer the SDK's own copy for this platform (x64 on Windows, macOS on Mac)
  const score = p => (/sdk/i.test(p) ? 4 : 0) + (mac ? (/macos/i.test(p) ? 2 : 0) : (/x64/i.test(p) ? 2 : 0)) + (/[\\/](bin|lib)[\\/]/i.test(p) ? 1 : 0);
  hits.sort((a, b) => score(b) - score(a));
  from = hits[0] || null;
  if (from) {
    fs.copyFileSync(from, path.join(dest, LIB));
    // license notices: next to the library first, otherwise anywhere in that SDK
    let notes = fs.readdirSync(path.dirname(from)).filter(isNotice).map(n => path.join(path.dirname(from), n));
    if (!notes.length) { const sdkRoot = roots.find(r => from.startsWith(r)) || path.dirname(from); notes = walk(sdkRoot, 6, isNotice, []); }
    for (const n of notes) fs.copyFileSync(n, path.join(dest, path.basename(n)));
  }
}

const notices = fs.readdirSync(dest).filter(isNotice);
if (fs.existsSync(path.join(dest, LIB))) {
  console.log(`[ok] The NDI® runtime will be built into TileSmith: ${rel(path.join(dest, LIB))}` + (from ? `\n     (copied from ${from})` : ''));
  if (notices.length) console.log('     NDI® license notices included: ' + notices.join(', '));
  else console.log(`[WARN] No NDI® license notices file found. NDI® requires its license notices to ship with the runtime.\n  Copy the license .txt that sits next to ${LIB} in the NDI® SDK (on Windows: Processing.NDI.Lib.Licenses.txt)\n  into ${rel(dest)} and run the build again.`);
} else {
  console.log(`[WARN] NDI® SDK not found, so the NDI® runtime will NOT be built into TileSmith.\n  Install the free NDI® SDK from https://ndi.video/for-developers/ndi-sdk/ and run the build again,\n  or copy ${LIB} and its license notices .txt into ${rel(dest)}.\n  Without it, every computer that runs TileSmith needs the NDI® Runtime or NDI® Tools for NDI® output.\n  The build itself still succeeds.`);
}
