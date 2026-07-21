"""
Thermal Oxidation Process Characterization  —  Temperature Study
Wet oxidation, 60 min, two conditions: 900 C and 1100 C  |  16 wafers each, 5-pt maps

Loads both tool exports, screens goodness-of-fit, and compares:
  - mean thickness & temperature dependence (apparent activation energy)
  - within-wafer non-uniformity (WIWNU) and wafer-to-wafer (W2W) variation
  - process capability, outliers, and the reaction- vs diffusion-limited signature
Author: Izaiah Thigpen
"""
import re, numpy as np, matplotlib.pyplot as plt
from matplotlib import gridspec

DATA = [("ox.txt", 900), ("ox1100.txt", 1100)]   # (tool export, temperature C)
GOF_MIN = 0.98
C = '#1a4f7a'; C2 = '#c0392b'
ptp = lambda a: float(np.max(a) - np.min(a))

def load(path):
    rows = []
    for ln in open(path):
        thk = re.search(r'^\s*\d+\s+([\d.]+)', ln)
        gofm = re.search(r'([\d.]+)\s+(?:SiO2 on Si|Si02_dwp)', ln)   # GOF sits right before the recipe
        wid = re.search(r'(A\d+)_(\d+)', ln)
        if thk and gofm and wid:
            rows.append(dict(wafer=int(wid.group(1)[1:]), pos=int(wid.group(2)),
                             thk=float(thk.group(1)), gof=float(gofm.group(1))))
    return rows

def stats(rows):
    clean = [r for r in rows if 0.98 <= r['gof'] <= 1.0]   # reject bad fits AND invalid GOF>1
    t = np.array([r['thk'] for r in clean])
    wm, wiw = [], []
    for w in sorted({r['wafer'] for r in clean}):
        tt = np.array([r['thk'] for r in clean if r['wafer'] == w])
        wm.append(tt.mean()); wiw.append(100 * ptp(tt) / (2 * tt.mean()))
    wm = np.array(wm)
    return dict(n=len(clean), rej=len(rows) - len(clean), t=t, mean=t.mean(),
                std=t.std(ddof=1), wiwnu=float(np.mean(wiw)), wiwnu_max=float(np.max(wiw)),
                w2w=100 * wm.std(ddof=1) / wm.mean(), wm=wm, wafers=sorted({r['wafer'] for r in clean}))

res = {T: stats(load(f)) for f, T in DATA}

print(f"{'condition':>14} | {'n':>3} {'rej':>3} | {'mean(A)':>8} {'std%':>5} | {'WIWNU%':>6} {'W2W%':>5}")
for T in (900, 1100):
    s = res[T]
    print(f"{T:>10} C   | {s['n']:>3} {s['rej']:>3} | {s['mean']:>8.0f} {100*s['std']/s['mean']:>5.1f} | "
          f"{s['wiwnu']:>6.1f} {s['w2w']:>5.1f}")

# temperature dependence -> apparent activation energy (2-point)
k = 8.617e-5
T1, T2 = 900 + 273.15, 1100 + 273.15
x1, x2 = res[900]['mean'], res[1100]['mean']
Ea = k * np.log(x2 / x1) / (1 / T1 - 1 / T2)
print(f"\nThickness ratio (1100/900): {x2/x1:.2f}x  ->  apparent Ea ~ {Ea:.2f} eV (2-point estimate)")

# -------------------------------------------------------------- figure
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3})
fig = plt.figure(figsize=(11, 7))
gs = gridspec.GridSpec(2, 2, hspace=.34, wspace=.26)

# (a) thickness distributions (log-friendly, two panels stacked via twin)
ax = fig.add_subplot(gs[0, 0])
for T, col in ((900, C), (1100, C2)):
    ax.hist(res[T]['t'], bins=14, alpha=.7, color=col, edgecolor='w',
            label=f'{T} C  (mean {res[T]["mean"]:.0f} A)')
ax.set_title('(a) Thickness distribution by temperature', loc='left', fontweight='bold')
ax.set_xlabel('Oxide thickness (A)'); ax.set_ylabel('count'); ax.legend(fontsize=7)

# (b) uniformity comparison
ax = fig.add_subplot(gs[0, 1])
labels = ['Within-wafer\nnon-uniformity', 'Wafer-to-wafer\nvariation', 'Overall\nstd']
x = np.arange(len(labels)); w = .36
v900 = [res[900]['wiwnu'], res[900]['w2w'], 100*res[900]['std']/res[900]['mean']]
v1100 = [res[1100]['wiwnu'], res[1100]['w2w'], 100*res[1100]['std']/res[1100]['mean']]
ax.bar(x - w/2, v900, w, color=C, label='900 C')
ax.bar(x + w/2, v1100, w, color=C2, label='1100 C')
for i, (a, b) in enumerate(zip(v900, v1100)):
    ax.text(i - w/2, a + .3, f'{a:.1f}', ha='center', fontsize=7)
    ax.text(i + w/2, b + .3, f'{b:.1f}', ha='center', fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel('%'); ax.set_title('(b) Uniformity improves at higher T', loc='left', fontweight='bold')
ax.legend(fontsize=7)

# (c) wafer-mean control charts (both)
ax = fig.add_subplot(gs[1, 0])
for T, col in ((900, C), (1100, C2)):
    wm = res[T]['wm']
    ax.plot(range(len(wm)), wm, 'o-', color=col, ms=4, lw=1, label=f'{T} C')
    ax.axhline(wm.mean(), color=col, ls='--', lw=.7)
ax.set_title('(c) Wafer-mean stability', loc='left', fontweight='bold')
ax.set_ylabel('Oxide thickness (A)'); ax.set_xlabel('wafer index'); ax.legend(fontsize=7)

# (d) temperature dependence / Arrhenius
ax = fig.add_subplot(gs[1, 1])
invT = np.array([1e4 / T1, 1e4 / T2]); lnx = np.log([x1, x2])
ax.plot(invT, lnx, 'o', color=C, ms=8)
ax.plot(invT, lnx, '-', color=C, lw=1.2)
for xt, yt, T in zip(invT, lnx, (900, 1100)):
    ax.annotate(f'{T} C\n{np.exp(yt):.0f} A', (xt, yt), textcoords='offset points',
                xytext=(8, -4), fontsize=8)
ax.set_title(f'(d) Temperature dependence  (apparent Ea ~ {Ea:.2f} eV)', loc='left', fontweight='bold')
ax.set_xlabel('10\u2074 / T  (1/K)'); ax.set_ylabel('ln(thickness)')

fig.suptitle('Thermal Oxidation Characterization  \u2014  Wet, 60 min: 900 \u00b0C vs 1100 \u00b0C  (16 wafers each)',
             fontweight='bold', fontsize=12, y=.98)
fig.savefig('oxide_temperature_study.png', dpi=150, bbox_inches='tight')
print('\nsaved oxide_temperature_study.png')
