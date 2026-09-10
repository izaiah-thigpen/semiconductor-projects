# OX-VAR-001 — JMP workflow and cross-validation

Two ways to run this. The script does it in one pass; the click-paths teach you where each
platform lives. Do it by hand once, then run the script and confirm you get the same numbers.

The validation tables at the end exist so you can prove the JMP output matches an independent
Python implementation. That cross-check is worth more in an interview than either analysis alone.

---

## Running the script

1. `File > Open` → `oxide_tidy_for_JMP.csv`, confirm 160 rows × 14 columns.
2. `File > New > Script`, paste `OX-VAR-001_analysis.jsl`.
3. Edit the `csvPath` line at the top to your actual path.
4. `Edit > Run Script` (Ctrl+R).
5. Output lands in a journal window: `File > Save As > PDF`.

**If a platform errors.** JSL platform messages change between JMP versions. Build that one
platform by hand from the click-path below, then use its red triangle → `Save Script > To Script
Window` to get the exact syntax your version wants, and paste it back. This is the normal way to
write JSL — nobody writes platform calls from memory.

---

## Column setup

Modeling types matter more than they look. `Slot` must be **Nominal** for variance components
(it's a grouping label) and **Continuous** for trend plots (it's a position). The script keeps it
Continuous and uses `Wafer` as the nominal grouping column, which avoids switching back and forth.

Set `FurnPos` value ordering to Top, Center, Bottom, Left, Right —
`Cols > Column Info > Column Properties > Value Ordering`. Without it JMP sorts alphabetically and
the vertical profile plots as Bottom, Center, Left, Right, Top, which destroys the whole point of
the chart.

### Derived columns

| Column | Formula | Why |
|---|---|---|
| `WaferMean_A` | `Col Mean( :Thk_A, :Run, :Wafer )` | grouped mean without building a summary table |
| `Dev_A` | `:Thk_A - :WaferMean_A` | within-wafer deviation |
| `Dev_pct` | `100 * :Dev_A / :WaferMean_A` | same, scaled so both runs are comparable |
| `DG_Target_A` | Deal–Grove, see script | wet O₂ on Si (100), τ = 0 |
| `DG_Resid_pct` | `100*(:Thk_A - :DG_Target_A)/:DG_Target_A` | model residual |
| `Thk_norm` | `:Thk_A / :DG_Target_A` | **the trick that makes capability work** |

`Col Mean( x, g1, g2 )` is the single most useful function in this analysis. It's how you get
within-wafer statistics without a summary table round-trip.

**Why `Thk_norm` matters.** JMP stores spec limits as a *column property*, so one column gets one
set of limits. The two recipes have different targets (1353 Å and 6421 Å), so a raw-thickness
capability analysis needs two separate runs. Dividing by target puts both on a common scale where
the spec is 0.90 / 1.00 / 1.10 for everything, and Cp and Cpk are unchanged because dividing by a
per-run constant doesn't alter the ratio of tolerance to spread. One platform, both recipes,
directly comparable.

### Subsets

`Rows > Data Filter` on `MetrologyOK == 1`, then `Tables > Subset`. Repeat with
`MetrologyOK == 1 AND Flagged == 0` for the sensitivity case.

---

## Click-paths

**Variance components (route 1)**
`Analyze > Quality and Process > Variability / Attribute Gauge Chart`.
Y = `Thk_A`, X = `Run` then `Wafer` in that order. Chart Type = Variability.
Red triangle → `Variance Components`, model = **Nested**.

**Variance components (route 2 — the one with confidence intervals)**
`Analyze > Fit Model`. Y = `Thk_A`, add `Wafer`, then `Attributes > Random Effect`.
Put `Run` in the **By** box rather than the model, so you get a separate decomposition per run.
Personality: Standard Least Squares. Method: **REML**.
Read the REML Variance Component Estimates table. Residual = within-wafer.

Run both. Route 1 gives the percent-of-total table you'll put in the report; route 2 gives
the confidence intervals that tell you how much to trust it.

**Splitting the within-wafer term**
`Analyze > Fit Model`, Y = `Thk_A`, effects = `Wafer` and `FurnPos` (both fixed), By = `Run`.
The `FurnPos` sum of squares divided by the model SS for `Wafer + FurnPos` residual is the share of
within-wafer variation carried by the repeatable vertical signature.

**Uniformity**
`Tables > Summary`, Group = `Run`, `Slot`, statistics Mean / Std Dev / Min / Max / N.
Add the two non-uniformity formula columns, then `Analyze > Tabulate` to summarise by run.

