# Code review, stress test and hardening (2026-11-24)

- Callum asked for a full review with comments, bug fixes and a stress test, ready for a critical outside reviewer.
  Findings, fixes, open items and timings: docs/CODE-REVIEW.md.
- User-visible: web links never open inside the app (main.js navigation lock); Update now refuses a download whose SHA-256
  does not match GitHub's; autosave is crash-safe and an unreadable save is kept (state.json.unreadable-<time>) with a
  message; projects only load embedded pictures; YES TECH Xtra 1.9 now 163 W (was listed twice, 145 W won).
- Speed: pieces() cache check, wst() cached with the tiles, text widths cached (mtW).
- Tests: 10 stale tests fixed, charpack_test.py removed, tests/_paths.py, run_all.py, stress_test.py, electron_test.py,
  .github/workflows/tests.yml.
- Not yet checked by Callum: the Xtra 1.9 wattage against the current YES TECH sheet; Update now on a real release.
