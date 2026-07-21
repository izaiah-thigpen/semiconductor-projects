# Wafer Process SPC & Yield-Excursion Analysis

Statistical process control over a 5,000-wafer dataset of process parameters.

**Highlights**
- Individuals / moving-range (I-MR) control limits and out-of-control detection across six parameters (temperature, pressure, gas flow, etch rate, voltage, current).
- Rare yield defects localized to process-window excursions: pressure −2.3σ, temperature/etch +1.4σ — pinpointing the parameters to tighten.

**Files**
- `wafer_spc_analysis.py` — local-file version
- `wafer_spc_drive.py` — reads the dataset from Google Drive
- `wafer_spc.png` — control charts + excursion fingerprint + process window
- `SPC_Project_Report.pdf` — one-page report

Run: `pip install pandas numpy matplotlib requests` then `python wafer_spc_drive.py`
