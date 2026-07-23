# Quantum-Dot NMOS Process Design Kit — TCAD Process & Device Simulation

Senior design project: developing and validating a **Process Design Kit (PDK)** for a
four-mask NMOS transistor process, simulated end-to-end in **Synopsys Sentaurus TCAD**
before fabrication.

## Flow
- **SProcess** — modeled the four-mask fabrication flow (oxidation, implantation, diffusion, etch, metallization) to build the device structure and doping profiles.
- **Sentaurus Workbench** — parameterized the flow and swept key process variables (gate-oxide thickness, doping, field-oxide/gate parameters) as a design-of-experiments.
- **SDevice** — ran electrical simulations on each structure and extracted device figures of merit: threshold voltage (Vt), subthreshold swing (SS), transconductance (gm), and drive current (Id).

## Result
The flow produced a working NMOS across the swept process corners with well-formed
channel and source/drain junctions and a controlled thin gate oxide. Extracted device
parameters confirmed the PDK's process targets — the simulated PDK was deemed a success
and now anchors the mask-design and fabrication phase.

## Figures
- `fig1_device_structure.png` — simulated NMOS cross-section (doping concentration)
- `fig2_gate_oxide.png` — thin gate-oxide region detail
- `fig3_workbench_sweep.png` — Sentaurus Workbench parameter sweep (DoE)
- `fig4_sdevice_results.png` — SDevice extraction results across the sweep
- `TCAD_NMOS_Overview.pdf` — one-page project overview

## Tools
Synopsys Sentaurus TCAD (SProcess, SDevice, Sentaurus Workbench); MOSFET device physics;
process integration; parameter extraction; PDK development; design-of-experiments.
