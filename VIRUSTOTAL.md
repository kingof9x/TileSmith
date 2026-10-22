# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-22 04:08 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/feaf9a22e094c98d295563b82ab2adbd406f3f28c2a3228604bf9df7e36bf66e) | `feaf9a22e094c98d295563b82ab2adbd406f3f28c2a3228604bf9df7e36bf66e` |
| TileSmith-linux-x64.AppImage | [0 / 52 engines flag it](https://www.virustotal.com/gui/file/72416d10a87b69141d94f3bbc9b60e454129a507f797e48e06a51b805fbb40b8) | `72416d10a87b69141d94f3bbc9b60e454129a507f797e48e06a51b805fbb40b8` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/08832155ff9f996deb671cebdc3962b2aab8d89cf49ab2b57f27f4eb26436c20) | `08832155ff9f996deb671cebdc3962b2aab8d89cf49ab2b57f27f4eb26436c20` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/c47867bc33485e269b295a8dec429238805395788dcf7a26c2ce6cb2014a97f0) | `c47867bc33485e269b295a8dec429238805395788dcf7a26c2ce6cb2014a97f0` |
| TileSmith-linux-x64.pacman | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/eda24c2a93596543764118a2ba57b6a1ffd21a0ab0357c60b7eb32340b44b674) | `eda24c2a93596543764118a2ba57b6a1ffd21a0ab0357c60b7eb32340b44b674` |
| TileSmith-linux-x64.rpm | [scan still running](https://www.virustotal.com/gui/file/676743c2ff07fb578e21c59af42f1207cc4415067bb85342a9ad0718828cab22) | `676743c2ff07fb578e21c59af42f1207cc4415067bb85342a9ad0718828cab22` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/0a7ce2b0d0b65f2274ec7bddc12cd1237aa60713477655b73f02d6cce37f2fd1) | `0a7ce2b0d0b65f2274ec7bddc12cd1237aa60713477655b73f02d6cce37f2fd1` |
| TileSmith-mac-universal.dmg | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/4875f4073f26cb023ee427f63f6666604f654a756879fe5d768ace018b257a8f) | `4875f4073f26cb023ee427f63f6666604f654a756879fe5d768ace018b257a8f` |
| TileSmith-windows-portable.exe | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/eb2b96608bb8467df2dfb73ecb19ada021ab95de58fcb64032546802c0f5727b) | `eb2b96608bb8467df2dfb73ecb19ada021ab95de58fcb64032546802c0f5727b` |
