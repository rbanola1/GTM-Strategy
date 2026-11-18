"""Synthetic fit x intent scoring and routing for a signal-based outbound GTM engine.

Company is fictional (Aurelis Life Sciences). All contacts, signals and outcomes are invented.
Run:  python scripts/score_and_route.py     (writes data/*.csv and charts/*.png)
Needs: pandas, numpy, matplotlib
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, CHARTS = ROOT / "data", ROOT / "charts"
DATA.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
N = 4000

# ---------------- 1. sources (synthetic contacts) ----------------
SEGMENTS = {"Organ-on-chip": .12, "Cell therapy developer": .14, "Pharma": .10, "CRO": .10,
            "Academic lab": .46, "Hospital / core": .05, "Other": .03}
ROLES = {"PI / Director": .20, "Scientist": .38, "Postdoc / Student": .27, "Procurement": .05, "Other": .10}
AREAS = {"Endothelial / vascular": .22, "Hematopoietic": .20, "Neural": .18, "Cardiac": .12,
         "Off-topic": .28}
SOURCES = {"CRM existing": .25, "Paper authors": .30, "Grant database": .15,
           "Website visitors": .15, "Event scans": .15}
REGIONS = {"US": .62, "EU": .22, "Asia": .12, "Other": .04}
SMALL_CO = rng.random(N) < 0.07     # companies already in CRM as tiny accounts
COMPETITOR = rng.random(N) < 0.03   # competitor domains

def pick(d, n=N):
    return rng.choice(list(d), n, p=np.array(list(d.values())) / sum(d.values()))

c = pd.DataFrame({
    "contact_id": [f"C{200000 + i}" for i in range(N)],
    "segment": pick(SEGMENTS), "role": pick(ROLES), "research_area": pick(AREAS),
    "source": pick(SOURCES), "region": pick(REGIONS),
    "past_buyer": rng.random(N) < 0.04,
    "small_company": SMALL_CO, "competitor_domain": COMPETITOR,
    "duplicate_in_crm": rng.random(N) < 0.18,
})

# ---------------- 2. clean and suppress ----------------
c["suppressed_reason"] = np.select(
    [c.competitor_domain, c.small_company, c.duplicate_in_crm & (c.source != "CRM existing")],
    ["competitor domain", "small company rule", "duplicate"], "")
active = c[c.suppressed_reason == ""].copy()

# ---------------- 3. score: fit (who) and intent (when) ----------------
FIT = {
    "segment": {"Organ-on-chip": 25, "Cell therapy developer": 22, "Pharma": 20, "CRO": 15,
                "Academic lab": 10, "Hospital / core": 8, "Other": 0},
    "role": {"PI / Director": 20, "Scientist": 15, "Postdoc / Student": 4, "Procurement": 10, "Other": 0},
    "research_area": {"Endothelial / vascular": 25, "Hematopoietic": 25, "Neural": 12,
                      "Cardiac": 10, "Off-topic": -15},
}
active["fit_score"] = (active.segment.map(FIT["segment"]) + active.role.map(FIT["role"])
                       + active.research_area.map(FIT["research_area"])
                       + np.where(active.past_buyer, 20, 0)
                       + np.where(active.region.isin(["US", "EU"]), 5, -5)).clip(0, 100)

SIGNALS = {  # signal: (probability, intent points)
    "new_paper_on_topic": (.10, 20), "new_grant": (.05, 25), "competitor_citation": (.04, 15),
    "pricing_page_visit": (.04, 30), "protocol_download": (.06, 20), "form_fill": (.02, 35),
    "email_reply": (.015, 40), "hiring_signal": (.03, 10),
}
active["intent_score"] = 0
for sig, (p, pts) in SIGNALS.items():
    hit = rng.random(len(active)) < p
    active[sig] = hit
    active["intent_score"] += hit * pts
active["intent_score"] = active.intent_score.clip(0, 100)

# ---------------- 4. route: fit x intent ----------------
FIT_HI, INTENT_HI = 50, 30
def lane(r):
    hi_fit, hi_int = r.fit_score >= FIT_HI, r.intent_score >= INTENT_HI
    return ("HOT: rep in 48h" if hi_fit and hi_int else "WARM: marketing nurture" if hi_fit
            else "CHECK: review by hand" if hi_int else "HOLD: not marketed")
active["lane"] = active.apply(lane, axis=1)

# ---------------- 5. outcomes (simulated) feed the measurement loop ----------------
REPLY = {"HOT: rep in 48h": .14, "WARM: marketing nurture": .04,
         "CHECK: review by hand": .05, "HOLD: not marketed": .004}
MEET = {"HOT: rep in 48h": .45, "WARM: marketing nurture": .20,
        "CHECK: review by hand": .15, "HOLD: not marketed": .05}
active["sent"] = active.lane != "HOLD: not marketed"
active["replied"] = active.sent & (rng.random(len(active)) < active.lane.map(REPLY))
active["meeting"] = active.replied & (rng.random(len(active)) < active.lane.map(MEET))

c.to_csv(DATA / "contacts_raw.csv", index=False)
active.to_csv(DATA / "contacts_scored_routed.csv", index=False)

summary = active.groupby("lane").agg(contacts=("contact_id", "count"), sent=("sent", "sum"),
                                     replies=("replied", "sum"), meetings=("meeting", "sum"))
summary["reply_rate"] = (summary.replies / summary.sent.replace(0, np.nan)).round(3)
summary.to_csv(DATA / "lane_summary.csv")
print("raw contacts:", len(c), "| suppressed:", int((c.suppressed_reason != "").sum()),
      "| active:", len(active))
print(c.suppressed_reason[c.suppressed_reason != ""].value_counts().to_string())
print(summary.to_string())

# measurement loop: reply rate with and without the signal, to re-weight intent points
rows = []
for sig in SIGNALS:
    s = active[active.sent]
    rows.append(dict(signal=sig, reply_with=s[s[sig]].replied.mean(), reply_without=s[~s[sig]].replied.mean()))
loop = pd.DataFrame(rows).assign(lift=lambda d: d.reply_with / d.reply_without).round(3)
loop.to_csv(DATA / "signal_lift.csv", index=False)

# ---------------- 6. charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"HOT: rep in 48h": "#D1495B", "WARM: marketing nurture": "#E9A23B",
       "CHECK: review by hand": "#2B5C9E", "HOLD: not marketed": "#9AA5B1"}
fig, ax = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Aurelis Life Sciences | Signal-based outbound engine (synthetic data)", fontsize=13, weight="bold")
for name, g in active.groupby("lane"):
    ax[0].scatter(g.intent_score + rng.normal(0, .6, len(g)), g.fit_score + rng.normal(0, .6, len(g)),
                  s=6, alpha=.5, color=COL[name], label=f"{name} ({len(g):,})")
ax[0].axvline(INTENT_HI, color="k", lw=.6, ls="--")
ax[0].axhline(FIT_HI, color="k", lw=.6, ls="--")
ax[0].set(xlabel="Intent score (timing)", ylabel="Fit score (who)", title="Fit x intent routing")
ax[0].legend(fontsize=7, loc="lower right", markerscale=2)
rr = summary.reply_rate.reindex(list(COL)).fillna(0) * 100
ax[1].bar([k.split(":")[0] for k in rr.index], rr.values, color=[COL[k] for k in rr.index])
ax[1].set(title="Reply rate by lane (%)", ylabel="%")
for i, v in enumerate(rr.values):
    ax[1].text(i, v + .2, f"{v:.1f}", ha="center")
l = loop.sort_values("lift")
ax[2].barh(l.signal, l.lift, color="#2A9D8F")
ax[2].axvline(1, color="k", lw=.6)
ax[2].set(title="Measurement loop: reply lift when signal present", xlabel="x times baseline")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "engine_overview.png", dpi=130)
print("done")
