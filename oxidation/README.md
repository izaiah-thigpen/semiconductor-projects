# Thermal Oxide Variation Characterization

Partitioning oxide thickness variation in a wet thermal oxidation process into
within-wafer, wafer-to-wafer, and load-position components — framed the way a fab
sustaining engineer would frame it, and analyzed twice in two independent tools.

**Primary analysis: JMP.** **Independent cross-check: Python.** The two agree to
seven significant figures across REML variance components, method-of-moments
ANOVA, and descriptive statistics. The one place they diverge is documented and
explained rather than reconciled away.

---

## The data

Two furnace runs, wet O₂ from a bubbler, Si (100), 16 wafers per run in a boat
with dummy wafers at both ends. Five Filmetrics reflectometry points per wafer —
top, center, bottom, left, right of a vertically standing wafer. 160 measurements
total.

| Run | Setpoint | Time at setpoint | Wafers analyzed |
| --- | --- | --- | --- |
| R1 | 900 °C | 60 min (dwell only) | 12 of 16 |
| R2 | 1100 °C | 60 min (dwell only) | 12 of 16 |

**This is not a DOE.** Time is constant and only temperature varied, so the two
factors are not confounded with each other — but with one run per temperature,
temperature is fully aliased with run, day, furnace load and metrology session.
No rate constant or activation energy is estimable from these data. The 2×2
factorial that would resolve it is specified in the report.

---

## Findings

**A gravity-aligned vertical gradient, in every wafer.** Oxide is thickest at the
top of the wafer and thinnest at the bottom, without exception in **24 of 24
wafers** across both runs. Mean top-minus-bottom is 25.0 % at 900 °C and 2.25 % at
1100 °C. The horizontal (left–right) difference is small and inconsistent in
sign. The signature follows gravity, not gas flow.

**One boat slot is out of control in two independent runs.** Wafer A15 exceeds the
upper control limit on both the individuals and the moving-range chart, in both
runs. Removing it and one other outlier collapses the 900 °C wafer-to-wafer
variance component from 60.6 % to 0.9 % — nearly all apparent wafer-to-wafer
variation at 900 °C is two wafers, not a distributed load effect.

**Variance components** (metrology-clean subset, 12 wafers per run):

| Component | 900 °C | 1100 °C |
| --- | --- | --- |
| Wafer-to-wafer within run | 60.6 % | 48.4 % |
| Within-wafer: vertical position | 28.6 % | 16.3 % |
| Within-wafer: residual | 10.8 % | 35.2 % |

No run-to-run component is reported: with two runs it carries one degree of
freedom and absorbs temperature, day, load and metrology all at once. REML
confidence intervals show the 1100 °C wafer-to-wafer component is not
distinguishable from zero.

**Both recipes grow ~35 % less oxide than Deal–Grove predicts.** The deficit is
proportional across a 200 °C span and flat across boat slot, so it is a
process-level offset rather than a load effect or a temperature-dependent model
error. Ramp accounting is ruled out — dwell-only timing means real growth time
exceeds 60 min, which would push measured thickness *above* prediction, not
below. Sub-saturation bubbler water partial pressure is the leading hypothesis,
unconfirmed.

**Capability fails for two different reasons.** At 1100 °C, Cp = 3.43 with
Cpk = −8.62: excellent spread, catastrophic centering, correctable by recipe
time. At 900 °C, Cp = 0.44: the process width alone exceeds the tolerance band,
so re-centering would not help. Same verdict, opposite corrective action.

---

## Data integrity work

Two problems in the raw exports had to be resolved before any analysis was valid.

**A metrology recipe was applied in error to 40 of 160 measurements**, in a
separate session a week later. In R2 the recipe boundary coincides exactly with a
157 Å step in wafer mean at the A03/A04 slot boundary — so load position and
metrology recipe are perfectly aliased there. Analyzed raw, the R2 wafer-to-wafer
component reads 72.2 %; on the clean subset it reads 48.4 %. The artifact would
have sent an investigation after a load-position problem the furnace does not
have.

**The export header statistics describe a different measurement set than the rows
beneath them.** Reconstruction showed the header was computed from the original
60-point session and never regenerated after the re-measured wafers were
appended. A competing hypothesis — that a floating-index refit explained the
whole discrepancy — was tested and ruled out on the second moment.

---

## Retraction

An earlier version of this project reported *"within-wafer non-uniformity improved
from 11.9 % to 1.2 %"* and *"apparent activation energy ≈ 1.06 eV."* Both are
withdrawn.

The uniformity figures are a comparison between the 900 °C and the 1100 °C run,
not an improvement over time. The difference is a consequence of setpoint: at
900 °C wet oxidation retains reaction-rate-limited character (2.05 eV linear
coefficient), while at 1100 °C growth is strongly parabolic (0.78 eV), so the same
local temperature non-uniformity produces a far larger fractional spread at the
lower setpoint.

The activation energy cannot be estimated from these data. Two runs give zero
degrees of freedom, no residual, and no confidence interval, and any two-point
value absorbs every run-level difference between the two furnace loads.

---

## Files

| File | What it is |
| --- | --- |
| `OX-VAR-001_process_report.pdf` | Two-page process report + appendices (fab format: objective, matrix, results, conclusions, process window, limitations, next experiment) |
| `OX-VAR-001_analysis.jsl` | JSL script reproducing the full JMP analysis |
| `OX-VAR-001_build_table.jsl` | Self-contained JSL — builds the data table from embedded values, no external file needed |
| `JMP_workflow_and_validation.md` | Click-paths for every platform plus expected values for cross-checking |
| `analysis.py` | Independent Python implementation |
| `oxide_tidy_for_JMP.csv` | Tidy dataset, one row per measurement |
| `wafer_uniformity.csv` | Per-wafer summary |
| `results.json` | All computed results, primary and sensitivity cases |
| `figures/` | Report figures and JMP platform screenshots |

Run `OX-VAR-001_build_table.jsl` in JMP to reproduce the analysis table from
scratch — it needs no data file and prints six self-check values to the log.

---

## Next experiment

1. **Gauge R&R first.** The residual within-wafer term (35 % of total variance at
   1100 °C) cannot be attributed to the process until measurement variation is
   bounded.
2. **2×2 factorial, replicated.** 900/1100 °C × 30/60 min, two replicate runs per
   cell, randomized across days, slot held constant as a blocking factor, one
   frozen metrology recipe, nine-point pattern with recorded X–Y coordinates.
3. **Directed checks.** Compute expected pH₂O from bubbler temperature and carrier
   flow; profile the tube with a calibrated thermocouple at three heights. These
   discriminate the thickness deficit and the gradient mechanism.
