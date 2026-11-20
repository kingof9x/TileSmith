# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.10

Scanned 2026-11-20 02:37 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/eda6309ba160a9d96d126eb939bb0409ec56f721e48931c85f1402c59106c686) | `eda6309ba160a9d96d126eb939bb0409ec56f721e48931c85f1402c59106c686` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/9c3edfe9766d25f299c94fb91ce0ef5f9f06650c2ad39ea13bb35997114fc777) | `9c3edfe9766d25f299c94fb91ce0ef5f9f06650c2ad39ea13bb35997114fc777` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/ae61df8095e35c86414584ff0b80735b1964c112f38dc460e5708a19b97633dd) | `ae61df8095e35c86414584ff0b80735b1964c112f38dc460e5708a19b97633dd` |
| TileSmith-linux-x64.flatpak | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/40c3f5f7c48653a07e3501e56301e712cb4c3c80f5d398569ebf3cc67cbef11e) | `40c3f5f7c48653a07e3501e56301e712cb4c3c80f5d398569ebf3cc67cbef11e` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/0928b4694fb83ede561bb6a8a84adeb009e84a5f3a8a6bef22a9737b81825304) | `0928b4694fb83ede561bb6a8a84adeb009e84a5f3a8a6bef22a9737b81825304` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/6d1be703deaa33d428851f6c6074b7c457dca08fb980e57f30cd659eb5ae37e3) | `6d1be703deaa33d428851f6c6074b7c457dca08fb980e57f30cd659eb5ae37e3` |
| TileSmith-linux-x64.snap | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/a0c9e071ef3f30adf3cf940a161e9640c170b14c7c398e9c3647d912a0c70c93) | `a0c9e071ef3f30adf3cf940a161e9640c170b14c7c398e9c3647d912a0c70c93` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/c9a6fd69b1f688ea05bd3906c92161cabeae4b6b1eecd257bc58fcbd2cb91f93) | `c9a6fd69b1f688ea05bd3906c92161cabeae4b6b1eecd257bc58fcbd2cb91f93` |
| TileSmith-mac-universal.pkg | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/e9403148f5471ddac5a497596e7430bf4737556d45a3372ed172f505efa0e9f3) | `e9403148f5471ddac5a497596e7430bf4737556d45a3372ed172f505efa0e9f3` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/40f3d6905f4f6e7ac222f078a5d6716d7d834e33cda8fe6aee7b0ff5c5e7202d) | `40f3d6905f4f6e7ac222f078a5d6716d7d834e33cda8fe6aee7b0ff5c5e7202d` |
| TileSmith-windows-setup.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/cbd9964a88e04b4752443eef42abdbdb13ac87431b70e2cc188f1831fbd13058) | `cbd9964a88e04b4752443eef42abdbdb13ac87431b70e2cc188f1831fbd13058` |

## v3.9

