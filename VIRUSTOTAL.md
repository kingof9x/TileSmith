# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-20 21:58 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/19d376f40ed8e06c07f8540329a7d974251476dfe507ee7b54de1712c34910c0) | `19d376f40ed8e06c07f8540329a7d974251476dfe507ee7b54de1712c34910c0` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/694bab2abddde7daad63f3716790c16c7b3d20cf24ad6797aba16e898fedf918) | `694bab2abddde7daad63f3716790c16c7b3d20cf24ad6797aba16e898fedf918` |
| TileSmith-linux-x64.deb | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/696bc127be18d9083e8d338527efe0ae370920e4dbdcd6f66a6c5005f4e2f75c) | `696bc127be18d9083e8d338527efe0ae370920e4dbdcd6f66a6c5005f4e2f75c` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/ca68a76d90d435fd234e3d28bd919ffd6da51be69e57cbd2459c3a337e430ba2) | `ca68a76d90d435fd234e3d28bd919ffd6da51be69e57cbd2459c3a337e430ba2` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/05f162a8f9830c49da94a2979ecd6b8498febd130c065e3480e20b8c212e7ee7) | `05f162a8f9830c49da94a2979ecd6b8498febd130c065e3480e20b8c212e7ee7` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/06feea925eff73a9f5e7105a90d26a705fee5f188dbf3d54be2774d4dc6fc3ba) | `06feea925eff73a9f5e7105a90d26a705fee5f188dbf3d54be2774d4dc6fc3ba` |
| TileSmith-linux-x64.snap | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/f1816ed1bfac35a6ef08ef5753c547916fdfa2cfd4b9cffdac81b6572f755aee) | `f1816ed1bfac35a6ef08ef5753c547916fdfa2cfd4b9cffdac81b6572f755aee` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/fb1b82d2ce8a3b029bf204645e491fff11f3d3e6289343debd27ba635f34cf10) | `fb1b82d2ce8a3b029bf204645e491fff11f3d3e6289343debd27ba635f34cf10` |
| TileSmith-windows-portable.exe | [0 / 64 engines flag it](https://www.virustotal.com/gui/file/9b8ec98b2796e7c61a5d8874d3fbb889e66754b617b81618ff195af5d118493b) | `9b8ec98b2796e7c61a5d8874d3fbb889e66754b617b81618ff195af5d118493b` |