**Furnace-frame profile**
`Graph > Graph Builder`. X = `Dev_pct`, Y = `FurnPos`, Overlay = `Run`.
Drop a Points element and a Caption Box set to Mean. Add a reference line at 0.

**Deal–Grove residuals**
Graph Builder, X = `Slot`, Y = `DG_Resid_pct`, Overlay = `Run`, reference line at 0.
Flat across slot means the offset is process-level, not a load effect — that's the read.

**Capability**
`Analyze > Quality and Process > Process Capability`. Process variable = `Thk_norm`
(limits come from the column property automatically). Subgroup ID = `Wafer`, By = `Run`.
Red triangle → check **Within Sigma Capability** and **Overall Sigma Capability** are both on.

> Set the within-sigma method to **Pooled Standard Deviation** (red triangle → `Set Within Sigma
> Method`). JMP's default varies by version, and only the pooled estimator equals √MSW, which is
> what the validation table below is computed against. If your Cp is close but not exact, this is
> almost always why.

**Control charts**
`Tables > Summary` grouped by `Run` and `Slot` to get wafer means, then
`Analyze > Quality and Process > Control Chart Builder`. Drag `Mean(Thk_A)` to Y, set chart type to
**Individual & Moving Range**, By = `Run`.
Red triangle → `Warnings > Tests` to enable Western Electric rules.

---

## Cross-validation targets

Metrology-clean primary set, 12 wafers per run, 60 measurements per run.

### Variance components (% of within-run total)

| Component | 900 °C | σ (Å) | 1100 °C | σ (Å) |
|---|---|---|---|---|
| Wafer-to-wafer | 60.6 % | 126.2 | 48.4 % | 60.5 |
| Within-wafer: vertical position | 28.6 % | 86.7 | 16.3 % | 35.1 |
| Within-wafer: residual | 10.8 % | 53.3 | 35.2 % | 51.6 |

Sensitivity case (A05 and A15 removed): 900 °C goes to 0.9 % / 80.8 % / 18.3 %,
1100 °C to 66.2 % / 23.3 % / 10.5 %. The 900 °C collapse is the finding.

### Uniformity

| Run | Mean range/2·mean | Mean 1σ/mean | Mean top−bottom |
|---|---|---|---|
| 900 °C | 13.08 % | 10.41 % | 25.01 % (222 Å) |
| 1100 °C | 1.17 % | 0.96 % | 2.25 % (95 Å) |

Top exceeds bottom in 12 of 12 wafers in both runs.

### Deal–Grove

| Run | Target (Å) | Measured (Å) | Ratio |
|---|---|---|---|
| 900 °C | 1352.9 | 904.1 | 0.668 |
| 1100 °C | 6421.1 | 4165.4 | 0.649 |

### Capability, ±10 % of target

| Run | Mean (Å) | σ within | σ overall | Cp | Cpk | Pp | Ppk |
|---|---|---|---|---|---|---|---|
| 900 °C | 904.1 | 101.8 | 158.8 | 0.44 | −1.03 | 0.28 | −0.66 |
| 1100 °C | 4165.4 | 62.4 | 85.4 | 3.43 | −8.62 | 2.51 | −6.29 |

### I–MR, wafer means in slot order

| Run | n | CL | UCL | LCL | M̄R | UCL(MR) | σ̂ = M̄R/1.128 |
|---|---|---|---|---|---|---|---|
| 900 °C | 12 | 904.1 | 1198.7 | 609.5 | 110.8 | 361.9 | 98.2 |
| 1100 °C | 12 | 4165.4 | 4285.1 | 4045.8 | 45.0 | 147.0 | 39.9 |

A15 falls beyond the UCL in both runs.

---

## Two things that will trip you up

**σ̂ from the moving range disagrees with the ANOVA wafer-to-wafer σ, and that's informative.**
At 900 °C the I–MR gives σ̂ = 98.2 Å while the REML wafer-to-wafer component is 126.2 Å. The moving
range only sees adjacent slots, so it estimates short-range variation and is deliberately blind to
a systematic trend across the boat. The ANOVA sees the whole spread. When the ANOVA estimate
exceeds the MR estimate, there is structure across the load — which is exactly what the two outlier
wafers and the slot trend are. Don't reconcile them; report both and explain the gap.

**Don't put `Run` in the model when you want per-run decomposition.** Putting it in as a fixed or
random effect gives one pooled within-wafer estimate across both temperatures, which is wrong here
because the two runs have wildly different within-wafer variance. Use the **By** box.
