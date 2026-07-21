"""
Thermal Oxidation Characterization  —  reads .xlsx runs directly from Google Drive.

Add a run by pasting its Drive share link (file must be shared "Anyone with the link").
No local files needed.

    pip install pandas openpyxl requests numpy matplotlib
    python oxide_drive_analysis.py

Author: Izaiah Thigpen
"""
import io, re, requests, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec

# ---- add / edit runs here: (label, temperature_C, Google Drive link or file ID) ----
RUNS = [
    ("900 C",  900,  "https://docs.google.com/spreadsheets/d/1yWJrouEeWHrYfEcgi06WQuWACzDAbWzo/edit?usp=sharing"),
    ("1100 C", 1100, "https://docs.google.com/spreadsheets/d/16eN1vAkdry1hCeeCIjOner0-ECUR712m/edit?usp=sharing"),
]
GOF_MIN, GOF_MAX = 0.98, 1.0          # keep valid fits only (reject bad + impossible GOF>1)
C, C2 = '#1a4f7a', '#c0392b'
ptp = lambda a: float(np.max(a) - np.min(a))

# ---------------------------------------------------------------- Google Drive
def file_id(link):
    m = re.search(r'/d/([A-Za-z0-9_-]+)', link) or re.search(r'[?&]id=([A-Za-z0-9_-]+)', link)
    return m.group(1) if m else link.strip()

def download(link):
    fid, s = file_id(link), requests.Session()
    url = "https://drive.google.com/uc?export=download"
    r = s.get(url, params={"id": fid}, timeout=30)
    tok = next((v for k, v in r.cookies.items() if k.startswith("download_warning")), None)
    if tok:                                   # large-file virus-scan confirm page
        r = s.get(url, params={"id": fid, "confirm": tok}, timeout=30)
    r.raise_for_status()
    if b'<html' in r.content[:200].lower():
        raise RuntimeError("Got an HTML page, not the file. Is it shared 'Anyone with the link'?")
    return io.BytesIO(r.content)

# ---------------------------------------------------------------- parse xlsx
def read_measurements(xbytes):
    raw = pd.read_excel(xbytes, header=None, engine="openpyxl")
    hdr = None
    for i in range(min(25, len(raw))):
        cells = [str(x).strip().lower() for x in raw.iloc[i].tolist()]
        if any('sample id' in c for c in cells) and any('gof' in c for c in cells):
            hdr = i
            break
    if hdr is None:
        raise ValueError("No data header row containing 'Sample ID' and 'GOF' was found.")
    cols = [str(x).strip() for x in raw.iloc[hdr].tolist()]
    data = raw.iloc[hdr + 1:].copy()
    data.columns = cols

    def col(names):
        for c in cols:
            cl = str(c).lower()
            if any(n in cl for n in names):
                return c
        return None
    c_thk = col(['l1 d', 'd (a', 'thick'])
    c_gof = col(['gof'])
    c_sid = col(['sample id', 'sample'])
    if not all([c_thk, c_gof, c_sid]):
        raise ValueError(f"Columns not found (thk={c_thk}, gof={c_gof}, sample={c_sid}). Columns are: {cols}")

    rows = []
    for _, r in data.iterrows():
        m = re.match(r'\s*A(\d+)_(\d+)', str(r[c_sid]))
        if not m:
            continue
        try:
            rows.append((int(m.group(1)), int(m.group(2)), float(r[c_thk]), float(r[c_gof])))
        except (ValueError, TypeError):
            continue
    return rows

# ---------------------------------------------------------------- stats
def stats(rows):
    clean = [r for r in rows if GOF_MIN <= r[3] <= GOF_MAX]
    t = np.array([r[2] for r in clean])
    wm, wiw = [], []
    for w in sorted({r[0] for r in clean}):
        tt = np.array([r[2] for r in clean if r[0] == w])
        wm.append(tt.mean()); wiw.append(100 * ptp(tt) / (2 * tt.mean()))
    wm = np.array(wm)
    return dict(n=len(clean), rej=len(rows) - len(clean), t=t, wm=wm,
                mean=t.mean(), stdp=100 * t.std(ddof=1) / t.mean(),
                wiwnu=float(np.mean(wiw)), w2w=100 * wm.std(ddof=1) / wm.mean())

# ---------------------------------------------------------------- run
def main():
    res = {}
    for label, T, link in RUNS:
        print(f"downloading {label} ...")
        res[T] = (label, stats(read_measurements(download(link))))

    print(f"\n{'run':>10} | {'n':>3} {'rej':>3} | {'mean(A)':>8} {'std%':>5} | {'WIWNU%':>6} {'W2W%':>5}")
    for T in sorted(res):
        lb, s = res[T]
        print(f"{lb:>10} | {s['n']:>3} {s['rej']:>3} | {s['mean']:>8.0f} {s['stdp']:>5.1f} | {s['wiwnu']:>6.1f} {s['w2w']:>5.1f}")

    Ts = sorted(res)
    if len(Ts) >= 2:
        lo, hi = Ts[0], Ts[-1]
        k = 8.617e-5
        Ea = k * np.log(res[hi][1]['mean'] / res[lo][1]['mean']) / (1/(lo+273.15) - 1/(hi+273.15))
        print(f"\n{res[lo][1]['mean']:.0f} -> {res[hi][1]['mean']:.0f} A "
              f"({res[hi][1]['mean']/res[lo][1]['mean']:.1f}x)  |  apparent Ea ~ {Ea:.2f} eV")

    # ---- figure ----
    plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': .3})
    fig = plt.figure(figsize=(11, 4.2)); gs = gridspec.GridSpec(1, 2, wspace=.26)
    cols = [C, C2, '#27ae60', '#8e44ad']

    ax = fig.add_subplot(gs[0, 0])
    for i, T in enumerate(Ts):
        lb, s = res[T]
        ax.hist(s['t'], bins=14, alpha=.7, color=cols[i % 4], edgecolor='w',
                label=f"{lb} (mean {s['mean']:.0f} A)")
    ax.set_title('(a) Thickness distribution', loc='left', fontweight='bold')
    ax.set_xlabel('Oxide thickness (A)'); ax.set_ylabel('count'); ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[0, 1])
    labels = ['Within-wafer', 'Wafer-to-wafer', 'Overall std']
    x = np.arange(len(labels)); w = .8 / max(len(Ts), 1)
    for i, T in enumerate(Ts):
        lb, s = res[T]
        vals = [s['wiwnu'], s['w2w'], s['stdp']]
        ax.bar(x + (i - (len(Ts)-1)/2) * w, vals, w, color=cols[i % 4], label=lb)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('%'); ax.set_title('(b) Variation by run', loc='left', fontweight='bold')
    ax.legend(fontsize=7)

    fig.suptitle('Thermal Oxidation Characterization  (from Google Drive)', fontweight='bold', y=1.02)
    fig.savefig('oxide_from_drive.png', dpi=150, bbox_inches='tight')
    print('\nsaved oxide_from_drive.png')


if __name__ == "__main__":
    main()
