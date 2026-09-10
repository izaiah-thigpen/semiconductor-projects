# Semiconductor & Electrical Engineering Projects

Izaiah Thigpen — B.S. Electrical Engineering, San Jose State University (Dec 2026)
[afmresults.com](https://afmresults.com) · [LinkedIn](https://www.linkedin.com/in/izaiah-thigpen-685704329)

A portfolio of hands-on projects spanning semiconductor process characterization,
device physics, statistical process control, reliability engineering, RTL design,
and control systems. Each folder contains the code, a results figure, and a
written report.

| Project | Area | Key result |
| --- | --- | --- |
| [Thermal Oxide Variation Characterization](oxidation) | Fab process / metrology / SPC | Variance decomposition in JMP + Python; gravity-aligned vertical gradient in 24/24 wafers; one boat slot out of control in two independent runs |
| [Diode I–V Characterization](diode-iv) | Device physics | Shockley fits (R² > 0.99) extracting ideality factor & saturation current for 5 devices |
| [Wafer Process SPC](wafer-spc) | Quality / yield | I-MR control charts over 5,000 wafers; defects localized to process-window excursions |
| [Reliability Life-Data (Weibull)](reliability-weibull) | Reliability | Censored-MLE Weibull (β=1.86 wear-out); Kaplan–Meier validation; AIC model selection |
| [UART Transceiver (Verilog)](uart-verilog) | Digital / RTL | Synthesizable 8-N-1 UART; self-checking testbench passes 512 bytes, 0 errors |
| [DC Motor PID Controller](pid-motor-control) | Control systems | 6% overshoot, <100 ms settling, zero steady-state error, disturbance rejection |
| [CMOS Op-Amp (SKY130)](opamp-cmos) | Analog IC design | Two-stage Miller op-amp designed in Cadence Virtuoso on the SKY130 PDK |

## Tools & skills

Python (NumPy, pandas, SciPy, Matplotlib), **JMP (JSL scripting, REML variance
components, process capability, control charts)**, MATLAB, Verilog
(Icarus/Vivado), Cadence Virtuoso, SPICE, SKY130 PDK; DOE, statistical analysis,
MLE, SPC/APC, gauge R&R, reliability life-data analysis, RTL design &
verification, control-loop design.

*Several analysis scripts read their datasets directly from shared cloud links, so
they run without local data files.*
