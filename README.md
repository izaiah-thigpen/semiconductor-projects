# Semiconductor & Electrical Engineering Projects

Izaiah Thigpen — B.S. Electrical Engineering, San Jose State University (Dec 2026)
[afmresults.com](https://afmresults.com) · [LinkedIn](https://www.linkedin.com/in/izaiah-thigpen-685704329)

A portfolio of hands-on projects spanning semiconductor process and device simulation,
process characterization, statistical process control, reliability engineering, analog
and digital IC design, and control systems. Each folder contains the code or design
files, a results figure, and a written report.

| Project | Area | Key result |
|---|---|---|
| [Quantum-Dot NMOS PDK (TCAD)](./tcad-nmos-pdk) | Process / device simulation | Four-mask NMOS validated end-to-end in Sentaurus (SProcess/SDevice); Vt, SS, and gm extracted across a process DoE |
| [Thermal Oxidation Characterization](./oxidation) | Fab process / metrology | Two-temperature study; within-wafer non-uniformity 11.9% → 1.2%, apparent Ea ≈ 1.06 eV, benchmarked to Deal–Grove |
| [Diode I–V Characterization](./diode-iv) | Device physics | Shockley fits (R² > 0.99) extracting ideality factor & saturation current for 5 devices |
| [Wafer Process SPC](./wafer-spc) | Quality / yield | I-MR control charts over 5,000 wafers; defects localized to process-window excursions |
| [Reliability Life-Data (Weibull)](./reliability-weibull) | Reliability | Censored-MLE Weibull (β=1.86 wear-out); Kaplan–Meier validation; AIC model selection |
| [CMOS Op-Amp (SKY130)](./opamp-cmos) | Analog IC design | Two-stage Miller op-amp designed in Cadence Virtuoso on the SKY130 PDK |
| [UART Transceiver (Verilog)](./uart-verilog) | Digital / RTL | Synthesizable 8-N-1 UART; self-checking testbench passes 512 bytes, 0 errors |
| [DC Motor PID Controller](./pid-motor-control) | Control systems | 6% overshoot, <100 ms settling, zero steady-state error, disturbance rejection |

## Tools & skills
Synopsys Sentaurus TCAD, Cadence Virtuoso, SPICE, SKY130 PDK, Verilog (Icarus/Vivado),
Python (NumPy, pandas, SciPy, Matplotlib), MATLAB; semiconductor process & device
simulation, parameter extraction, statistical analysis, MLE, SPC, reliability life-data
analysis, RTL design & verification, and control-loop design.

*Several analysis scripts read their datasets directly from shared cloud links, so they
run without local data files.*
