# Power cabling (2026-11-19, thread "Add hand-drawn power cabling with circuit limits")

- Each wall starts on its own cable (per-wall `pown`, default on): circuit numbers jump to the next cable at each wall
  (pcStart in powerPlan), so walls far apart never share a Socapex; unused circuits are spare. `pcabs` = cables run to the
  wall; circuits past them get `nocab` + over (pcCap).
- Manual power wiring: circuit chips (#pchips, pcabUI, pcSel/pcIdx) pick the circuit to draw onto; dashed chips start a
  new circuit on a spare. Full circuits still refuse tiles (pmanAdd).
- Maker power data PWR / PWRSRC for 369 of 402 models (vin range, panels per power link at 110/230 V, loop-through A,
  average W, source), researched 2026-11-19 from maker sheets/manuals (ROE manuals via 4Wall and ledwallcentral.com PDF
  copies). pwrEnforce greys out voltages a tile does not take (and moves off one), sets plink to mkLink (pmk remembers
  it, a lower user value is kept); tpcW also caps at mkLink. Engineering gets pwrRows. Research JSON:
  /mnt/project-files/power-cabling/research/.
- Max W corrected from maker sheets: ROE Meru MR1.9 (300) and Half (150), INFiLED DB2.6 (150), AR4.8 (270), Absen KL1.5 II
  (129), PL2.5 Pro V10 (170), Unilumin UpadIV 1.9 (150), YES TECH MG6S 2.84 (105).
- Option A (Callum 2026-11-19, card): the distros set the rules. dsRules/dsVolts/dsKinds: voltage only one every distro supplies, cable only a type with distro outputs, breaker clamped to the connector rating (rA), #dsSrc shows the source. powercheck_test now expects the clamp instead of a breaker warning.
- Open: INFiLED GXmk2 / NX voltage (website 100-240 V vs brochure 200-240 V; 200-240 used).
- 2026-11-19 follow-up (Callum: "I still can't add socapex cable or draw circuit"): cable cards with circuit chips for every wall (#pcabCards, pcabUI), + Add Socapex cable / × (pcabs, reserved via PCK0 so the next wall starts after them; empty reserved cables go in the tray via pcEmpty), Draw circuit (pcToManual keeps an automatic pattern's circuits).
- Test: tests/powercabling_test.py.
