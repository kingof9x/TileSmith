# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.8

Scanned 2026-11-18 19:18 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/ecaddfddb7923779986b9b423b66c00fd866f3ab8667a54acca268c6a2444633) | `ecaddfddb7923779986b9b423b66c00fd866f3ab8667a54acca268c6a2444633` |
| TileSmith-linux-x64.AppImage | [0 / 43 engines flag it](https://www.virustotal.com/gui/file/e4e7f6d953a768088107fafea42115bc5d6d75dec0a2929018bded0bb58e528d) | `e4e7f6d953a768088107fafea42115bc5d6d75dec0a2929018bded0bb58e528d` |
| TileSmith-linux-x64.deb | [0 / 48 engines flag it](https://www.virustotal.com/gui/file/1a1b8834b95e4f7ccbd0ca15efab812456b2bb6e1f8fe11b21254988c23e526b) | `1a1b8834b95e4f7ccbd0ca15efab812456b2bb6e1f8fe11b21254988c23e526b` |
| TileSmith-linux-x64.flatpak | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/47efb8cd527d172c60c8ddbc5923337cdb4de11bdf4973940a8273f804574f47) | `47efb8cd527d172c60c8ddbc5923337cdb4de11bdf4973940a8273f804574f47` |
| TileSmith-linux-x64.pacman | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/e81c97c5f28d937c075f487f1660521db58b65e054ff722d8ac93fcfbb9a59b2) | `e81c97c5f28d937c075f487f1660521db58b65e054ff722d8ac93fcfbb9a59b2` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/b04e1c1f71030a2f50aa4be9cd4467cbcbd54124aa19cf4bc1b89e5cd0852bbe) | `b04e1c1f71030a2f50aa4be9cd4467cbcbd54124aa19cf4bc1b89e5cd0852bbe` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/2b7b303eb8be406c62bbffed1b44a74a57ad5a3538b24491eb45c61552378279) | `2b7b303eb8be406c62bbffed1b44a74a57ad5a3538b24491eb45c61552378279` |
| TileSmith-mac-universal.dmg | [0 / 56 engines flag it](https://www.virustotal.com/gui/file/73257c3861d68eea51694d27fd450a87fa2a0e16b6303520e8be5af9db1a737b) | `73257c3861d68eea51694d27fd450a87fa2a0e16b6303520e8be5af9db1a737b` |
| TileSmith-mac-universal.pkg | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/1b376a13cd8c3d20ed88016646df9cbe4a83eddbd1a2860a0ecb0a00b7f332dc) | `1b376a13cd8c3d20ed88016646df9cbe4a83eddbd1a2860a0ecb0a00b7f332dc` |
| TileSmith-windows-portable.exe | [0 / 64 engines flag it](https://www.virustotal.com/gui/file/39c5ee72fc99937bc1dca19d826f1b0269cebe9c10cf576b86fd0b2327bff67d) | `39c5ee72fc99937bc1dca19d826f1b0269cebe9c10cf576b86fd0b2327bff67d` |
| TileSmith-windows-setup.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/5fcc3d96a4fa5e08ff31c18ef97ef15f8dac100221213c87430b16b8bc3301bf) | `5fcc3d96a4fa5e08ff31c18ef97ef15f8dac100221213c87430b16b8bc3301bf` |

## v3.7

Scanned 2026-11-18 17:48 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/39914fec8e9c2f4dd33fb1680c3113bd75e600d95f276eead40d6cf6c6f2c74b) | `39914fec8e9c2f4dd33fb1680c3113bd75e600d95f276eead40d6cf6c6f2c74b` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/0aee44118a6e5f27e4ca3fb4303fe3252aff0ddf028568a96285f11d8cadea7c) | `0aee44118a6e5f27e4ca3fb4303fe3252aff0ddf028568a96285f11d8cadea7c` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/cf5cc59d9b863b627b38a7cf88b6556d3f3abe6f308c12accc3c28458f65ada6) | `cf5cc59d9b863b627b38a7cf88b6556d3f3abe6f308c12accc3c28458f65ada6` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/50580a0c1976793210aa4bd2391aa582cd56fac66490b94650f039146714b7f6) | `50580a0c1976793210aa4bd2391aa582cd56fac66490b94650f039146714b7f6` |
| TileSmith-linux-x64.pacman | [0 / 53 engines flag it](https://www.virustotal.com/gui/file/9cdd9bd339e758a260788bb962d53bc3e445010699fddcd877ff11280b39d4f2) | `9cdd9bd339e758a260788bb962d53bc3e445010699fddcd877ff11280b39d4f2` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/8796d2af240903daafabb51e3f50ed18d793078d530354f6a25c6a949a55568f) | `8796d2af240903daafabb51e3f50ed18d793078d530354f6a25c6a949a55568f` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/3eba3062b149de2915c82a74c0483945acc69949ffe126930559f587565197cb) | `3eba3062b149de2915c82a74c0483945acc69949ffe126930559f587565197cb` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/d77c3f8ca908c3ebfbd5444f1fbf5d7178249be71845f5b7e410f2dbb41fba76) | `d77c3f8ca908c3ebfbd5444f1fbf5d7178249be71845f5b7e410f2dbb41fba76` |
| TileSmith-mac-universal.pkg | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/0a71c0c07b93c582dd76e3aea3dcc3b64d1afd07e61b03e263f674b07b8c6dd2) | `0a71c0c07b93c582dd76e3aea3dcc3b64d1afd07e61b03e263f674b07b8c6dd2` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/6a7ea39d40a3b92fe578cfb85a2719f4c7bb5eb696ca4605c1baf6b34cb74814) | `6a7ea39d40a3b92fe578cfb85a2719f4c7bb5eb696ca4605c1baf6b34cb74814` |
| TileSmith-windows-setup.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/4469d78ad94c169e2042678834cdfb5267170ad3aa44ecfd7612bde1eaec3158) | `4469d78ad94c169e2042678834cdfb5267170ad3aa44ecfd7612bde1eaec3158` |

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
