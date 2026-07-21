"""
Statistical Process Control (SPC) & Yield-Excursion Analysis
5,000-wafer semiconductor process dataset: parameter control charts, out-of-control
detection, and correlation of the rare defects with process-window excursions.

    pip install pandas numpy matplotlib
    python wafer_spc_analysis.py

Data: semiconductor_wafer_defect_dataset.csv
Author: Izaiah Thigpen
"""
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

CSV = "semiconductor_wafer_defect_dataset.csv"
PARAMS = ["temperature_c", "pressure_torr", "gas_flow_sccm",
          "etch_rate_nm_min", "voltage_v", "current_ma"]
NICE = {"temperature_c":"Temperature (\u00b0C)","pressure_torr":"Pressure (Torr)",
        "gas_flow_sccm":"Gas flow (sccm)","etch_rate_nm_min":"Etch rate (nm/min)",
        "voltage_v":"Voltage (V)","current_ma":"Current (mA)"}
D2 = 1.128   # SPC constant for moving-range of n=2

def imr_limits(x):
    """Individuals (I-MR) control limits: center +/- 3*sigma, sigma from mean moving range."""
    mr = np.abs(np.diff(x))
    sigma = mr.mean() / D2
    mu = x.mean()
    return mu, sigma, mu - 3*sigma, mu + 3*sigma

def main():
    df = pd.read_csv(CSV)
    defect = df["defect_label"].astype(bool).values
    n_def = int(defect.sum())
    print(f"{len(df)} wafers | defect rate {100*defect.mean():.2f}% ({n_def} defects)\n")

    # --- control limits + out-of-control counts ---
    lims = {}
    print(f"{'Parameter':17s} {'mean':>9} {'sigma':>8} {'LCL':>9} {'UCL':>9} {'#OOC':>5}")
    for c in PARAMS:
        mu, sig, lcl, ucl = imr_limits(df[c].values)
        ooc = int(np.sum((df[c] < lcl) | (df[c] > ucl)))
        lims[c] = (mu, sig, lcl, ucl)
        print(f"{c:17s} {mu:9.2f} {sig:8.3f} {lcl:9.2f} {ucl:9.2f} {ooc:5d}")

    # --- defect excursion fingerprint (z-score of defect wafers per parameter) ---
    print("\nDefect-wafer excursion fingerprint (mean z-score vs population):")
    zbar = {}
    for c in PARAMS:
        z = (df.loc[defect, c] - df[c].mean()) / df[c].std()
        zbar[c] = z.mean()
        print(f"  {c:17s} {zbar[c]:+.2f}")

    # ---------------- figure ----------------
    plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.3})
    fig = plt.figure(figsize=(11,7)); gs = gridspec.GridSpec(2,2,hspace=.32,wspace=.24)
    C, RED = '#1a4f7a', '#c0392b'
    idx = np.arange(len(df))

    def ichart(ax, c, title):
        mu, sig, lcl, ucl = lims[c]
        ax.scatter(idx, df[c], s=3, color='#b8c4d0', alpha=.5, linewidths=0)
        ax.axhline(mu, color=C, lw=1); ax.axhline(ucl, color=RED, ls='--', lw=.9)
        ax.axhline(lcl, color=RED, ls='--', lw=.9)
        ax.scatter(idx[defect], df[c][defect], s=42, color=RED, edgecolors='k',
                   linewidths=.5, zorder=5, label=f'defect (n={n_def})')
        ax.set_title(title, loc='left', fontweight='bold')
        ax.set_xlabel('wafer #'); ax.set_ylabel(NICE[c]); ax.legend(fontsize=7, loc='upper right')

    ichart(fig.add_subplot(gs[0,0]), 'pressure_torr', '(a) Pressure control chart')
    ichart(fig.add_subplot(gs[0,1]), 'temperature_c', '(b) Temperature control chart')

    # (c) excursion fingerprint
    ax = fig.add_subplot(gs[1,0])
    vals = [zbar[c] for c in PARAMS]
    cols = [RED if abs(v) >= 1 else C for v in vals]
    ax.barh(range(len(PARAMS)), vals, color=cols)
    ax.axvline(0, color='#333', lw=.8)
    for s in (2,-2): ax.axvline(s, color=RED, ls=':', lw=.7)
    ax.set_yticks(range(len(PARAMS))); ax.set_yticklabels([NICE[c] for c in PARAMS], fontsize=8)
    ax.set_xlabel('mean z-score of defect wafers'); ax.invert_yaxis()
    ax.set_title('(c) Defect excursion fingerprint', loc='left', fontweight='bold')

    # (d) process-window scatter
    ax = fig.add_subplot(gs[1,1])
    ax.scatter(df['pressure_torr'][~defect], df['etch_rate_nm_min'][~defect],
               s=5, color='#b8c4d0', alpha=.4, linewidths=0, label='pass')
    ax.scatter(df['pressure_torr'][defect], df['etch_rate_nm_min'][defect],
               s=55, color=RED, edgecolors='k', linewidths=.5, label='defect')
    ax.set_xlabel(NICE['pressure_torr']); ax.set_ylabel(NICE['etch_rate_nm_min'])
    ax.set_title('(d) Process window: defects cluster at\nlow pressure / high etch rate',
                 loc='left', fontweight='bold', fontsize=9)
    ax.legend(fontsize=7)

    fig.suptitle('Wafer Process SPC & Yield-Excursion Analysis  (5,000 wafers)',
                 fontweight='bold', y=.98)
    fig.savefig('wafer_spc.png', dpi=150, bbox_inches='tight')
    print("\nsaved wafer_spc.png")

if __name__ == "__main__":
    main()
