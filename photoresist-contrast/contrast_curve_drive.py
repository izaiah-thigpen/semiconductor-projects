"""
Photoresist Contrast Curve & Parameter Extraction  —  reads the .xlsx from Google Drive.

Reconstructs the exposure dose for each step of an AZ1512 contrast sweep (evenly
spaced exposure times, step 12 = longest, at a fixed lamp intensity) and fits the
clearing transition to extract the resist contrast (gamma), the onset dose (Q0),
and the dose-to-clear (Qf = E0). Also reports coat uniformity and wafer-to-wafer
dose spread across every wafer that has a full sweep.

    pip install pandas openpyxl requests numpy matplotlib
    python contrast_curve_drive.py

The workbook must be shared "Anyone with the link".
Author: Izaiah Thigpen
"""
import io, re, requests, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec

DRIVE_LINK = "https://docs.google.com/spreadsheets/d/17Cyt2ZOpuD68XJhxqzqVIwUz_P3ccJsw/edit?usp=sharing"
I_MW_CM2 = 32.0                 # lamp intensity (mW/cm^2)
T_MAX_S  = 3.4                  # longest exposure, step 12 (s); steps evenly spaced
N_STEPS  = 12                   # dose steps per wafer
GOF_MIN  = 0.50                 # drop poor reflectometry fits
MIN_SWEEP = 11                  # keep wafers with at least this many valid steps

# ---------------------------------------------------------------- Google Drive
def file_id(link):
    m = re.search(r'/d/([A-Za-z0-9_-]+)', link) or re.search(r'[?&]id=([A-Za-z0-9_-]+)', link)
    return m.group(1) if m else link.strip()

def download(link):
    fid, s = file_id(link), requests.Session()
    url = "https://drive.google.com/uc?export=download"
    r = s.get(url, params={"id": fid}, timeout=30)
    tok = next((v for k, v in r.cookies.items() if k.startswith("download_warning")), None)
    if tok:
        r = s.get(url, params={"id": fid, "confirm": tok}, timeout=30)
    r.raise_for_status()
    if b'<html' in r.content[:200].lower():
        raise RuntimeError("Got an HTML page, not the file. Is it shared 'Anyone with the link'?")
    return io.BytesIO(r.content)

# ---------------------------------------------------------------- analysis
def dose(step):
    """UV dose (mJ/cm^2) for an evenly-spaced exposure step."""
    return I_MW_CM2 * (T_MAX_S * step / N_STEPS)

def read_sweeps(xls):
    """Return {wafer: {step: resist_thickness_um}} for the FM2 session.

    Sample-ID convention:  FM<session>_A<wafer>_<step>
    Session 1 (uncleared reference) is dropped; only wafers with a full sweep kept.
    """
    df = pd.read_excel(xls, sheet_name=0, header=8, engine="openpyxl")
    wafers = {}
    for _, row in df.iterrows():
        m = re.match(r'FM(\d+)_A(\d+)_(\d+)', str(row.get("Sample ID", "")))
        if not m:
            continue
        sess, waf, step = (int(x) for x in m.groups())
        l1 = pd.to_numeric(row.get("L1 d (um)"), errors="coerce")
        gof = pd.to_numeric(row.get("GOF"), errors="coerce")
        if sess == 1 or not np.isfinite(l1) or row.get("Valid") != 1:
            continue
        if np.isfinite(gof) and gof < GOF_MIN:
            continue
        wafers.setdefault(waf, {})[step] = float(l1)
    return {w: s for w, s in wafers.items() if len(s) >= MIN_SWEEP}

def fit_contrast(d, y):
    """Fit y = normalized thickness vs log10(dose) over the clearing transition.

    Returns gamma = -slope, onset dose Q0 (y=1) and dose-to-clear Qf/E0 (y=0).
    """
    floor = np.median(np.sort(y)[:4])            # cleared-film floor
    band = (y > floor + 0.08) & (y < 0.90)
    slope, b = np.polyfit(np.log10(d[band]), y[band], 1)
    return dict(gamma=-slope, Q0=10 ** ((1 - b) / slope),
                Qf=10 ** (-b / slope), slope=slope, b=b)

def d50(series):
    """Dose (mJ/cm^2) at 50% remaining thickness, interpolated (no extrapolation)."""
    ser = sorted(series.items())
    for (s1, y1), (s2, y2) in zip(ser, ser[1:]):
        if y1 >= 0.5 >= y2:
            f = (0.5 - y1) / (y2 - y1)
            return dose(s1 + f * (s2 - s1))
    return np.nan

