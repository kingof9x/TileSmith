//! Everything that can go wrong while planning power.

use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum PowerError {
    /// The tile's spec has no wattage, so nothing can be planned.
    NoWattage(String),
    /// One tile draws more than a whole circuit can supply.
    TileTooHungry { tile_watts: f64, usable: f64 },
}

// Display is what you see when the error is printed with {}.
impl fmt::Display for PowerError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PowerError::NoWattage(name) => write!(f, "tile '{name}' has no wattage in its spec"),
            PowerError::TileTooHungry { tile_watts, usable } => write!(
                f,
                "one tile needs {tile_watts} W but a circuit only gives {usable} W"
            ),
        }
    }
}

impl std::error::Error for PowerError {}