Scanned 2026-11-20 01:51 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/19811d02e8f5fdfb58ae40e5e2f55971920718949a6ba89a91632366da9a1738) | `19811d02e8f5fdfb58ae40e5e2f55971920718949a6ba89a91632366da9a1738` |
| TileSmith-linux-x64.AppImage | [0 / 56 engines flag it](https://www.virustotal.com/gui/file/b1648fdd2d20c7db93a08cf30b521f8c60b459856d27c1185e7a9c72f17006ce) | `b1648fdd2d20c7db93a08cf30b521f8c60b459856d27c1185e7a9c72f17006ce` |
| TileSmith-linux-x64.deb | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/4414158943f678b2e582da0c3e56cc8ca02fad43de31b590621588bc1180c911) | `4414158943f678b2e582da0c3e56cc8ca02fad43de31b590621588bc1180c911` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/b745047dcfd6aad3d7ecba2ebcd22cbd8350af76a2dec80dbc37a879be72eb0c) | `b745047dcfd6aad3d7ecba2ebcd22cbd8350af76a2dec80dbc37a879be72eb0c` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/06db7883e1e14c355d23149c1acf9ccafc8dd2675e0da5692f5ab21aa359e820) | `06db7883e1e14c355d23149c1acf9ccafc8dd2675e0da5692f5ab21aa359e820` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/090efe7cfb7b66f061cdba2df58223429391f4d475796614bbc1b7e468dc47f5) | `090efe7cfb7b66f061cdba2df58223429391f4d475796614bbc1b7e468dc47f5` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/2008992cd6e1a077c97c292207a66343da03cda203c38c0469fefe494812ef19) | `2008992cd6e1a077c97c292207a66343da03cda203c38c0469fefe494812ef19` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/caf856b1a7d571e303342b68a91143beecf8350c41849f6278dca3d86ddfcab4) | `caf856b1a7d571e303342b68a91143beecf8350c41849f6278dca3d86ddfcab4` |
| TileSmith-mac-universal.pkg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/7b872d416449d4c17792f30cd34d5d99aa9fb69cffbb789b97935bfd0dab68f5) | `7b872d416449d4c17792f30cd34d5d99aa9fb69cffbb789b97935bfd0dab68f5` |
| TileSmith-windows-portable.exe | [0 / 64 engines flag it](https://www.virustotal.com/gui/file/58870ace071419fff57e7cf6c8fb9f4659e574075feceacb6fc64f7d5b494828) | `58870ace071419fff57e7cf6c8fb9f4659e574075feceacb6fc64f7d5b494828` |
| TileSmith-windows-setup.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/58f8494d99bd5dfddf0ba7bf7e44743b39b31dcb485035af1bae627829faa861) | `58f8494d99bd5dfddf0ba7bf7e44743b39b31dcb485035af1bae627829faa861` |

## v3.8

Scanned 2026-11-19 09:25 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/de90073fae21842a8ba5cde8f6f02947035f90eb48714197c73496f460ca555d) | `de90073fae21842a8ba5cde8f6f02947035f90eb48714197c73496f460ca555d` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/73dc7f5b20f179dcbafd22dfb4e436915512dfbae5a2852b71003cff0c5224dc) | `73dc7f5b20f179dcbafd22dfb4e436915512dfbae5a2852b71003cff0c5224dc` |
| TileSmith-linux-x64.deb | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/b3ff3475c3d6f1db42bcf57564cc2823d9f902429b062fa5aa8b8838eff76a76) | `b3ff3475c3d6f1db42bcf57564cc2823d9f902429b062fa5aa8b8838eff76a76` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/31ed34437e0ea7c46db2892ae4f3bfd470e1db4c96c603efe0792bab60d945c1) | `31ed34437e0ea7c46db2892ae4f3bfd470e1db4c96c603efe0792bab60d945c1` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/3b958e6357903942d45263191950fd0070fef77f3e06829348043d5dfeb61dfb) | `3b958e6357903942d45263191950fd0070fef77f3e06829348043d5dfeb61dfb` |
| TileSmith-linux-x64.rpm | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/53fb000f96bb2b12109e959dea44685902fbea4151c2589b6616927e739cdf69) | `53fb000f96bb2b12109e959dea44685902fbea4151c2589b6616927e739cdf69` |
| TileSmith-linux-x64.snap | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/5829ba6640e9f99c36f7841422d8597e62b924d99882769aa102e84e05deefe7) | `5829ba6640e9f99c36f7841422d8597e62b924d99882769aa102e84e05deefe7` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/e0f60a57461a92ebd92c22b38e24999faacd2646f7d80af8aa7ddac546ed6f36) | `e0f60a57461a92ebd92c22b38e24999faacd2646f7d80af8aa7ddac546ed6f36` |
| TileSmith-mac-universal.pkg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/160314c0a49bd36fd503a474e8d05979eb16fe4013c26bedfb25af4c21804fe0) | `160314c0a49bd36fd503a474e8d05979eb16fe4013c26bedfb25af4c21804fe0` |
| TileSmith-windows-portable.exe | [0 / 64 engines flag it](https://www.virustotal.com/gui/file/eb803a7bd5ca8b4f8131dcda8319fa2ade713d87e37dda3cbabcae966ae2ecf5) | `eb803a7bd5ca8b4f8131dcda8319fa2ade713d87e37dda3cbabcae966ae2ecf5` |
| TileSmith-windows-setup.exe | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/facd63d5553c666543033db95d56c17217b5865116f9be27dcb08ff7190c65b6) | `facd63d5553c666543033db95d56c17217b5865116f9be27dcb08ff7190c65b6` |

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
