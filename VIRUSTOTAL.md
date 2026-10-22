# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-22 16:15 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/bcdc94916437de90ce07dcde0d65794abcea2c72a0268bcf70be1f15ae1e4010) | `bcdc94916437de90ce07dcde0d65794abcea2c72a0268bcf70be1f15ae1e4010` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/1b3725e3afae3561f4ecbb6d7b5d21e249ad6974d998cb71a453fc2d8f065910) | `1b3725e3afae3561f4ecbb6d7b5d21e249ad6974d998cb71a453fc2d8f065910` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/6e89449323c1fa0512a3846ab1b59e0c28f3ac831ccfa4277c44b2fdd4adf9a2) | `6e89449323c1fa0512a3846ab1b59e0c28f3ac831ccfa4277c44b2fdd4adf9a2` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/241c4e5f410885c49b44354f7941eba7739c5711f7711c0d7822d69d998f0e2a) | `241c4e5f410885c49b44354f7941eba7739c5711f7711c0d7822d69d998f0e2a` |
| TileSmith-linux-x64.pacman | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/1692d9de0c23947a1df3df67015b4b75f42bec937052c4570d13bb101e76af4a) | `1692d9de0c23947a1df3df67015b4b75f42bec937052c4570d13bb101e76af4a` |
| TileSmith-linux-x64.rpm | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/a717a7c76b511deab35fb68060ea2284a1dcc29f27936daf0749578c3b3fbc56) | `a717a7c76b511deab35fb68060ea2284a1dcc29f27936daf0749578c3b3fbc56` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/c03740afb7718d8205a1615b98edc0c577054399a54a4f31a7431590f052d1f6) | `c03740afb7718d8205a1615b98edc0c577054399a54a4f31a7431590f052d1f6` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/ec4072d6633ae63036cc5f96a1ac404848d37955258de0696fc391a4f1fad0e5) | `ec4072d6633ae63036cc5f96a1ac404848d37955258de0696fc391a4f1fad0e5` |
| TileSmith-windows-portable.exe | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/6f91f503da4714273b8a2b4d85f764e94123974fa3601be537c5683e4b92d42d) | `6f91f503da4714273b8a2b4d85f764e94123974fa3601be537c5683e4b92d42d` |
