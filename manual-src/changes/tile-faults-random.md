# Tile faults: Random mix variety (2026-11-14)

Callum reported that Random mix with one random tile "always chooses dead tile" (v3.6). In tests the fault was already
random (all 12 turned up), but nothing stopped the same fault coming back several starts in a row, several random tiles
could share a fault, and the panel never said which fault was showing, while four faults look like a black tile (Dead
tile, Data chain break at a row end, Module out, Power circuit tripped).

- glRT(): never the same fault twice in a row (GLLAST). Used for tiles picked by hand.
- glDeck(k): faults for k random tiles, all 12 used before any repeats, no repeat across the deck seam or from the
  previous start. glRoll uses it.
- glNames(): the status line under Tile faults names the faults showing in Random mix ("Faults: Flicker.").
- Test: tests/tilefaults_test.py (60 starts with one random tile, 12 tiles get 12 faults, picks vary). Prints ALL OK.
  Set CHROME to a Chromium binary if Python Playwright has no browser of its own.
- Not yet checked by Callum.
