# Thermal Oxidation Process Characterization

Two-condition study (900 °C and 1100 °C, wet, 60 min) of SiO₂ growth on silicon,
from 160 ellipsometry measurements across 16 wafers.

**Highlights**
- Python/NumPy pipeline that screens measurement goodness-of-fit to reject invalid data.
- Mean oxide grew 909 → 4160 Å (4.6×) with temperature; apparent activation energy ≈ 1.06 eV.
- Within-wafer non-uniformity collapsed 11.9% → 1.2% (reaction- → diffusion-limited).
- Benchmarked to the Deal–Grove model; 900 °C within ~5%, 1100 °C ~30% below (traced to sub-standard steam pressure, ruling out ramp effects by simulation).

**Files**
- `oxide_temperature_study.py` — two-condition comparison (primary)
- `oxide_drive_analysis.py` — reads the data directly from Google Drive
- `oxide_uniformity_analysis.py` — single-condition SPC / wafer-map view
- `oxide_temperature_study.png`, `oxide_analysis.png` — figures
- `Oxidation_Lab_Report.pdf` — one-page report

Run: `pip install numpy matplotlib pandas openpyxl requests` then `python oxide_temperature_study.py`
