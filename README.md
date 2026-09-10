# Semiconductor & Electrical Engineering Projects

Izaiah Thigpen — B.S. Electrical Engineering, San Jose State University (Dec 2026)
[afmresults.com](https://afmresults.com) · [LinkedIn](https://www.linkedin.com/in/izaiah-thigpen-685704329)

Hands-on projects across semiconductor process characterization and control,
device physics, TCAD, reliability, RTL design, and control systems. Each folder
holds the code, a results figure, and a written report.

## Fab process & metrology

| Project | Tools | Key result |
| --- | --- | --- |
| [Thermal Oxide Variation Characterization](oxidation) | JMP, Python, Filmetrics | Variance decomposition into within-wafer / wafer-to-wafer / position components. Gravity-aligned vertical gradient in 24/24 wafers; one boat slot out of control in two independent runs. JMP and Python agree to 7 significant figures |
| [Photoresist Contrast Curve (AZ1512)](photoresist-contrast) | Contact aligner, Filmetrics, Python | γ = 1.98, dose-to-clear E₀ = 48.6 mJ/cm² across 12 wafers; 5.7 % coat uniformity, 19 % wafer-to-wafer dose spread, 2.2× exposure margin |
| [Quantum-Dot NMOS PDK (TCAD)](tcad-nmos-pdk) | Synopsys Sentaurus | Four-mask NMOS flow simulated end to end in SProcess/SDevice; Workbench DoE swept gate-oxide thickness and doping, extracting V<sub>t</sub>, SS, g<sub>m</sub>, I<sub>d</sub> across process corners |
| [Wafer Process SPC & Yield Excursion](wafer-spc) | Python | I-MR charts on six parameters over 5,000 wafers; the 7 defective wafers share an excursion signature — pressure −2.3σ, temperature and etch rate +1.4σ |

## Devices, reliability & design

| Project | Tools | Key result |
| --- | --- | --- |
| [Diode & LED I–V Characterization](diode-iv) | Python | Shockley fits (R² > 0.98) across five devices; near-ideal silicon junctions (n = 1.11–1.30, V<sub>on</sub> ≈ 0.75 V) separated from recombination-dominated LEDs (n = 1.66–2.44, V<sub>on</sub> = 1.8–2.0 V) |
| [Reliability Life-Data (Censored Weibull)](reliability-weibull) | Python, SciPy | Censored MLE on 3,000 units (60 % censored): β = 1.85 wear-out, η = 181 h, B10 = 54 h; Weibull preferred over lognormal by AIC, validated against Kaplan–Meier |
| [UART Transceiver](uart-verilog) | Verilog, Icarus, Vivado | Parameterized 8-N-1 UART with 16× oversampling and 3-sample majority vote; self-checking loopback passes 512 bytes with 0 errors, decodes correctly at ±3 % baud mismatch |
| [DC Motor PID Controller](pid-motor-control) | MATLAB | 6.2 % overshoot, 38 ms rise, 96 ms settling, zero steady-state error; 1.0 % dip under step load torque with full recovery, versus open-loop droop to ~860 rpm |
| [CMOS Op-Amp (SKY130)](opamp-cmos) | Cadence Virtuoso | Two-stage Miller-compensated op-amp on the SKY130 open PDK |

## Tools & skills

**Statistical / process:** JMP (JSL scripting, REML variance components, process
capability, control charts), Python (NumPy, pandas, SciPy, Matplotlib), DOE,
SPC/APC, gauge R&R, process capability, censored-MLE life-data analysis

**Process & device:** Synopsys Sentaurus TCAD (SProcess, SDevice, Workbench),
thermal oxidation, photolithography, Filmetrics reflectometry, Deal–Grove
modelling, PDK development

**Design:** Verilog RTL and self-checking verification (Icarus, Vivado), Cadence
Virtuoso, SPICE, SKY130 PDK, MATLAB control-loop design

*Several analysis scripts read their datasets directly from shared cloud links, so
they run without local data files.*
