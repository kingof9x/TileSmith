MAC: NDI® runtime that is built into TileSmith.
"npm run dist:mac" fills this folder automatically from the free NDI® SDK for Apple installed on the build Mac
(https://ndi.video/for-developers/ndi-sdk/ - it installs to /Library/NDI SDK for Apple). Or copy here yourself:
  libndi.dylib                       (from /Library/NDI SDK for Apple/lib/macOS)
  the license .txt next to it        (the license notices; NDI® requires them to ship with the runtime)
Leave this folder empty to build without it; NDI® output then needs the NDI® Runtime or NDI® Tools on each Mac.
NDI® is a registered trademark of Vizrt NDI AB.
