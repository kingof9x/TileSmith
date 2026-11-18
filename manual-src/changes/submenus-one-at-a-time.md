# Left panel sub menus open one at a time

Asked for by Callum on 2026-11-18: "only one sub menu at a time unless the user double clicks on the carrot ... give power
users the ability to open more than one sub menu."

- Top-level menus (Canvases, Animation Options, Engineering, ...) still open and close freely, several at once.
- Opening a sub menu closes the other open sub menus in the same parent menu. Sub menus nested inside it (Tile model ›
  Tile details, LED processor › Data wiring) and sub menus in other top-level menus are left alone.
- Double-clicking a sub menu header (the caret or its name) opens it and keeps the others open. A second click that
  lands somewhere else (the canvas list moves when another canvas is selected) counts as the double-click and is swallowed.
- 2026-11-18 follow-up (Callum: "there is a lag or delay when automatically closing a sub menu"): the others now close
  at once instead of after 0.32 s, with a 0.16 s slide (`::details-content` height transition, `interpolate-size` on
  #left, off with reduced motion). `subPin()` scrolls the panel while they shrink so the clicked header stays under the
  pointer, as far as the scroll position allows.
- Canvas sub menus follow the same rule, and Add canvas opens the new canvas alone.
- Code: `subOne` / `subSet()` / `subPin()` click handler next to `SUB()` in index.html; `cvAdd` closes the other canvases.
- Header text is no longer selectable (a double-click used to select the word).
- Test: tests/submenu_test.py. Not yet checked by Callum.
