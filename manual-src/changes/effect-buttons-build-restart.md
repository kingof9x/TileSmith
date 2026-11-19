# Effect buttons light up; LED build on/off survives a restart

2026-11-19, from a user bug report Callum passed on.

- The toolbar Start LED Build, Start DVD Screensaver and Start Tile Faults buttons (and the Start tile faults
  button in the panel) get the green `live` look (like Start NDI) while their effect is on. `fxLit()`, called from
  the viewport draw next to the button text updates.
- The LED build is saved as on or off when the app closes and comes back the same way. It is off after a first
  install. Stored outside the project as the app setting `localStorage['tilesmith-build-on']` ('1' / '0'), so it
  is not part of undo or of .tilesmith project files. `bldRun`, `bldTrack()` (called from `step()`), `bldActive()`.
- The bug: with Loop build continuously on, the loop restarted the build a few seconds after every start even if
  the build had been stopped. The loop now only restarts a build that is on (`bldRun`).
- A looped build counts as on in the pause between rounds, so the toolbar button reads Stop LED Build then and
  stops it. A paused build (Play / Pause) counts as off.
- Test: manual-src/tests/fxbuttons_test.py.
