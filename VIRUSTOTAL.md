# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-22 05:15 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/88c67590272399edeb305bb57ece4a0ddb85dca8e28582df662548a7ade2b760) | `88c67590272399edeb305bb57ece4a0ddb85dca8e28582df662548a7ade2b760` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/67e163c602d1c221f3970fdbadc58fc1cb78d1b197d28cd4e9c9692de697e19a) | `67e163c602d1c221f3970fdbadc58fc1cb78d1b197d28cd4e9c9692de697e19a` |
| TileSmith-linux-x64.deb | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/9616865e46ca819924726eb931f05ea5ec14fcb2b26572a3ee542b5da1e09b53) | `9616865e46ca819924726eb931f05ea5ec14fcb2b26572a3ee542b5da1e09b53` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/781d4c6fe15fca24f9a490ea6da79093995aeda6e4bd176936ff1753374fae7d) | `781d4c6fe15fca24f9a490ea6da79093995aeda6e4bd176936ff1753374fae7d` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/7970ae692b89be1a2b41a89a45b70b0e699f963083f60a4ec8ece3f469e454a5) | `7970ae692b89be1a2b41a89a45b70b0e699f963083f60a4ec8ece3f469e454a5` |
| TileSmith-linux-x64.rpm | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/e462958fc08a1f7a7f5bd737e89a421031b854f4c1a7a7d11bf9542d938a78a1) | `e462958fc08a1f7a7f5bd737e89a421031b854f4c1a7a7d11bf9542d938a78a1` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/96a48acf8c76cbc2a6e02efe3a3f8524d300468782901d678ebaf365906e4abf) | `96a48acf8c76cbc2a6e02efe3a3f8524d300468782901d678ebaf365906e4abf` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/560a6a6a35164c290fffe2979c2b0033954d14cf6c91a06bd1ecf2129725890a) | `560a6a6a35164c290fffe2979c2b0033954d14cf6c91a06bd1ecf2129725890a` |
| TileSmith-windows-portable.exe | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/4a3c928aebf5492650a273c89625a1c87dece7ca66b856004454ca9c6f1eb43b) | `4a3c928aebf5492650a273c89625a1c87dece7ca66b856004454ca9c6f1eb43b` |
