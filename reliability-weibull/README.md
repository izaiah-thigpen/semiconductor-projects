# Reliability Life-Data Analysis (Censored Weibull)

Fits a Weibull life distribution to device time-to-failure data with right-censoring.

**Highlights**
- Maximum-likelihood Weibull fit with 60% right-censored (surviving) units handled correctly: β = 1.86 (wear-out), η = 181 hrs, MTTF 161 hrs, B10 54 hrs.
- Validated against a nonparametric Kaplan–Meier estimate; Weibull chosen over lognormal by AIC.
- Failure-mode breakdown (battery / CPU / network / overheat).

**Files**
- `device_reliability_weibull.py` — local-file version
- `device_reliability_drive.py` — reads the dataset from Google Drive
- `device_reliability.png` — reliability, probability plot, hazard, failure modes
- `Reliability_Weibull_Report.pdf` — one-page report

Run: `pip install pandas numpy scipy matplotlib requests` then `python device_reliability_drive.py`
