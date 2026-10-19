# TileSmith {{VERSION}} animations: how to recreate them exactly

Everything here was read from the app's code (`source/readable/app.js`; line numbers are in
`source/readable/FUNCTIONS.md`). The pictures are frames of the real app, made by stepping its own animation loop
1/60 s at a time. All sizes are canvas pixels, and all times are seconds.

## 1. Frame loop and when to redraw

- One loop at up to 60 fps (`loop` → `tick(now)`). Each tick does the following:
  - `dt = min(0.1, (now − lastStep) / 1000)`, and `T = now / 1000` (the global animation clock).
  - It steps the build (`step(dt)`), then the DVD logo (`dvdStep(dt)`).
  - It redraws the master canvas when something moves, or every 250 ms as a safety net.
- **Something moves** when any of these is true:
  - a drag is in progress;
  - there was user input in the last 1.2 s;
  - the DVD screensaver is on;
  - a recording is running;
  - a build is playing and not finished;
  - a lock sparkle is still fading;
  - a wall shows `sweep` or a scrolling pattern.
- `cycle` redraws when its colour index changes. `tileshade-cycle` redraws when its step changes, and every frame
  during the 1.5 s slide.
- The viewport (the zoomed preview) is redrawn whenever the master canvas changed, and for 1.2 s after any input.
- On Android, use `withFrameNanos` (or `Choreographer`) with the same rules, so a still picture costs almost no
  battery.

## 2. Build animation: the state machine

![Build strip](screenshots/animations/anim-build-strip.png)

GIF (real time, first two tiles): `screenshots/animations/anim-build-first-tiles.gif`. Whole wall at Speed 4:
`anim-build-timelapse.gif`.

**Per wall** (`mkSim`): `{ph: 'wait', t: 0, i: 0 (tile being built), inst: 0 (tiles lit), delay: i × 0.6,
rate: RATES[i mod 8], sp: [] (sparkles), m: crew member}` with RATES = 1, 0.88, 1.1, 0.94, 1.06, 0.84, 1.14, 0.97.
So wall 2 starts 0.6 s after wall 1 and works at its own pace.

**Each frame** (`stepSim`): `d = dt × Speed × rate; t += d`, and then:

| Phase | Lasts (s at Speed 1) | Then | What happens |
|---|---|---|---|
| wait | until `t ≥ delay` | walkin, picks a crew member | Nothing is drawn yet; unbuilt slots show dashed #2a3340 outlines (8 on, 8 off). |
| walkin | 0.8 | move | The tech walks in from outside the wall edge, carrying the tile. |
| move | 1.1 | place | The tech walks on to the spot beside the slot, slowing down (ease-out). |
| place | 0.8 | lock | The tech turns to the wall and lifts the tile; the tile flies from the hands to the slot and grows from carry size to full size. |
| lock | 0.6 | walkout | The tile sits in the slot (still the dark carried-tile look) and the tech's arms shake. At 40% of lock (0.24 s) one sparkle ring starts. At the end the tile becomes **lit**: it now shows the pattern (`inst = i + 1`). |
| walkout | 1.5 | walkin of the next tile with the **next crew member** | The tech turns and walks off the way he came. After the last tile the wall is done. |

That is 4.8 s per tile at Speed 1 and rate 1. **Build order** (`seqRC`): the k-th tile is
`[col, row] = Horizontal ? [k mod cols, floor(k / cols)] : [floor(k / rows), k mod rows]`. The column is mirrored when
"Tech starts at" contains *right*, and the row is mirrored when it starts with *Bottom*. Half-tile layouts sort their
pieces by the order of their anchor cell.

**Crew rotation** (`pickCrew`): every walkin takes the next crew member in the list, skipping anyone already working on
another wall. Default crew: Marcus #8d5524, Elena #e0ac69, David #f1c27d, Chen #ffdbac, Priya #c68642, Malik #5c3a21
(skin), with hair colours #2b1d14, #4a3020, #6b4a2b, #14100c, #0f0f0f, #1c1410.

