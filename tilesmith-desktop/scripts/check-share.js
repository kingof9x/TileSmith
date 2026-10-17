// Runs before a build. Checks the files that give TileSmith Spout output (Windows) or Syphon output (Mac).
// They ship in the project zip, so nothing has to be downloaded:
//   Windows: bin/spout/SpoutDX.dll (+ Spout-licence.txt)
//   Mac:     bin/mac/syphon/bin/syphon.node and bin/mac/syphon/Frameworks/Syphon.framework (+ licence files)
// If they are missing the build still succeeds; that platform's Start Spout / Start Syphon button is then hidden.
// On a Mac it also repairs the framework's internal symlinks (some unzip tools turn them into plain files)
// and clears the download quarantine flag, so macOS loads the framework without a security prompt.
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const root = path.join(__dirname, '..');
const rel = p => path.relative(root, p);
const mac = process.platform === 'darwin';
const isNotice = n => /licen[cs]e/i.test(n) && /\.(txt|rtf|md)$/i.test(n);

function checkSpout() {
  const dir = path.join(root, 'bin', 'spout'), dll = path.join(dir, 'SpoutDX.dll');
  if (!fs.existsSync(dll)) {
    console.log(`[info] ${rel(dll)} not found, so Spout output will NOT be built into TileSmith (the Start Spout button is hidden).\n  To include it, unzip a fresh copy of tilesmith-desktop.zip; bin/spout comes with it.`);
    return;
  }
  const b = fs.readFileSync(dll);
  const has = s => b.includes(Buffer.from(s, 'latin1'));
  const pe = b.readUInt16LE(0) === 0x5a4d && b.readUInt16LE(b.readUInt32LE(0x3c) + 4) === 0x8664;
  const missing = ['??0spoutDX@@QEAA@XZ', '?SetSenderName@spoutDX@@QEAA_NPEBD@Z', '?SetSenderFormat@spoutDX@@QEAAXW4DXGI_FORMAT@@@Z',
    '?SendImage@spoutDX@@QEAA_NPEBEIII@Z', '?ReleaseSender@spoutDX@@QEAAXXZ', '?GetName@spoutDX@@QEAAPEBDXZ',
    // graphics card choice and DirectX 11 device
    '?OpenDirectX11@spoutDX@@QEAA_NPEAUID3D11Device@@@Z', '?CloseDirectX11@spoutDX@@QEAAXXZ', '?GetDX11Device@spoutDX@@QEAAPEAUID3D11Device@@XZ',
    '?GetNumAdapters@spoutDX@@QEAAHXZ', '?GetAdapterName@spoutDX@@QEAA_NHPEADH@Z', '?GetAdapter@spoutDX@@QEAAHXZ', '?SetAdapter@spoutDX@@QEAA_NH@Z',
    '?SetPreferredAdapter@spoutDX@@QEAA_NH@Z', '?EnableSpoutLogFile@spoutDX@@QEAAXPEBD_N@Z'].filter(s => !has(s));
  if (!pe || missing.length) {
    console.log(`[STOP] ${rel(dll)} is not the SpoutDX.dll TileSmith expects (64-bit Spout SDK 2.007.017, MT build).` +
      (missing.length ? `\n  Missing functions: ${missing.join(', ')}` : '') +
      `\n  Unzip a fresh copy of tilesmith-desktop.zip, or delete bin/spout/SpoutDX.dll to build without Spout.`);
    process.exit(1);
  }
  if (/vcruntime140/i.test(b.toString('latin1'))) console.log(`[WARN] ${rel(dll)} is an "MD" build that needs the Visual C++ runtime on every PC.\n  Use the MT build from the zip (Libs_2-007-017/MT/bin/SpoutDX.dll) so TileSmith runs anywhere.`);
  const notes = fs.readdirSync(dir).filter(isNotice);
  console.log(`[ok] Spout output will be built into TileSmith: ${rel(dll)}` + (notes.length ? `\n     Spout licence included: ${notes.join(', ')}` : ''));
  if (!notes.length) console.log(`[WARN] No Spout licence file in ${rel(dir)}. Spout's licence must ship with the DLL; unzip a fresh copy of the project.`);
}

// Recreate a framework symlink if it is missing or was turned into a plain file or folder.
function link(p, target) {
  let st = null; try { st = fs.lstatSync(p); } catch (e) {}
  if (st && st.isSymbolicLink() && fs.readlinkSync(p) === target) return false;
  if (st) fs.rmSync(p, { recursive: true, force: true });
  fs.symlinkSync(target, p);
  return true;
}

function checkSyphon() {
  const dir = path.join(root, 'bin', 'mac', 'syphon'), node = path.join(dir, 'bin', 'syphon.node');
  const fw = path.join(dir, 'Frameworks', 'Syphon.framework'), bin = path.join(fw, 'Versions', 'A', 'Syphon');
  if (!fs.existsSync(node) || !fs.existsSync(bin)) {
    console.log(`[info] ${rel(dir)} is missing or incomplete, so Syphon output will NOT be built into TileSmith (the Start Syphon button is hidden).\n  To include it, unzip a fresh copy of tilesmith-desktop.zip; bin/mac/syphon comes with it.`);
    return;
  }
  let fixed = 0;
  fixed += link(path.join(fw, 'Versions', 'Current'), 'A');
  for (const n of ['Syphon', 'Resources', 'Headers', 'Modules'])
    if (fs.existsSync(path.join(fw, 'Versions', 'A', n))) fixed += link(path.join(fw, n), path.join('Versions', 'Current', n));
  if (fixed) console.log(`     repaired ${fixed} symlink(s) inside Syphon.framework`);
  try { execFileSync('xattr', ['-cr', dir], { stdio: 'ignore' }); } catch (e) {}
  try { fs.chmodSync(bin, 0o755); } catch (e) {}
  const notes = fs.readdirSync(dir).filter(isNotice);
  console.log(`[ok] Syphon output will be built into TileSmith: ${rel(node)} and ${rel(fw)}` + (notes.length ? `\n     Syphon licences included: ${notes.join(', ')}` : ''));
  if (!notes.length) console.log(`[WARN] No Syphon licence files in ${rel(dir)}. They must ship with the framework; unzip a fresh copy of the project.`);
}

if (mac) checkSyphon(); else checkSpout();
