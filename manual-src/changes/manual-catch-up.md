# Manual catch-up (2026-11-18)

Callum asked "is the manual up to date?". It was not: the v3.7 PDFs were built before #32 (installers, Check for
updates, Add-ons) and #33 (one sub menu at a time) merged, and the text still listed 3 languages and no Aluvision.

- make_manual.py: chapter 2 now starts with Downloading (release files), Add-ons and Updates, then "Building it
  yourself"; Info row lists all ten languages, Updates and Add-ons; The screen explains one sub menu at a time and
  double-click; Aluvision in the brand list; Random mix fault names in Tile faults; troubleshooting points to
  Info > Add-ons and Check for updates.
- make_manual.py DESK_MOCK: stubs child_process and sets process.execPath. Without them the manual build failed on main
  after #32 ("no module child_process", then ffCands' path.dirname(undefined)), so the next Build documentation run
  would have failed.
- make_spec.py: sub menu rule in 3.1, all ten languages in 3.5. make_mobile_manual.py: ten languages and Check for
  updates in the Info paragraph.
- Not run here: make_mobile_manual.py (needs make_kit_shots.py + make_kit_anims.py first). Not yet checked by Callum.
