"""Back-test an engagement-only lead score against a fit + engagement + intent score (synthetic).

Fictional company Aurelis Life Sciences; contacts, behaviour and outcomes are simulated.
Questions answered:
  1. Does the old engagement-only score (MQL >= 15, SQL >= 30) predict who buys?
  2. Does a fit + engagement + intent score (0-100, split 55 / 25 / 20) do better?
  3. How should MQL and SQL thresholds be set, given sales capacity?
Run: python scripts/scoring_backtest.py      Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(31)
N = 30000

# ---------------- 1. synthetic contacts with a hidden buying propensity ----------------
SEG = {"Organ-on-chip": 1.0, "Cell therapy": 0.9, "Pharma": 0.7, "CRO": 0.5, "Academic": 0.4,
       "Hospital/core": 0.2, "Other": -0.3}
ROLE = {"PI/Director": 0.8, "Scientist": 0.6, "Procurement": 0.4, "Postdoc/Student": -0.2, "Other": -0.5}
AREA = {"Endothelial/vascular": 1.0, "Hematopoietic": 0.9, "Neural": 0.2, "Off-topic": -1.0}
df = pd.DataFrame({
    "segment": rng.choice(list(SEG), N, p=[.07, .09, .08, .08, .55, .05, .08]),
    "role": rng.choice(list(ROLE), N, p=[.15, .38, .06, .28, .13]),
    "area": rng.choice(list(AREA), N, p=[.2, .18, .17, .45]),
    "company_size": rng.choice(["1-10", "11-50", "51-500", "500+"], N, p=[.12, .18, .3, .4]),
    "past_buyer": rng.random(N) < .03,
})
fit_true = (df.segment.map(SEG) + df.role.map(ROLE) + df.area.map(AREA)
            + np.where(df.past_buyer, 1.2, 0) + np.where(df.company_size == "1-10", -0.8, 0))
hot = rng.random(N) < .07                                                         # a real timing signal is live
intent_true = rng.normal(0, 1, N) * .3 + np.where(hot, 2.0, 0)
eng_true = rng.normal(0, 1, N) * .6 + 0.7 * fit_true + 0.5 * hot                 # engagement follows fit and timing
logit = -5.5 + 1.0 * fit_true + 1.0 * intent_true + 0.25 * eng_true
p = 1 / (1 + np.exp(-logit))
df["bought"] = rng.random(N) < p                                                   # deal within 180 days

# observed behaviours (noisy, partly unrelated to buying)
df["email_opens"] = rng.poisson(np.clip(1.0 + 0.5 * eng_true, 0.05, None))          # inflated by scanners
df["email_clicks"] = rng.poisson(np.clip(0.12 + 0.12 * eng_true.clip(0), 0.01, None))
df["sales_replies"] = (rng.random(N) < (0.01 + 0.03 * hot + 0.01 * (fit_true > 1.5))).astype(int)
df["newsletter_forms"] = rng.poisson(0.08, N)
df["quote_forms"] = (rng.random(N) < (0.005 + 0.025 * hot)).astype(int)
df["blog_visits"] = rng.poisson(0.7, N)
df["pricing_visits"] = (rng.random(N) < (0.01 + 0.05 * hot)).astype(int)
df["seq_enrolled"] = rng.random(N) < 0.35                                           # our own action
df["called_by_us"] = rng.random(N) < 0.06                                           # our own action
df["new_grant"] = rng.random(N) < (0.03 + 0.05 * hot)
df["new_paper"] = rng.random(N) < (0.05 + 0.08 * hot)
df["competitor_domain"] = rng.random(N) < 0.02
df["student_only"] = (df.role == "Postdoc/Student") & (rng.random(N) < 0.6)

# ---------------- 2. OLD score: engagement only, as configured historically ----------------
def cap(x, c):
    return np.minimum(x, c)
old = (cap(df.email_opens * 1, 30) + cap(df.email_clicks * 6, 30)
       + cap(df.sales_replies * 20, 20) + cap(df.newsletter_forms * 10 + df.quote_forms * 10, 10)
       + cap(df.blog_visits * 2 + df.pricing_visits * 2, 5)
       + np.where(df.seq_enrolled, 5, 0) + np.where(df.called_by_us, 2, 0))
df["old_score"] = np.clip(old, 0, 100)

# ---------------- 3. NEW score: Buy-Readiness style, 0-100 ----------------
# company fit 0-30, contact fit 0-25, engagement 0-25, intent 0-20, plus hard rules
company_fit = (df.segment.map({"Organ-on-chip": 14, "Cell therapy": 13, "Pharma": 11, "CRO": 8, "Academic": 6,
                               "Hospital/core": 4, "Other": 0})
               + df.company_size.map({"1-10": 0, "11-50": 3, "51-500": 6, "500+": 7})
               + np.where(df.past_buyer, 9, 0)).clip(0, 30)
contact_fit = (df.role.map({"PI/Director": 12, "Scientist": 10, "Procurement": 7, "Postdoc/Student": 2, "Other": 0})
               + df.area.map({"Endothelial/vascular": 13, "Hematopoietic": 12, "Neural": 5, "Off-topic": 0})).clip(0, 25)
engagement = (cap(df.email_clicks * 6, 12) + cap(df.sales_replies * 12, 12)       # clicks and replies only
              + cap(df.newsletter_forms * 2, 3) + cap(df.blog_visits * 0.5, 2)).clip(0, 25)   # no opens, no own actions
intent = (np.where(df.pricing_visits > 0, 8, 0) + np.where(df.quote_forms > 0, 10, 0)
          + np.where(df.new_grant, 5, 0) + np.where(df.new_paper, 3, 0)).clip(0, 20)
df["new_score"] = (company_fit + contact_fit + engagement + intent).astype(float)
df["hand_raise"] = (df.sales_replies > 0) | (df.quote_forms > 0) | (df.pricing_visits > 0)
df["excluded"] = df.competitor_domain | df.student_only | (df.company_size == "1-10")
df.loc[df.excluded, "new_score"] = 0

def auc(score, y):
    r = pd.Series(score).rank(method="average").values
    n1, n0 = y.sum(), (~y).sum()
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
auc_old, auc_new = auc(df.old_score.values, df.bought.values), auc(df.new_score.values, df.bought.values)

# ---------------- 4. lifecycle definitions: old vs new ----------------
df["old_stage"] = np.select([df.old_score >= 30, df.old_score >= 15], ["SQL", "MQL"], "Lead")
SQL_CAP = 400                                                         # sales can work about this many per period
# SQL = a hand-raise from a good-fit contact, or a very high combined score; MQL = good fit with some interest
sql_new = ~df.excluded & ((df.hand_raise & (df.new_score >= 50)) | (df.new_score >= 65))
df["new_stage"] = "Lead"
df.loc[~df.excluded & (df.new_score >= 45), "new_stage"] = "MQL"
df.loc[sql_new, "new_stage"] = "SQL"

rows = []
for scheme, col in (("Old: engagement score", "old_stage"), ("New: fit + engagement + intent", "new_stage")):
    for st in ("Lead", "MQL", "SQL"):
        g = df[df[col] == st]
        rows.append(dict(scheme=scheme, stage=st, contacts=len(g), buyers=int(g.bought.sum()),
                         conversion=round(float(g.bought.mean()), 4) if len(g) else 0.0))
stage_tbl = pd.DataFrame(rows)
stage_tbl.to_csv(DATA / "stage_comparison.csv", index=False)
print(stage_tbl.to_string(index=False))
print(f"AUC old {auc_old:.3f} | new {auc_new:.3f}")
total_buyers = int(df.bought.sum())

# threshold sweep for the new score
sweep = []
for t in range(20, 61, 5):
    sel = df[df.new_score >= t]
    sweep.append(dict(threshold=t, contacts=len(sel), precision=round(float(sel.bought.mean()), 4),
                      recall=round(float(sel.bought.sum() / total_buyers), 3)))
sweep = pd.DataFrame(sweep)
sweep.to_csv(DATA / "threshold_sweep.csv", index=False)

# conversion by score band, old vs new
def band(s, edges):
    return pd.cut(s, edges, right=False)
ob = df.groupby(band(df.old_score, [0, 5, 15, 30, 101]), observed=True).bought.mean()
nb = df.groupby(band(df.new_score, [0, 25, 45, 60, 101]), observed=True).bought.mean()
df.drop(columns=[]).sample(2000, random_state=1).to_csv(DATA / "contacts_sample.csv", index=False)
pd.Series({"contacts": N, "buyers": total_buyers, "auc_old": round(auc_old, 3), "auc_new": round(auc_new, 3),
           "sql_capacity": SQL_CAP}).to_csv(DATA / "kpi_summary.csv", header=["value"])

# ---------------- 5. charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("Aurelis Life Sciences | Lead score back-test (synthetic data)", fontsize=13, weight="bold")

def roc(score, y):
    o = np.argsort(-score)
    ys = y[o]
    tpr = np.cumsum(ys) / ys.sum()
    fpr = np.cumsum(~ys) / (~ys).sum()
    return fpr[::200], tpr[::200]
for name, s, c in (("Old engagement score", df.old_score.values, RED), ("New fit + intent score", df.new_score.values, TEAL)):
    f, t = roc(s + rng.random(N) * 1e-6, df.bought.values)
    ax[0].plot(f, t, color=c, label=f"{name} (AUC {auc(s, df.bought.values):.2f})")
ax[0].plot([0, 1], [0, 1], color=GREY, ls="--", lw=.8)
ax[0].legend(fontsize=8, loc="lower right")
ax[0].set(title="Ranking power (ROC)", xlabel="false positive rate", ylabel="true positive rate")
w = .38
labels = ["Lead", "MQL", "SQL"]
oc = stage_tbl[stage_tbl.scheme.str.startswith("Old")].conversion.values * 100
nc = stage_tbl[stage_tbl.scheme.str.startswith("New")].conversion.values * 100
x = np.arange(3)
ax[1].bar(x - w / 2, oc, w, color=RED, label="Old")
ax[1].bar(x + w / 2, nc, w, color=TEAL, label="New")
ax[1].set_xticks(x, labels)
ax[1].legend(fontsize=8)
ax[1].set(title="Buy rate by lifecycle stage (%)", ylabel="% who bought in 180 days")
ax[2].plot(sweep.threshold, sweep.precision * 100, color=BLUE, marker="o", ms=3, label="Precision (%)")
ax2 = ax[2].twinx()
ax2.plot(sweep.threshold, sweep.recall * 100, color=GOLD, marker="o", ms=3, label="Recall (%)")
ax2.spines["top"].set_visible(False)
ax[2].set(title="Choosing a threshold (new score)", xlabel="score threshold", ylabel="precision %")
ax2.set_ylabel("recall %")
ax[2].axvline(45, color=GREY, ls=":")
ax[2].text(46, ax[2].get_ylim()[1] * .9, "MQL 45", fontsize=8)
vol = stage_tbl.pivot(index="stage", columns="scheme", values="contacts").reindex(["Lead", "MQL", "SQL"])
vol.columns = ["New", "Old"] if vol.columns[0].startswith("New") else ["Old", "New"]
ax[3].bar(x - w / 2, vol["Old"].replace(0, 1), w, color=RED, label="Old")
ax[3].bar(x + w / 2, vol["New"].replace(0, 1), w, color=TEAL, label="New")
ax[3].set_yscale("log")
ax[3].set_xticks(x, labels)
ax[3].legend(fontsize=8)
ax[3].set(title="Contacts per stage (log scale)", ylabel="contacts")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "scoring_backtest.png", dpi=130)
print("done")
