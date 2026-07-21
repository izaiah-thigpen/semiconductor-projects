"""
Reliability / Life-Data Analysis with Censoring  —  IoT device failures
Fits a Weibull life distribution (with right-censoring) to device time-to-failure,
compares it against a lognormal fit, overlays a nonparametric Kaplan-Meier estimate,
and extracts reliability metrics (characteristic life, MTTF, B10) and the hazard trend.

    pip install pandas numpy scipy matplotlib
    python device_reliability_weibull.py

Data: IoT_Failure_Prediction_Dataset.csv
  time  = Uptime (hrs)
  event = Failure_Type > 0  (1..4 = battery/CPU/network/overheat failure; 0 = Normal -> censored)
Author: Izaiah Thigpen
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy import stats
from math import gamma
import matplotlib.pyplot as plt
from matplotlib import gridspec

CSV = "IoT_Failure_Prediction_Dataset.csv"
MODES = {1:"Battery", 2:"CPU", 3:"Network", 4:"Overheat"}

def load():
    df = pd.read_csv(CSV); df.columns = [c.strip() for c in df.columns]
    t = np.maximum(df["Uptime (hrs)"].values.astype(float), 0.1)
    ft = df["Failure_Type"].values
    event = (ft > 0).astype(int)
    return t, event, ft

# ---------- censored MLE fits ----------
def weibull_mle(t, event):
    def nll(p):
        k, lam = p
        if k <= 0 or lam <= 0: return 1e12
        z = t/lam
        logf = np.log(k/lam) + (k-1)*np.log(z) - z**k
        logS = -z**k
        return -(event*logf + (1-event)*logS).sum()
    r = minimize(nll, [2, np.median(t)], method="Nelder-Mead")
    return r.x[0], r.x[1], -r.fun

def lognormal_mle(t, event):
    def nll(p):
        mu, s = p
        if s <= 0: return 1e12
        z = (np.log(t)-mu)/s
        logf = -np.log(t*s*np.sqrt(2*np.pi)) - 0.5*z**2
        logS = np.log(np.clip(1-stats.norm.cdf(z), 1e-12, 1))
        return -(event*logf + (1-event)*logS).sum()
    r = minimize(nll, [np.log(np.median(t)), 0.5], method="Nelder-Mead")
    return r.x[0], r.x[1], -r.fun

# ---------- Kaplan-Meier (nonparametric survival) ----------
def kaplan_meier(t, event):
    order = np.argsort(t); t, event = t[order], event[order]
    times = np.unique(t[event==1])
    S = 1.0; xs=[0]; ys=[1.0]
    for tt in times:
        n_risk = np.sum(t >= tt)
        d = np.sum((t==tt) & (event==1))
        S *= (1 - d/n_risk)
        xs.append(tt); ys.append(S)
    return np.array(xs), np.array(ys)

def main():
    t, event, ft = load()
    nf, nc = int(event.sum()), int((1-event).sum())
    print(f"n={len(t)} | failures={nf} | censored={nc} ({100*nc/len(t):.0f}%)\n")

    k, lam, llw = weibull_mle(t, event)
    mu, s, lll = lognormal_mle(t, event)
    mttf = lam*gamma(1+1/k); B10 = lam*(-np.log(0.9))**(1/k); B50 = lam*(np.log(2))**(1/k)
    aic_w, aic_l = 2*2-2*llw, 2*2-2*lll
    print(f"WEIBULL   beta={k:.3f}  eta={lam:.1f} hrs | MTTF={mttf:.1f} | B10={B10:.1f} | AIC={aic_w:.0f}")
    print(f"LOGNORMAL mu={mu:.3f}  sigma={s:.3f} | median={np.exp(mu):.1f} hrs | AIC={aic_l:.0f}")
    print(f"Preferred (lower AIC): {'Weibull' if aic_w<aic_l else 'Lognormal'}\n")

    tt = np.linspace(1, t.max(), 400)
    Rw = np.exp(-(tt/lam)**k)                                  # Weibull reliability
    Rl = 1-stats.norm.cdf((np.log(tt)-mu)/s)                   # Lognormal reliability
    hz = (k/lam)*(tt/lam)**(k-1)                               # Weibull hazard
    kmx, kmy = kaplan_meier(t, event)

    plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.3})
    fig = plt.figure(figsize=(11,7)); gs = gridspec.GridSpec(2,2,hspace=.32,wspace=.24)
    C, RED, GRN = '#1a4f7a', '#c0392b', '#27ae60'

    # (a) reliability: KM vs fitted models
    ax = fig.add_subplot(gs[0,0])
    ax.step(kmx, kmy, where='post', color='#888', lw=1.4, label='Kaplan-Meier (data)')
    ax.plot(tt, Rw, color=C, lw=1.8, label=f'Weibull (\u03b2={k:.2f}, \u03b7={lam:.0f})')
    ax.plot(tt, Rl, color=RED, lw=1.2, ls='--', label='Lognormal')
    ax.set_xlabel('Time (hrs)'); ax.set_ylabel('Reliability  R(t)')
    ax.set_title('(a) Reliability: model vs Kaplan-Meier', loc='left', fontweight='bold')
    ax.legend(fontsize=7)

    # (b) Weibull probability plot
    ax = fig.add_subplot(gs[0,1])
    kmx2, kmy2 = kaplan_meier(t, event); F = 1-kmy2[1:]; xt = kmx2[1:]
    good = (F>0)&(F<1)
    ax.plot(np.log(xt[good]), np.log(-np.log(1-F[good])), 'o', color=C, ms=3, label='data (KM)')
    xs = np.log(np.array([xt[good].min(), xt[good].max()]))
    ax.plot(xs, k*xs - k*np.log(lam), color=RED, lw=1.4, label=f'Weibull fit (\u03b2={k:.2f})')
    ax.set_xlabel('ln(time)'); ax.set_ylabel('ln(-ln(1-F))')
    ax.set_title('(b) Weibull probability plot', loc='left', fontweight='bold'); ax.legend(fontsize=7)

    # (c) hazard (wear-out)
    ax = fig.add_subplot(gs[1,0])
    ax.plot(tt, hz*1000, color=C, lw=1.8)
    ax.fill_between(tt, hz*1000, color=C, alpha=.1)
    ax.set_xlabel('Time (hrs)'); ax.set_ylabel('Hazard rate  (per 1000 hrs)')
    ax.set_title(f'(c) Hazard is increasing (\u03b2={k:.2f} > 1 \u2192 wear-out)', loc='left', fontweight='bold')

    # (d) failure-mode breakdown
    ax = fig.add_subplot(gs[1,1])
    names=[MODES[m] for m in (1,2,3,4)]; cnts=[int(np.sum(ft==m)) for m in (1,2,3,4)]
    mean_ttf=[t[ft==m].mean() for m in (1,2,3,4)]
    b=ax.bar(names, cnts, color=C, alpha=.85)
    ax.set_ylabel('failure count'); ax.set_title('(d) Failure modes (count; mean TTF hrs)', loc='left', fontweight='bold')
    for rect,mt in zip(b,mean_ttf):
        ax.text(rect.get_x()+rect.get_width()/2, rect.get_height()+4, f'{mt:.0f}h', ha='center', fontsize=8, color='#333')
    ax.set_ylim(0, max(cnts)*1.2)

    fig.suptitle(f'Device Reliability \u2014 Censored Weibull Life-Data Analysis  '
                 f'({nf} failures, {nc} censored)', fontweight='bold', y=.98)
    fig.savefig('device_reliability.png', dpi=150, bbox_inches='tight')
    print("saved device_reliability.png")

if __name__ == "__main__":
    main()
