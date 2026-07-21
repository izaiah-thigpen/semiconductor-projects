# Diode I–V Characterization & Parameter Extraction

Extracts diode parameters from measured current–voltage sweeps of five devices:
a silicon diode, a 1N5234 Zener, and red / green / yellow LEDs.

**Highlights**
- Fits the Shockley diode equation to the exponential region (R² > 0.99) to extract ideality factor (n) and saturation current (Is).
- Silicon junctions near-ideal (n ≈ 1.1–1.3, ~0.75 V turn-on); LEDs higher (n ≈ 1.7–2.4, ~1.8–2 V), consistent with recombination in wider-bandgap material.

**Files**
- `diode_iv_analysis.py` — local-file version
- `diode_iv_drive.py` — reads the workbook from Google Drive
- `diode_iv.png` — linear + semilog I–V with fits
- `Diode_Lab_Report.pdf` — one-page report

Run: `pip install numpy pandas openpyxl matplotlib requests` then `python diode_iv_drive.py`
