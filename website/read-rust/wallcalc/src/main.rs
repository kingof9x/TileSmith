//! wallcalc: how many power circuits does an LED wall need?
//! Usage: wallcalc <columns> <rows>

use std::env;
use std::process::ExitCode;

use wallcalc::power::Circuit;
use wallcalc::tile::{BuildMode, Tile, Wall};

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: wallcalc <columns> <rows>");
        return ExitCode::from(2);
    }

    let (cols, rows) = match (parse_count(&args[1]), parse_count(&args[2])) {
        (Ok(c), Ok(r)) => (c, r),
        (Err(e), _) | (_, Err(e)) => {
            eprintln!("error: {e}");
            return ExitCode::from(2);
        }
    };

    let wall = Wall {
        name: String::from("Main wall"),
        tile: Tile::new("Demo 500", 192, 192, 120.0, 6.3),
        cols,
        rows,
        mode: BuildMode::GroundStack,
    };
    let circuit = Circuit::default(); // 120 V, 20 A, loaded to 80%

    match wall.circuits_needed(&circuit) {
        Ok(n) => {
            println!(
                "{}: {} tiles, {:.0} kg",
                wall.name,
                wall.tiles(),
                wall.weight_kg()
            );
            println!("needs {n} circuits at {:.0} W each", circuit.usable_watts());
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}

/// Turns "12" into 12, or explains what was wrong.
fn parse_count(text: &str) -> Result<u32, String> {
    let n: u32 = text
        .parse()
        .map_err(|_| format!("'{text}' is not a whole number"))?;
    if n == 0 {
        return Err(String::from("a wall needs at least one column and one row"));
    }
    Ok(n)
}
