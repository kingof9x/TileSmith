//! Power planning: how many tiles fit on one circuit.

use crate::error::PowerError;
use crate::tile::{Tile, Wall};

/// One power circuit from a distro.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Circuit {
    pub volts: f64,
    pub amps: f64,         // breaker rating
    pub derate: bool,      // load to 80% (continuous load rule)
    pub power_factor: f64, // 0.5 to 1
}

impl Default for Circuit {
    fn default() -> Self {
        Circuit {
            volts: 120.0,
            amps: 20.0,
            derate: true,
            power_factor: 1.0,
        }
    }
}

impl Circuit {
    /// usable watts = V × A × (0.8 if derated) × power factor
    pub fn usable_watts(&self) -> f64 {
        let derate = if self.derate { 0.8 } else { 1.0 };
        self.volts * self.amps * derate * self.power_factor
    }
}

/// Tiles per circuit = floor(usable ÷ tile watts), capped by the link limit if there is one.
pub fn tiles_per_circuit(
    c: &Circuit,
    tile: &Tile,
    link_limit: Option<u32>,
) -> Result<u32, PowerError> {
    if tile.max_watts <= 0.0 {
        return Err(PowerError::NoWattage(tile.name.clone()));
    }
    let fit = (c.usable_watts() / tile.max_watts).floor() as u32;
    if fit == 0 {
        return Err(PowerError::TileTooHungry {
            tile_watts: tile.max_watts,
            usable: c.usable_watts(),
        });
    }
    Ok(match link_limit {
        Some(max) => fit.min(max),
        None => fit,
    })
}

// Methods for one type can live in several files: this block adds a power method to Wall.
impl Wall {
    pub fn circuits_needed(&self, c: &Circuit) -> Result<u32, PowerError> {
        let per_circuit = tiles_per_circuit(c, &self.tile, None)?;
        Ok(self.tiles().div_ceil(per_circuit))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tile::BuildMode;

    fn demo_tile() -> Tile {
        Tile::new("Demo 500", 192, 192, 120.0, 6.3)
    }

    #[test]
    fn matches_the_spec_example() {
        // 120 V × 20 A × 0.8 = 1,920 W, and 1,920 ÷ 120 W = 16 tiles
        let c = Circuit::default();
        assert_eq!(c.usable_watts(), 1920.0);
        assert_eq!(tiles_per_circuit(&c, &demo_tile(), None), Ok(16));
    }

    #[test]
    fn link_limit_caps_the_count() {
        assert_eq!(
            tiles_per_circuit(&Circuit::default(), &demo_tile(), Some(10)),
            Ok(10)
        );
    }

    #[test]
    fn a_tile_bigger_than_a_circuit_is_an_error() {
        let mut tile = demo_tile();
        tile.max_watts = 5000.0;
        assert!(matches!(
            tiles_per_circuit(&Circuit::default(), &tile, None),
            Err(PowerError::TileTooHungry { .. })
        ));
    }

    #[test]
    fn a_wall_rounds_circuits_up() {
        let wall = Wall {
            name: "Main".into(),
            tile: demo_tile(),
            cols: 10,
            rows: 5,
            mode: BuildMode::Flown,
        };
        // 50 tiles at 16 per circuit = 3.125, so 4 circuits
        assert_eq!(wall.circuits_needed(&Circuit::default()), Ok(4));
        assert_eq!(wall.first_row(), "top");
    }
}
