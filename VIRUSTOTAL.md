# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-25 07:54 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/f152170e1dbbe45ac4ae1c2b872f71d121905d06dbd50ba9f30b7980d3e09c13) | `f152170e1dbbe45ac4ae1c2b872f71d121905d06dbd50ba9f30b7980d3e09c13` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/c311b7ace292afbb4550488f7a6ad86da16055194aa336684ddb0a98e127608b) | `c311b7ace292afbb4550488f7a6ad86da16055194aa336684ddb0a98e127608b` |
| TileSmith-linux-x64.deb | [0 / 56 engines flag it](https://www.virustotal.com/gui/file/1bbc5c592d9123cd7a1f0a05412b65e2bb2cd9064dd704e7d21f4db9802de06e) | `1bbc5c592d9123cd7a1f0a05412b65e2bb2cd9064dd704e7d21f4db9802de06e` |
| TileSmith-linux-x64.flatpak | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/5ec66032e06993a0e9ba2c48a0be0781787e901cd433a5964f04c3bdf8602d11) | `5ec66032e06993a0e9ba2c48a0be0781787e901cd433a5964f04c3bdf8602d11` |
| TileSmith-linux-x64.pacman | [0 / 48 engines flag it](https://www.virustotal.com/gui/file/f1601c5ea1fded394cd243d0accfd0acae32f16ccb56e6143bda2a7fafcfc926) | `f1601c5ea1fded394cd243d0accfd0acae32f16ccb56e6143bda2a7fafcfc926` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/fb6d9364fac0d0a680c1d572f14c124ca3ed905215084376b5145d4ff5acce68) | `fb6d9364fac0d0a680c1d572f14c124ca3ed905215084376b5145d4ff5acce68` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/154c8ee3e5d4c04e3c93722d9f9d8d56ac662d7da0e30f629ab69b9e7a5ba3ae) | `154c8ee3e5d4c04e3c93722d9f9d8d56ac662d7da0e30f629ab69b9e7a5ba3ae` |
| TileSmith-mac-universal.dmg | [0 / 56 engines flag it](https://www.virustotal.com/gui/file/25c856da78fbdba2eb7435664ece199b5e273bd241cf8fc4cfa67ed27589ccf2) | `25c856da78fbdba2eb7435664ece199b5e273bd241cf8fc4cfa67ed27589ccf2` |
| TileSmith-windows-portable.exe | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/d36fc3bd2807f50ee6d3e184a3092d8a7b5cc69dd8950319dba1259db43e5494) | `d36fc3bd2807f50ee6d3e184a3092d8a7b5cc69dd8950319dba1259db43e5494` |
