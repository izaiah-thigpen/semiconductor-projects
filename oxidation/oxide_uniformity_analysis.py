"""
Thermal Oxide Uniformity & Process-Control Analysis
900 C / 60 min wet oxidation  |  16 wafers, 5-point maps (ellipsometry)

- Parses raw tool output (thickness + goodness-of-fit)
- Screens measurements by GOF to reject invalid fits
- Computes within-wafer non-uniformity (WIWNU), wafer-to-wafer (W2W) variation,
  center-vs-edge radial signature, and process capability (Cpk)
- Validates the mean oxide thickness against the Deal-Grove model
- Produces a 4-panel summary figure

Author: Izaiah Thigpen
"""
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

RAW = "ox.txt"            # tool export (text)
GOF_MIN = 0.98            # reject fits below this goodness-of-fit
TARGET, TOL = 900.0, 150.0   # example spec window (A): 900 +/- 150

# 5-point map geometry (from tool position key): 1=top 2=center 3=bottom 4=left 5=right
POS_XY = {1: (0, 1), 2: (0, 0), 3: (0, -1), 4: (-1, 0), 5: (1, 0)}

# ---------------------------------------------------------------- parse
def load(path):
    rows = []
    for ln in open(path):
        m = re.search(r'^\s*\d+\s+([\d.]+)\s+([\d.]+)\s+.*?(A\d+)_(\d+)\s+1\s+[0-9a-f-]+', ln)
        if m:
            rows.append(dict(
                wafer=int(m.group(3)[1:]), pos=int(m.group(4)),
                thk=float(m.group(1)), gof=float(m.group(2)),
                session='S1' if 'SiO2 on Si DWP' in ln else 'S2'))
    return rows

# ---------------------------------------------------------------- Deal-Grove
def deal_grove_wet(T_C=900.0, minutes=60.0, orientation=100):
    """Predicted oxide thickness (A) for wet oxidation via Deal-Grove."""
    k, T = 8.617e-5, T_C + 273.15
    B = 386 * np.exp(-0.78 / (k * T))                 # parabolic, um^2/hr
    BA = 9.7e7 * np.exp(-2.05 / (k * T))              # linear (111), um/hr
    if orientation == 100:
        BA /= 1.68
    A = B / BA
    t = minutes / 60.0
    x = (-A + np.sqrt(A * A + 4 * B * t)) / 2         # um
    return x * 1e4                                    # -> Angstrom

