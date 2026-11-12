Hand-drawn crew files, loaded by index.html only when Technician > Character style is set to Hand-drawn.

- three.min.js, FBXLoader.js, fflate.min.js: three.js r147 (MIT) and the libraries its FBX loader needs.
- rb-assets.js: two Microsoft Rocketbox avatars (a man and a woman in hard hat and hi-vis vest) as binary FBX,
  their motion-captured walk animations, and their colour textures, all base64 encoded so they load from file://
  (desktop) and from the mobile app the same way. Rocketbox: https://github.com/microsoft/Microsoft-Rocketbox (MIT).

If this folder is missing, Hand-drawn falls back to the Classic crew and says so under Character style.
Backlit does not need this folder.
