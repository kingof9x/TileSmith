# Power settings rethink (2026-11-19, thread "Power settings rethink")

- Callum (2026-11-19): the old top-level Power settings (Power distribution switch, Distribution cable, Circuit voltage,
  Breaker, Edison plugs per wall circuit) didn't fit the distros and drawn wiring. He approved the proposal in
  /mnt/project-files/power-settings/power-settings-demo.html, including a cable picked per wall.
- Engineering > Power is now Supply / Load / This wall / Show. Power is on while S.dists holds a supply (pdOn); the
  pdist switch, pwall and pwallA are gone.
- Supply: distro cards own the circuit voltage cv (L-N or L-L for multi-phase systems, supVolts) and breaker cb (capped at
  the connector rating). "+ Add house power" adds a single-phase house supply (Edison outlets, outl outlets per house
  circuit, hb house breaker) that replaces the old Edison wall-circuit fields.
- This wall: Fed from (wall key pfeed) and Cable (wall key pdt, only kinds the supply has). pwC(w) gives a wall's
  supply, cable type, V, A and usable watts; pwMirror keeps S.pvolt / S.pamps / S.pdt in step. Circuits are numbered
  per wall segment (SEG/segDef, cabNo counts within each cable type), so walls on different supplies and cables work.
- Patching only goes to the wall's own supply; moving a cable to another supply in the tray changes the walls' Fed from.
- Old projects (no pwv) are migrated by pwMigrate: power off clears supplies, old distros take cv/cb from pvolt/pamps,
  an old Edison setup becomes house power, otherwise a distro matching the old voltage is made; projects with 2+
  distros get pfeed from their existing patches (pwFix in dsState).
- New TR group "// Power settings". Spec and manual updated.
- Tests: powercabling_test (supplies, Fed from, house power, tray move, migration), powercheck_test, edison_test,
  phase_test, labels_test and the other power users updated.
- Not yet checked by Callum.
