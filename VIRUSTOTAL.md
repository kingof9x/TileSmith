# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-19 05:03 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/708957efc5c04c131bf117b8bfbe9ac7027b330dc20f8f074e1369724efaf3cb) | `708957efc5c04c131bf117b8bfbe9ac7027b330dc20f8f074e1369724efaf3cb` |
| TileSmith-linux-x64.AppImage | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/1b3241d6900dc37b2460c34f0b248f681df6931b75d8e745e6d091d3506fb121) | `1b3241d6900dc37b2460c34f0b248f681df6931b75d8e745e6d091d3506fb121` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/8a3be25aa1134ec20dcdc61af7119d8b7b1c78d4616b512e982cde46c7700e9e) | `8a3be25aa1134ec20dcdc61af7119d8b7b1c78d4616b512e982cde46c7700e9e` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/78884b71e7ea811526ac960ad6ae858d9df0de2c7f95e46957fb7ca244264337) | `78884b71e7ea811526ac960ad6ae858d9df0de2c7f95e46957fb7ca244264337` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/673e3a229f369d16aafdceb049f86d4c854d20f9fe0e8517a9a970172ef56ea8) | `673e3a229f369d16aafdceb049f86d4c854d20f9fe0e8517a9a970172ef56ea8` |
| TileSmith-linux-x64.rpm | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/c98f7b10da4d6c5af5b58a79411339d6af315bcc8c502ec7fa79b31cbc4988fb) | `c98f7b10da4d6c5af5b58a79411339d6af315bcc8c502ec7fa79b31cbc4988fb` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/7e507782649d2be3147bc019acc23ec2eefb31892ee663ea04198f8e817a5556) | `7e507782649d2be3147bc019acc23ec2eefb31892ee663ea04198f8e817a5556` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/5ee99afdda940eb76841c241fac04804850aaa605453cc5b226d049fdcaebbab) | `5ee99afdda940eb76841c241fac04804850aaa605453cc5b226d049fdcaebbab` |
| TileSmith-windows-portable.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/1e3130b5b80be60417f1821efaa29b483d2041270a2b88210a871b88cb64fc19) | `1e3130b5b80be60417f1821efaa29b483d2041270a2b88210a871b88cb64fc19` |
