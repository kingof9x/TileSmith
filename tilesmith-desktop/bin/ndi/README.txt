WINDOWS: NDI® runtime that is built into TileSmith.
"npm run dist" fills this folder automatically from the free NDI® SDK installed on the build computer
(https://ndi.video/for-developers/ndi-sdk/). Or copy these two files here yourself from the SDK:
  Processing.NDI.Lib.x64.dll
  Processing.NDI.Lib.Licenses.txt   (the license notices; NDI® requires them to ship with the runtime)
Leave this folder empty to build without it; NDI® output then needs the NDI® Runtime or NDI® Tools on each computer.
NDI® is a registered trademark of Vizrt NDI AB.
