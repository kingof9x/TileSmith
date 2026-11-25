# wallcalc

A tiny, made-up Rust program used by the website's guide [How to read a Rust codebase](https://kingof9x.github.io/TileSmith/read-rust/).
It does one TileSmith job, working out how many power circuits an LED wall needs, so the guide has real Rust to read.
It is not part of the TileSmith app.

```sh
cargo run -- 10 5   # a wall 10 tiles wide and 5 high
cargo test          # 5 tests
```

The formula is the one in `tilesmith-desktop/TileSmith-App-Spec.md`: usable watts = V × A × (0.8 if derated) × power
factor, and tiles per circuit = floor(usable ÷ tile watts). `src/ffi.rs` only declares two NDI® functions to show what a
link to a C library looks like; nothing links to or calls NDI®. NDI® is a registered trademark of Vizrt NDI AB.
