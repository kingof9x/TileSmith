# Aluvision tiles in the catalog

New brand **Aluvision** (in PBR) with 12 Hi-LED 55 models, asked for by Callum on 2026-11-16 ("add all Aluvision tiles",
especially the Hi-LED 55 Plus 2.5 mm).

- Flat: 1.9, 2.5, 2.8 indoor and OU 3.9 outdoor (496×496 mm). Curved: R437 concave and convex, R1421 convex and R1476
  concave, each in 2.5 and 2.8.
- Every figure is from Aluvision's own Hi-LED 55 brochure (Aluvision NV, code L24E01; PSCO's copy, since aluvision.com
  has a bot check). Power is max W per tile as printed; PINFO also gives average W, brightness, refresh, viewing angle,
  NovaStar power box and the source.
- The Hi-LED 55+ (Plus) has no separate figures: the brochure describes it as the same 496×496×55 tile built from four
  modules, so the flat 2.5 / 2.8 entries cover it.
- Processors: `CMP.push([/^Aluvision /,['novastar']])`, since the brochure names only NovaStar power and sending boxes.
- Model menu groups: "Aluvision Hi-LED 55" and "Aluvision Hi-LED 55 curved" (TSER).
- Not published, so not in the app: IP rating (only a rental sheet says IP44 for the 2.5), max hanging height, the
  curve radius in mm, a separate R1421 / R1476 size (the brochure prints one for both).
- Test: tests/aluvision_test.py. tests/tilemenu_test.py already failed on main (it predates AOTO and Gloshine).