# ---------------------------------------------------------------- analysis
def main():
    rows = load(RAW)
    ptp = lambda a: float(np.max(a) - np.min(a))

    # --- GOF screening ---
    bad_session = sorted({r['wafer'] for r in rows if r['session'] == 'S2'})
    low_gof = [r for r in rows if r['session'] == 'S1' and r['gof'] < GOF_MIN]
    clean = [r for r in rows if r['session'] == 'S1' and r['gof'] >= GOF_MIN]
    t = np.array([r['thk'] for r in clean])

    print(f"Total measurements ............ {len(rows)}")
    print(f"Rejected (GOF>1 session) ...... {sum(r['session']=='S2' for r in rows)}  wafers {bad_session}")
    low_str = ", ".join("A{:02d}_{} ({:.0f}A, GOF {:.3f})".format(r['wafer'], r['pos'], r['thk'], r['gof']) for r in low_gof)
    print(f"Rejected (low-GOF outliers) ... {len(low_gof)}  [{low_str}]")
    print(f"Clean measurements ............ {len(clean)}\n")

    print(f"Mean {t.mean():.0f} A | Std {t.std(ddof=1):.0f} A ({100*t.std(ddof=1)/t.mean():.0f}%) "
          f"| Range {t.min():.0f}-{t.max():.0f} A")

    wafers = sorted({r['wafer'] for r in clean})
    wmean, wiwnu, ce = [], [], []
    for w in wafers:
        wr = [r for r in clean if r['wafer'] == w]
        tt = np.array([r['thk'] for r in wr])
        pos = {r['pos']: r['thk'] for r in wr}
        wmean.append(tt.mean())
        wiwnu.append(100 * ptp(tt) / (2 * tt.mean()))
        edges = [pos[p] for p in (1, 3, 4, 5) if p in pos]
        if 2 in pos and edges:
            ce.append(pos[2] - np.mean(edges))
    wmean = np.array(wmean)

    USL, LSL = TARGET + TOL, TARGET - TOL
    cpk = min(USL - t.mean(), t.mean() - LSL) / (3 * t.std(ddof=1))
    dg = deal_grove_wet()

    print(f"Within-wafer non-uniformity ... {np.mean(wiwnu):.1f}% (mean), up to {max(wiwnu):.1f}%")
    print(f"Wafer-to-wafer variation ...... {100*wmean.std(ddof=1)/wmean.mean():.1f}%")
    print(f"Center - edge (radial) ........ {np.mean(ce):+.0f} A ({100*np.mean(ce)/t.mean():+.1f}%)")
    print(f"Process capability Cpk ........ {cpk:.2f}  (spec {TARGET:.0f} +/- {TOL:.0f} A)")
    print(f"Deal-Grove predicted .......... {dg:.0f} A  vs measured {t.mean():.0f} A  ({100*abs(dg-t.mean())/dg:.1f}% diff)")

    # ------------------------------------------------------------ figure
    plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3})
    fig = plt.figure(figsize=(11, 7.2))
    gs = gridspec.GridSpec(2, 2, hspace=.34, wspace=.24)
    C = '#1a4f7a'

    # (a) wafer-mean control chart
    ax = fig.add_subplot(gs[0, 0])
    gm, sd = wmean.mean(), wmean.std(ddof=1)
    ax.axhspan(gm - 3*sd, gm + 3*sd, color=C, alpha=.06)
    ax.axhline(gm, color=C, lw=1.3)
    for k in (1, -1):
        ax.axhline(gm + 3*k*sd, color=C, ls='--', lw=.8)
    out = wmean > gm + 3*sd
    ax.plot(range(len(wafers)), wmean, 'o-', color=C, ms=5, lw=1)
    ax.plot(np.where(out)[0], wmean[out], 'o', color='#c0392b', ms=8, label='outlier')
    ax.set_xticks(range(len(wafers)))
    ax.set_xticklabels([f'A{w:02d}' for w in wafers], rotation=90, fontsize=7)
    ax.set_title('(a) Wafer-mean control chart', loc='left', fontweight='bold')
    ax.set_ylabel('Oxide thickness (A)')
    if out.any(): ax.legend(fontsize=7, loc='upper left')

    # (b) within-wafer non-uniformity
    ax = fig.add_subplot(gs[0, 1])
    ax.bar(range(len(wafers)), wiwnu, color=C, alpha=.8)
    ax.axhline(np.mean(wiwnu), color='#c0392b', ls='--', lw=1,
               label=f'mean {np.mean(wiwnu):.1f}%')
    ax.set_xticks(range(len(wafers)))
    ax.set_xticklabels([f'A{w:02d}' for w in wafers], rotation=90, fontsize=7)
    ax.set_title('(b) Within-wafer non-uniformity', loc='left', fontweight='bold')
    ax.set_ylabel('WIWNU  (range / 2·mean)  %')
    ax.legend(fontsize=7)

    # (c) center-vs-edge radial signature (avg over wafers, per position)
    ax = fig.add_subplot(gs[1, 0])
    posmean = {p: np.mean([r['thk'] for r in clean if r['pos'] == p]) for p in range(1, 6)}
    vals = np.array(list(posmean.values()))
    norm = plt.Normalize(vals.min(), vals.max())
    cmap = plt.cm.RdBu_r
    ax.add_patch(plt.Circle((0, 0), 1.4, fill=False, color='#333', lw=1.6))
    for p, (x, y) in POS_XY.items():
        ax.scatter(x, y, s=1700, c=[cmap(norm(posmean[p]))], edgecolors='#333', linewidths=1, zorder=3)
        ax.text(x, y, f'{posmean[p]:.0f}', ha='center', va='center', fontsize=9,
                fontweight='bold', color='#111', zorder=4)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=.045, pad=.04); cb.set_label('mean thk (A)', fontsize=7)
    cb.ax.tick_params(labelsize=6)
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('(c) Radial signature: mean thickness by position',
                 loc='left', fontweight='bold')
    ax.text(0, -1.85, f'center {posmean[2]:.0f} A  vs  edge {np.mean([posmean[p] for p in (1,3,4,5)]):.0f} A',
            ha='center', fontsize=7.5, color='#555')

    # (d) distribution + Deal-Grove + spec
    ax = fig.add_subplot(gs[1, 1])
    ax.hist(t, bins=14, color=C, alpha=.75, edgecolor='w')
    ax.axvline(t.mean(), color=C, lw=1.5, label=f'measured mean {t.mean():.0f} A')
    ax.axvline(dg, color='#27ae60', lw=1.5, ls='--', label=f'Deal-Grove {dg:.0f} A')
    ax.axvline(USL, color='#c0392b', lw=.9, ls=':'); ax.axvline(LSL, color='#c0392b', lw=.9, ls=':',
               label=f'spec {TARGET:.0f}\u00b1{TOL:.0f}')
    ax.set_title(f'(d) Thickness distribution  (Cpk {cpk:.2f})', loc='left', fontweight='bold')
    ax.set_xlabel('Oxide thickness (A)'); ax.set_ylabel('count')
    ax.legend(fontsize=7)

    fig.suptitle('Thermal Oxide Uniformity & Process Control  \u2014  900 \u00b0C / 60 min Wet Oxidation, 16 wafers',
                 fontweight='bold', fontsize=12, x=.5, y=.98)
    fig.savefig('oxide_analysis.png', dpi=150, bbox_inches='tight')
    print("\nsaved oxide_analysis.png")


if __name__ == "__main__":
    main()
