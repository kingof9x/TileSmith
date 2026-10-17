// Removes everything the mobile build downloads or generates, so the next "npm install" starts fresh.
// The Android and iOS projects themselves (android/, ios/) are kept.
const fs = require('fs'), path = require('path'), root = path.join(__dirname, '..');
for (const p of ['node_modules', 'package-lock.json', 'www', 'android/app/build', 'android/build', 'android/.gradle',
  'android/app/src/main/assets/public', 'ios/App/App/public', 'ios/DerivedData'])
  fs.rmSync(path.join(root, p), { recursive: true, force: true });
console.log('clean done');
