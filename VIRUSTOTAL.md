# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.7

Scanned 2026-11-16 03:37 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/156adcd44adb7d1e221c326d2d97b80f87808b8113c9160d313afb4a64a04133) | `156adcd44adb7d1e221c326d2d97b80f87808b8113c9160d313afb4a64a04133` |
| TileSmith-linux-x64.AppImage | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/579f0940b546fab7a9a695b082719bbe07e649044dfee2e87f5670283d031d91) | `579f0940b546fab7a9a695b082719bbe07e649044dfee2e87f5670283d031d91` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/d104d6b419508a0dd1efbf327dd97161d337530cf0b5c200e2271f7d900225a3) | `d104d6b419508a0dd1efbf327dd97161d337530cf0b5c200e2271f7d900225a3` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/34a758969499ce1823d276c2d98f10dedc70ed01aa2486c3f5e1459654e3444c) | `34a758969499ce1823d276c2d98f10dedc70ed01aa2486c3f5e1459654e3444c` |
| TileSmith-linux-x64.pacman | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/6ca7aaa15522cf70c683035a348671937c7aa0f72647819afc51988121205d63) | `6ca7aaa15522cf70c683035a348671937c7aa0f72647819afc51988121205d63` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/b28632aef8cd6daaae6e59472ab656e9594910973c29118874516e35e8a4c8cd) | `b28632aef8cd6daaae6e59472ab656e9594910973c29118874516e35e8a4c8cd` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/96a0f49421add006a5deb024fd036feec921cf246dd8f03cc0e0df98675c434e) | `96a0f49421add006a5deb024fd036feec921cf246dd8f03cc0e0df98675c434e` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/b5b1ed9db4f57a4d3b6815a39658cd79eb0323043b1760e86ef7682a734bbac8) | `b5b1ed9db4f57a4d3b6815a39658cd79eb0323043b1760e86ef7682a734bbac8` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/8ef8d63e462a50af30d53554b787ef6e12083292e6940beb90632bb531595b51) | `8ef8d63e462a50af30d53554b787ef6e12083292e6940beb90632bb531595b51` |

## v3.6

Scanned 2026-11-14 21:48 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/690be3790169adbac2f74f395d78961ba95c0a58367b472741b2288643141a69) | `690be3790169adbac2f74f395d78961ba95c0a58367b472741b2288643141a69` |
| TileSmith-linux-x64.AppImage | [1 / 63 engines flag it](https://www.virustotal.com/gui/file/b0885e4ac1ef679a3336c514d1557cae0175d4b833fa593822507f411485c24c) | `b0885e4ac1ef679a3336c514d1557cae0175d4b833fa593822507f411485c24c` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/244c6ca940eddfa22fe55b8c541a4c0681dc2b6913a02397ac735794a06b6d2f) | `244c6ca940eddfa22fe55b8c541a4c0681dc2b6913a02397ac735794a06b6d2f` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/4446d611389df29e2b662a80b8f5fb7de0518e56ba05c575e4a2bf8793fe4a88) | `4446d611389df29e2b662a80b8f5fb7de0518e56ba05c575e4a2bf8793fe4a88` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/5dd7250d432cae72e84ea729e77567cf21cc64832ee56c138881d7c9e8729c26) | `5dd7250d432cae72e84ea729e77567cf21cc64832ee56c138881d7c9e8729c26` |
| TileSmith-linux-x64.rpm | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/11d377e164795111789b067e5272cc1396729b32c999a1a3f23945f94e326c98) | `11d377e164795111789b067e5272cc1396729b32c999a1a3f23945f94e326c98` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/7f4485aa67ec00af8a6522b878beaee5abeda7d9c281ccc79612d1a293032cd5) | `7f4485aa67ec00af8a6522b878beaee5abeda7d9c281ccc79612d1a293032cd5` |
| TileSmith-mac-universal.dmg | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/eb4d2689138f76b4e53e945cdf898a5fcd7954b221db22515d4ff65d4a19ae12) | `eb4d2689138f76b4e53e945cdf898a5fcd7954b221db22515d4ff65d4a19ae12` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/f15aaa367e700a25831539d523120f7f2b4c74d017c3067c6d85718486ee30db) | `f15aaa367e700a25831539d523120f7f2b4c74d017c3067c6d85718486ee30db` |

## v3.5

Scanned 2026-10-28 04:12 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/60e0c51058535c9c2dfe34534186524f05675d1c54e65152c824d92dbbaaec4b) | `60e0c51058535c9c2dfe34534186524f05675d1c54e65152c824d92dbbaaec4b` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/aba9c3d3dba4199609bb561a7643f37298447964830fd0cfb3a9eff73119356c) | `aba9c3d3dba4199609bb561a7643f37298447964830fd0cfb3a9eff73119356c` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/f9dce55b44ebef36a948f96c9f2fb6b694f506e5c728e6c1c25193d1a9210181) | `f9dce55b44ebef36a948f96c9f2fb6b694f506e5c728e6c1c25193d1a9210181` |
| TileSmith-linux-x64.flatpak | [0 / 52 engines flag it](https://www.virustotal.com/gui/file/87edc37c4d66d47d1173e9f010039251be42c43f15606b5d649cb5653ecfd9f1) | `87edc37c4d66d47d1173e9f010039251be42c43f15606b5d649cb5653ecfd9f1` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/dd3ab3c9c8c3f51a289f961ec77951248dbbe938f797988f5fb60dcf57976da3) | `dd3ab3c9c8c3f51a289f961ec77951248dbbe938f797988f5fb60dcf57976da3` |
| TileSmith-linux-x64.rpm | [0 / 42 engines flag it](https://www.virustotal.com/gui/file/37bffa266cad8e058bedd956373c4e5dfa36fd5a12d19a5f870d0d2e8d76015c) | `37bffa266cad8e058bedd956373c4e5dfa36fd5a12d19a5f870d0d2e8d76015c` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/79bd75ba4f4d86e92c73df09935b94e55db06b06d361a50445c4e01d6b7ae556) | `79bd75ba4f4d86e92c73df09935b94e55db06b06d361a50445c4e01d6b7ae556` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/114b329be6c34be0f33a77eb3c62e9a9c9cbc7f79a6250500f6fbb85597ebe80) | `114b329be6c34be0f33a77eb3c62e9a9c9cbc7f79a6250500f6fbb85597ebe80` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/cc67568f0a75a20159140d4ffad645935482218b3dfe86ad121071d9ded7c4a6) | `cc67568f0a75a20159140d4ffad645935482218b3dfe86ad121071d9ded7c4a6` |
