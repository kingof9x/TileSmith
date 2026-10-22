# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-22 04:35 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/74beb35c7347b954ba5b4db13a09cd807d29138357ef8031694fca7141e5eea3) | `74beb35c7347b954ba5b4db13a09cd807d29138357ef8031694fca7141e5eea3` |
| TileSmith-linux-x64.AppImage | [1 / 62 engines flag it](https://www.virustotal.com/gui/file/0baf83a6e575c1006a31da6728a65703d423e2f3daee93bef40566cf7f569c40) | `0baf83a6e575c1006a31da6728a65703d423e2f3daee93bef40566cf7f569c40` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/dde1a72e3ed7c9da050d193e49b5be453716136ae4c12b8d86a82837a0e2e9ce) | `dde1a72e3ed7c9da050d193e49b5be453716136ae4c12b8d86a82837a0e2e9ce` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/a077de64c270e1983255735a24965af8946ca8e1da1dfdf38f93d526e36efac8) | `a077de64c270e1983255735a24965af8946ca8e1da1dfdf38f93d526e36efac8` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/12f66fbdcf0a872204f7a756b842deff42f58fbf87cb4b589325aa15170bd42b) | `12f66fbdcf0a872204f7a756b842deff42f58fbf87cb4b589325aa15170bd42b` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/3799c071bb7e4ddc23349c4863ebe067d3382171d1ac0c90c26348b46426016d) | `3799c071bb7e4ddc23349c4863ebe067d3382171d1ac0c90c26348b46426016d` |
| TileSmith-linux-x64.snap | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/89be5ae193063af862787a99b44ccfe0de291c9a3bb58755bd0a789ec753233c) | `89be5ae193063af862787a99b44ccfe0de291c9a3bb58755bd0a789ec753233c` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/41171d0a4b587d08bbe3aecd2b3939805f61a2907c49c3fd5917dc7c13faff61) | `41171d0a4b587d08bbe3aecd2b3939805f61a2907c49c3fd5917dc7c13faff61` |
| TileSmith-windows-portable.exe | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/d0a4b9c9dbae0a75373ea44376f87e425cfdb0608aa7f14c2787ab9598aac34e) | `d0a4b9c9dbae0a75373ea44376f87e425cfdb0608aa7f14c2787ab9598aac34e` |
