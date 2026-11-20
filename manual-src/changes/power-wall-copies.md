# Walls never share power circuits (2026-11-20)

- Callum: on two IMAG walls on one canvas, drawing circuit 1 on one wall also wired the other wall as circuit 2. Cause: Duplicate
  wall (addWall(true)) copied the wall shallowly, so the copy shared S.pman (and the other list settings: half, gone, lay...)
  with the original. wallOwn() now deep-copies every list/object setting of a new or copied wall; a new (not copied) wall
  starts with Power wiring None, no circuits, its own cable.
- Power tray said "✓ every cable patched" when there were no cables; it now says "No cables yet" (grey). An empty cable card
  says "no circuits yet" instead of "not patched".
- Spare circuit chips on a cable card were named from the next wall's segment (2-1 on Socapex 1); now cable + leg.
- Test: tests/powercabling_test.py (copied/new wall, empty tray, spare chip names).
