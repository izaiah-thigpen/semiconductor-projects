"""
Diode I-V Characterization & Parameter Extraction
Fits the Shockley diode equation to measured I-V sweeps to extract the ideality
factor (n) and saturation current (Is), the turn-on voltage, and series resistance
for several devices (silicon diode, Zener, and red/green/yellow LEDs).

    pip install pandas openpyxl numpy matplotlib
    python diode_iv_analysis.py

Data: MatE129_Group2_DiodeTesting.xlsx  (one sheet per device: columns VD, ID)
Author: Izaiah Thigpen
"""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec

XLSX = "MatE129_Group2_DiodeTesting.xlsx"
VT = 8.617e-5 * 300.15          # thermal voltage kT/q at ~27 C (V)
FIT_LO, FIT_HI = 1e-6, 5e-3     # current window for the exponential-region fit (A)

DEVICES = [                     # (sheet, label, color)
    ("DIODE",        "Si diode",     "#333333"),
    ("1N5234",       "1N5234 Zener",  "#8e44ad"),
    ("RED_LTL4223",  "Red LED",       "#c0392b"),
    ("DIODE_YELLOW", "Yellow LED",    "#d4ac0d"),
    ("DIODE_GREEN",  "Green LED",     "#27ae60"),
]

def read(sheet):
    df = pd.read_excel(XLSX, sheet_name=sheet, header=0, engine="openpyxl")
    V = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
    I = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
    m = np.isfinite(V) & np.isfinite(I)
    return V[m], I[m]

def extract(V, I):
    sel = (I > FIT_LO) & (I < FIT_HI) & (V > 0)
    slope, intercept = np.polyfit(V[sel], np.log(I[sel]), 1)
    n = 1.0 / (slope * VT)
    Is = np.exp(intercept)
    yhat = slope * V[sel] + intercept
    r2 = 1 - np.sum((np.log(I[sel]) - yhat) ** 2) / np.sum((np.log(I[sel]) - np.log(I[sel]).mean()) ** 2)
    fwd = I > 0
    Von = np.interp(1e-3, I[fwd], V[fwd])            # turn-on defined at 1 mA
    # crude series resistance from the top decade (deviation from ideal exponential)
    hi = (I > 1e-2)
    Rs = np.nan
    if hi.sum() >= 2:
        Videal = (np.log(I[hi]) - intercept) / slope
        Rs = np.median((V[hi] - Videal) / I[hi])
    return dict(n=n, Is=Is, Von=Von, r2=r2, Rs=Rs, slope=slope, intercept=intercept)

def main():
    rows = {}
    print(f"{'Device':16s} {'n':>5} {'Is (A)':>11} {'Von@1mA':>8} {'Rs(ohm)':>8} {'R^2':>7}")
    for sheet, label, _ in DEVICES:
        V, I = read(sheet); p = extract(V, I); rows[sheet] = (V, I, p)
        print(f"{label:16s} {p['n']:>5.2f} {p['Is']:>11.2e} {p['Von']:>7.3f}V {p['Rs']:>8.2f} {p['r2']:>7.4f}")

    plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3})
    fig = plt.figure(figsize=(11, 4.4)); gs = gridspec.GridSpec(1, 2, wspace=.24)

    # (a) linear forward I-V
    ax = fig.add_subplot(gs[0, 0])
    for sheet, label, col in DEVICES:
        V, I, p = rows[sheet]
        ax.plot(V, I * 1e3, '-', color=col, lw=1.4, label=f"{label}  (Von {p['Von']:.2f} V)")
    ax.set_xlim(0, None); ax.set_ylim(-2, 105)
    ax.set_xlabel('Forward voltage (V)'); ax.set_ylabel('Current (mA)')
    ax.set_title('(a) Forward I\u2013V', loc='left', fontweight='bold'); ax.legend(fontsize=7)

    # (b) semilog with Shockley fits
    ax = fig.add_subplot(gs[0, 1])
    for sheet, label, col in DEVICES:
        V, I, p = rows[sheet]
        fwd = I > 1e-9
        ax.semilogy(V[fwd], I[fwd], '.', color=col, ms=4, alpha=.6)
        vv = np.linspace(0, V[I > 0].max(), 100)
        ax.semilogy(vv, np.exp(p['slope'] * vv + p['intercept']), '-', color=col, lw=1.2,
                    label=f"{label}: n={p['n']:.2f}")
    ax.set_ylim(1e-9, 2e-1); ax.set_xlim(0, None)
    ax.set_xlabel('Forward voltage (V)'); ax.set_ylabel('Current (A, log)')
    ax.set_title('(b) Shockley fit: ln(I) = ln(Is) + V/(n\u00b7Vt)', loc='left', fontweight='bold')
    ax.legend(fontsize=7)

    fig.suptitle('Diode I\u2013V Characterization & Parameter Extraction', fontweight='bold', y=1.01)
    fig.savefig('diode_iv.png', dpi=150, bbox_inches='tight')
    print('\nsaved diode_iv.png')

if __name__ == "__main__":
    main()