**Buttons:**
- **Start** (LED build menu) clears every wall and plays.
- **Play / Pause** freezes the simulation.
- **Stop** marks every wall done and stops.
- **Reset** clears every wall and waits.
- **Loop build**: when everything is done, wait **Pause before restart** seconds (default 3), then start again.

## 3. Build animation: positions and motion (`drawWallTech`)

![Phases](screenshots/animations/anim-tech-phases.png)

For the wall rectangle `L0..R0 × T0..B0` and the current tile `RC` (piece rectangle, size `tw × th`):

- **Tech size**: `sz = max(6, min(2.4 × tileH, 0.42 × canvasH, wallH / 1.05, wallW / 0.85))`.
- **Carry scale**: `cs = min(1, sz / (2.4 × tileH), 0.45 × sz / tw)`. The tech always fits inside the wall, and
  everything is clipped to the wall rectangle (only the wall's pixels reach the real LED screen).
- **Slot centre**: `sx = L0 + RC.x + tw/2`, `cy = T0 + RC.y + th/2`. The feet line `sy` is the slot bottom minus
  0.05 tile height. The feet are drawn at `yy = clamp(sy, T0 + 0.99 sz, B0 − 0.045 sz)`.
- **Entry side** `eF` is +1 (from the left) unless "Tech starts at" contains *right* (−1).
  - Preferred standing x: `sx − eF (tw/2 + 0.05 sz)` (beside the slot, on the side he came from). If that does not
    fit between `L0 + 0.31 sz` and `R0 − 0.31 sz`, he stands on the other side, else he is clamped.
  - He faces the slot: `sF` = +1 when the slot is to his right.
- **Walk-on point** `st`:
  - from the left, `min(L0 + 0.31 sz, R0 − 0.5 sz)`;
  - from the right, `max(L0 + 0.5 sz, R0 − 0.31 sz)`.
  - Off-wall point `off = L0 − 0.6 sz` (or `R0 + 0.6 sz`).
- **Facing angle** `A(f, b) = f > 0 ? b : π − b`. Walking uses b = 0.75; working (SIDE) uses b = 0.3. The angle is
  `th`; `sin(th)` > 0 shows the front, `cos(th)` gives the left/right mirror.
- `ss(q) = q²(3 − 2q)` (smoothstep), and `p = min(1, t / phaseLength)`.

| Phase | x | angle | arms / tile |
|---|---|---|---|
| walkin | `off + (st − off) p` | A(eF, 0.75) | walking (mv = 1), carrying |
| move | `st + (xs − st)(1 − (1 − p)²)` | A(eF, 0.75) | mv = 1 − p³ while moving, carrying |
| place | xs | from A(eF, 0.75) to A(sF, 0.3) over the first 45% (smoothstep) | carrying, lift u = p; after 30% the tile moves from the hands to the slot: `k = ss((p − 0.3)/0.7)`, `tile = hands + (slot − hands) k`, `scale = cs + (1 − cs) k` |
| lock | xs | A(sF, 0.3) | the tile is at the slot, full size; the hands hold its top corners and shake: `±sin(t × 40) × 0.006 sz` |
| walkout | `xs + (off − xs) q^1.7` with `q = max(0, (p − 0.2)/0.8)` | turns to the exit side over the first 40%; if he must turn through the back, he turns via the back view (−π/2) in the first 25%, then on to the exit angle by 55% | mv = min(1, p/0.3) |

**Carry position**: the tile's centre is at `x + dir × 0.27 sz × |cos(angle)|` (clamped inside the wall) and
`yy − 0.5 sz`. **Hands**: when a tile is shown, the two hands reach the tile's top corners, inset by
`min(0.045 sz, half width × 0.45, height × 0.45)`. The arms use two-bone inverse kinematics, with an upper arm of
0.16 sz and a forearm of 0.155 sz.

**Lock sparkle**: one ring per tile.
- On every frame the ring's `t` grows by `0.03 × Speed` (about 0.55 s at 60 fps).
- Radius `t × max(tileW, tileH) × 0.9`, line width `6(1 − t) + 1`, colour `rgba(255, 255, 200, 1 − t)`.
- Centred on the tile and clipped to the wall.

## 4. The technician drawing (`worker`, `cab`)

![Poses](screenshots/animations/anim-tech-poses.png)

`drawTech(ctx, x, y, size, pose)` draws a flat vector person standing with his feet at (x, y), about 1.05 × size tall.
`pose = {th: facing angle, mv: 0..1 walking amount, g: gait phase (x / (0.2 sz), so the steps match the ground), u: lift
0..1, m: crew member [name, skin, face photo, hair], carry, lock, shake, hands: [[x, y], [x, y]] or null}`.

- A shadow ellipse `rgba(0,0,0,.3)` sits at the feet. The body bobs by `|sin g| × 0.02 sz × mv` (plus a tiny idle
  sway).
- **Legs** pivot at `−0.37 sz`, swing `sin(g + iπ) × 0.55 × mv × |cos th|`, and bend the knee when stepping. Pants
  #1f2937, boots #4a3524 with black soles.
- **Arms** pivot at `−0.69 sz`, at the shoulders. The shirt sleeve is #2b6cb0 and the gloves are #fb923c.
  - Free arms swing opposite to the legs.
  - Carry: 1.25 + 1.6u rad.
  - Lock: arms up at 2.85 rad with a shake.
  - With `hands` set, inverse kinematics reaches the targets.
- **Hi-vis vest** in the Vest colour (default #b6ff00) with light reflective bands. On the back it shows the
  **Vest logo** text (default TILESMITH) or the uploaded logo. On the front it shows a **name tag** (white card, green
  top band, lanyard) when "Crew details & name tags" is on.
- **Head and hard hat**: skin and hair colours from the crew member, or a round face photo. The hard hat is in the Hard
  hat colour (default #ffcc00), with a brim on the facing side.
- The figure is mirrored by `cos(th) < 0`. Width grows with `|sin th|`, so the front view is wider than the side view.
  The back view (`sin th < −0.1`) hides the face and shows the vest logo.

![Options](screenshots/animations/anim-tech-looks.png)

**Carried tile** (`cab`, picture `anim-carried-tile.png`): a dark #1b2028 rectangle of the piece's size × scale, with
a #8ea0b0 frame of `max(1, 2k)` px, four amber #e8c11c corner squares of `max(2, 7k)` px, and a black handle bar of
0.24 × width × 8k px in the middle.

For an exact copy, port `worker` and `cab` line by line. The pose sheet above is drawn with those functions, so it is
the reference for every angle and arm pose.

Several walls: `anim-multiwall-start.png`. One technician per wall, staggered 0.6 s, each at its own pace.

## 5. DVD screensaver

![DVD](screenshots/animations/anim-dvd-strip.png)

GIFs: `anim-dvd.gif` (8 s), and `anim-dvd-corner.gif` (corner hit chance 100).

- **Sprite** (`dvdSpr`), 200 px tall:
  - *TileSmith logo*: five 2.2-unit squares at (1.5, 1.5), (6.3, 1.5), (3.9, 3.9) and (1.5, 6.3) in #22a0ac, plus
    (6.3, 6.3) in #ffb300 (unit = 20 px). Then "TILESMITH" in 800-weight type, 100 px, white, starting at x = 236.
  - *Text*: the logo text in 800-weight type at 156 px.
  - *Uploaded image*: the image at 200 px tall.
  - *Recolour*: with "Change color on each bounce", the sprite is filled `source-in` with `hsl(hue, 100%, 55%)`.
    Each new hue is random, at least 70° from the last one.
  - See `anim-dvd-sprites.png`.
- **Size**: the logo height is `dvdSize% × min(W, H)`, at most 95% of the area. Free area `Wr = W − lw`,
  `Hr = H − lh`.
- **Motion**:
  - Start at a random point, at a random angle of 30–60° (random signs).
  - Speed = `dvdSpeed × 0.25 × min(W, H)` px/s.
  - Each frame moves that distance. At a wall the logo reflects (x and y separately; both at once is a corner).
    It can bounce up to 16 times per frame.
- **Corner hits** (`dvdDecide`, `dvdAim`, `dvdAvoid`):
  - After every bounce, with probability `dvdCorner% × 0.45`, the logo aims for a corner. It unfolds the reflections
    and picks a direction that reaches a corner directly or via one side bounce: fewest bounces first, then the one
    that keeps its direction, then the closest angle. Angles stay between 2° and 88°.
  - Otherwise it keeps its angle. If the next hit would land within `max(2, min(0.3 × logo size, 0.4 × free size))`
    of a corner, it nudges the angle (by up to 60°, kept between 8° and 82°) so it misses.
- **Perfect loop**: see spec section 13. The position is `tri(U0 + vx t, Wr), tri(V0 + vy t, Hr)` with
  `tri(u, L) = L − |((u mod 2L) + 2L) mod 2L − L|`, and colours come from a seeded list, so frame T equals frame 0.
- **Where**: one logo per wall ("Each LED wall", clipped to the wall), or one over the whole canvas. It is drawn over
  the pattern and under the tile borders.

## 6. Moving test patterns

| Pattern | Rule | Pictures |
|---|---|---|
| `tileshade-cycle` | Tile (col, row) shows `TCYC[(col + 2 row + k) mod 3]`, with TCYC = #ff0000, #00ff00, #0000ff, `k = floor(T / 2.5)`. In each 2.5 s step the colour holds for 1.0 s. Then, for the last 1.5 s, `e = (frac − 0.4) / 0.6` and `p = e²(3 − 2e)`: the next colour fills the left `round(tw × p)` px of the tile and the current colour is pushed to the right. Neighbours never match. The tileshade lines, circle and text are drawn on top, with a dark casing so they show on every colour. | `anim-tileshade-cycle.gif`, `anim-tileshade-cycle-strip.png` |
| `cycle` | The full field is `[#f00, #0f0, #00f, #fff, #000, #ff0, #0ff, #f0f][floor(T / 1.5) mod 8]`. | `anim-cycle-strip.png` |
| `sweep` | A horizontal gradient with 7 stops `hsl((i × 60 + T × 60) mod 360, 100%, 50%)` at i/6. Over it, a vertical overlay: rgba(255,255,255,.7) at the top, clear at the middle, rgba(0,0,0,.6) at the bottom. Redrawn every frame. | `anim-sweep.gif`, `anim-sweep-strip.png` |
| Scroll (any pattern) | Offset `((v × T × s) mod size + size) mod size`, with s = Scroll speed × 0.2 × min(w, h) px/s and v = (1,1) ↘, (1,−1) ↗, (1,0) →, (0,1) ↓. The pattern is pre-rendered once and drawn 4 times (offsets −1/0 in x and y) to wrap. | `anim-scroll.gif`, `anim-scroll-strip.png` |

## 7. Other moving things

- **Viewport** (preview only, never in the output):
  - The selected wall gets a solid amber outline (3 px); other walls get a dashed outline (2 px, 6/4).
  - While dragging a wall, magenta #ff2bd6 dashed snap guides appear.
  - In Remove tiles and Mark half tiles modes, empty spots show red dashed rectangles with an X.
- **Toasts**: bottom centre, 2.5 to 9 s.
- **Recording status** (top bar, red): ● REC blank Ns → ● REC building → ● REC hold Ns → Saving video… → Saved name.
