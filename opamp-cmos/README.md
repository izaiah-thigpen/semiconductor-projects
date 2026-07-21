# Two-Stage CMOS Op-Amp (Cadence Virtuoso · SKY130)

A two-stage Miller-compensated operational amplifier designed in Cadence Virtuoso
on the SkyWater SKY130 (130 nm) PDK at 1.8 V.

**Design targets:** ≥65 dB gain, ≥60° phase margin, ≈8 MHz GBW, 5 pF load.

**Topology:** NMOS differential input pair with PMOS current-mirror load (stage 1),
PMOS common-source with NMOS current-source load (stage 2), Miller Cc + nulling
resistor Rz for compensation.

**Files**
- `opamp_schematic.png` — transistor-level topology
- `OpAmp_Design_Guide.pdf` — specs, device sizing, Virtuoso build steps, and ADE (Spectre) simulation recipe

*Schematic entry and test bench complete; SPICE simulation results (gain / phase-margin / GBW plots) to be added.*
