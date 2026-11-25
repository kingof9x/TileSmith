//! Tiles (one LED cabinet) and walls (a grid of tiles).

/// One LED product, such as a 500 mm cabinet.
#[derive(Debug, Clone, PartialEq)]
pub struct Tile {
    pub name: String,
    pub px_w: u32,      // pixels across
    pub px_h: u32,      // pixels down
    pub max_watts: f64, // power draw at full white
    pub kg: f64,
}

impl Tile {
    /// Makes a tile. `&str` borrows the name; `to_string` makes the tile its own copy.
    pub fn new(name: &str, px_w: u32, px_h: u32, max_watts: f64, kg: f64) -> Self {
        Tile {
            name: name.to_string(),
            px_w,
            px_h,
            max_watts,
            kg,
        }
    }

    pub fn pixels(&self) -> u32 {
        self.px_w * self.px_h
    }
}

/// How the crew builds the wall.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BuildMode {
    GroundStack, // stacked up from the floor
    Flown,       // hung from motors, built from the top
}

/// A grid of identical tiles.
#[derive(Debug, Clone)]
pub struct Wall {
    pub name: String,
    pub tile: Tile,
    pub cols: u32,
    pub rows: u32,
    pub mode: BuildMode,
}

impl Wall {
    pub fn tiles(&self) -> u32 {
        self.cols * self.rows
    }

    pub fn weight_kg(&self) -> f64 {
        self.tiles() as f64 * self.tile.kg
    }

    /// Which row the crew starts on.
    pub fn first_row(&self) -> &'static str {
        match self.mode {
            BuildMode::GroundStack => "bottom",
            BuildMode::Flown => "top",
        }
    }
}