# ---------------------------------------------------------------- main
def main():
    print("downloading workbook from Google Drive ...")
    xls = pd.ExcelFile(download(DRIVE_LINK), engine="openpyxl")
    sweeps = read_sweeps(xls)
    if not sweeps:
        raise SystemExit(f"No full contrast sweeps found. Sheets in file: {xls.sheet_names}")

    T0   = {w: max(s.values()) for w, s in sweeps.items()}
    norm = {w: {st: v / T0[w] for st, v in s.items()} for w, s in sweeps.items()}

    print(f"\n{'Wafer':7s} {'T0(um)':>7} {'D50(mJ/cm2)':>12}")
    D50 = {}
    for w in sorted(sweeps):
        D50[w] = d50(norm[w])
        print(f"A{w:<6d} {T0[w]:>7.3f} {D50[w]:>12.1f}")

    steps    = sorted({st for s in norm.values() for st in s})
    dose_arr = np.array([dose(st) for st in steps])
    dmean    = np.array([np.mean([norm[w][st] for w in norm if st in norm[w]]) for st in steps])
    fit      = fit_contrast(dose_arr, dmean)

    T0v, D50v = np.array(list(T0.values())), np.array(list(D50.values()))
    print(f"\ngamma = {fit['gamma']:.2f}     Q0 = {fit['Q0']:.1f} mJ/cm2     "
          f"E0 (dose-to-clear) = {fit['Qf']:.1f} mJ/cm2")
    print(f"coat uniformity  T0  = {T0v.mean():.3f} +/- {T0v.std():.3f} um "
          f"({100 * T0v.std() / T0v.mean():.1f}%)")
    print(f"wafer-to-wafer   D50 = {np.nanmean(D50v):.1f} +/- {np.nanstd(D50v):.1f} mJ/cm2")

    # ---- figure ----
    plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3})
    fig = plt.figure(figsize=(11, 4.4)); gs = gridspec.GridSpec(1, 2, wspace=.24)

    ax = fig.add_subplot(gs[0, 0])
    for w in sorted(norm):
        ser = sorted(norm[w].items())
        ax.plot([dose(st) for st, _ in ser], [y for _, y in ser], '-', color='#bbbbbb', lw=1)
    ax.plot(dose_arr, dmean, 'o-', color='#1f77b4', lw=1.8, ms=5,
            label=f"mean of {len(sweeps)} wafers")
    ax.axhline(0.5, ls=':', color='gray', lw=1)
    ax.set_xlim(0, None); ax.set_ylim(-0.05, 1.15)
    ax.set_xlabel('Exposure dose (mJ/cm$^2$)'); ax.set_ylabel('Normalized thickness  T/T$_0$')
    ax.set_title('(a) Contrast characteristic', loc='left', fontweight='bold'); ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[0, 1])
    ax.semilogx(dose_arr, dmean, 'o', color='#1f77b4', ms=5, label='mean data')
    xf = np.linspace(np.log10(fit['Q0']), np.log10(fit['Qf']), 50)
    ax.semilogx(10 ** xf, fit['slope'] * xf + fit['b'], '-', color='#c0392b', lw=1.6,
                label=f"fit: \u03b3 = {fit['gamma']:.2f}")
    for q, lbl, yy in [(fit['Q0'], 'Q0', 1.0), (fit['Qf'], 'Qf=E0', 0.0)]:
        ax.axvline(q, ls=':', color='#c0392b', lw=1, alpha=.6)
        ax.annotate(f"{lbl}\n{q:.0f}", (q, yy), fontsize=7, ha='center',
                    va='bottom' if yy else 'top', color='#c0392b')
    ax.set_ylim(-0.05, 1.15)
    ax.set_xlabel('Exposure dose (mJ/cm$^2$, log)'); ax.set_ylabel('Normalized thickness  T/T$_0$')
    ax.set_title('(b) Contrast fit: \u03b3 = 1/log\u2081\u2080(Qf/Q0)', loc='left', fontweight='bold')
    ax.legend(fontsize=7)

    fig.suptitle('Photoresist Contrast Curve & Parameter Extraction (AZ1512)',
                 fontweight='bold', y=1.01)
    fig.savefig('contrast_curve.png', dpi=150, bbox_inches='tight')
    print('\nsaved contrast_curve.png')

if __name__ == "__main__":
    main()
