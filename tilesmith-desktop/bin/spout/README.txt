WINDOWS: Spout output, built into TileSmith.
This folder already holds what TileSmith needs, so nothing has to be downloaded:
  SpoutDX.dll         Spout SDK 2.007.017, the "MT" build (needs no Visual C++ runtime)
                      from https://github.com/leadedge/Spout2/releases/tag/2.007.017
                      file Spout-SDK-binaries_2-007-017_1.zip -> Libs_2-007-017/MT/bin/SpoutDX.dll
                      SHA-256 bbcee6f0031f6bd1a6461585c53f3f8f3cecbf006b486661bcde6413e2addef5
  Spout-licence.txt   Spout's licence (Simplified BSD). It must ship with the DLL.
"npm run dist" packs both into the portable exe, and the "Start Spout" button appears in the top bar.
To build WITHOUT Spout, delete SpoutDX.dll from this folder; the Spout button is then hidden.
Use only this exact DLL: TileSmith calls its functions by name, and another Spout version may not match.
Spout is by Lynn Jarvis: https://spout.zeal.co/
