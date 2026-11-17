# More NovaStar processors

Callum, 2026-11-17: "the novastar mctrl 4k is missing. add it and any other novastar processors that are missing."

Added to PROC (one line each, inside the NovaStar block so the Processor menu keeps one NovaStar group):
MCTRL300, MCTRL600, MCTRL660, MCTRL660 PRO, MCTRL700, MCTRL R5, MCTRL4K, MX20, MX30, NovaPro UHD Jr, VX16s, VX600,
VX600 Pro.

- Figures are from NovaStar's own spec sheets: MCTRL300 V2.4.3, MCTRL600 V2.3.4, MCTRL660 datasheet, MCTRL R5 V1.0.5,
  MCTRL4K V1.2.2 (oss.novastar.tech), MX20 V1.4.0, MX30 V1.5.1, NovaPro UHD Jr V1.6.0, VX16s V1.0.0, VX600 V1.7.1,
  VX600 Pro V1.3.0. MCTRL660 PRO and MCTRL700 come from NovaStar's 2021 product catalog (no separate sheet found).
- px10 (10-bit per-port figure) is set only where the sheet prints one (MCTRL R5, MCTRL4K, MX20, MX30, NovaPro UHD Jr);
  the rest halve at 10-bit as before.
- max for the MCTRL300/600/660/660 PRO/700 is the 1920 × 1200 at 60 Hz input limit (the sheets give no output total).
  MCTRL4K max is 8.8 MP (DP / HDMI input); DVI gives 8.3 MP, said in the note.
- VX600's sheet gives no per-port figure; 650,000 is its 3.9 MP over 6 ports.
- Optical outputs on every model copy the Ethernet ports, so ports counts are Ethernet only.
- Not added: VX4S-N, VX6s, non-Pro VX400 / VX1000, MX2000 Pro, MX6000 Pro (no NovaStar sheet could be read from here;
  the modular MX units also need per-card modelling like the H series).
- Test: tests/novastar_procs_test.py.
