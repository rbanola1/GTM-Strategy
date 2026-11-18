"""Net-new lead generation pilot: suppress first, tier first, enrich last (fictional Aurelis Life Sciences).

Compares two ways to spend a fixed enrichment credit budget on 3,000 candidate contacts:
  A. "Enrich everything, filter later"
  B. "Suppress first, tier first, enrich only the best" (the pilot design)
Then forecasts replies with a Monte Carlo simulation and compares targeted vs bulk sending.
All numbers are synthetic. Run: python scripts/pilot_model.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(64)

N = 3000
BUDGET = 2000                                         # credits
COST = {"ai_fit_row": 1.15, "email_lookup": 1.4}      # measured on a 10-row test before scaling up
FIND_RATE = 0.84
BOUNCE_UNVERIFIED = 0.07

# ---------------- 1. candidate list from free searches ----------------
c = pd.DataFrame({"candidate_id": range(N)})
c["already_in_crm"] = rng.random(N) < .34
c["competitor"] = rng.random(N) < .04
c["small_company"] = rng.random(N) < .06
c["duplicate"] = rng.random(N) < .03
c["suppressed"] = c.already_in_crm | c.competitor | c.small_company | c.duplicate
c["tier"] = rng.choice(["A", "B", "C", "D"], N, p=[.14, .24, .38, .24])        # free signals: papers, grants, titles
c["true_fit"] = np.where(c.tier == "A", rng.random(N) < .8, np.where(c.tier == "B", rng.random(N) < .5,
                          np.where(c.tier == "C", rng.random(N) < .2, rng.random(N) < .05)))
c["has_email_findable"] = rng.random(N) < FIND_RATE

# ---------------- 2. strategies ----------------
def strategy_a():
    credits = 0.0
    out = []
    for _, r in c.iterrows():
        if credits + COST["ai_fit_row"] + COST["email_lookup"] > BUDGET:
            break
        credits += COST["ai_fit_row"] + COST["email_lookup"]
        out.append(r.candidate_id)
    sel = c[c.candidate_id.isin(out)]
    usable = sel[~sel.suppressed & sel.has_email_findable & sel.true_fit]
    return credits, len(sel), usable

def strategy_b():
    pool = c[~c.suppressed & c.tier.isin(["A", "B", "C"])].copy()          # suppress first, drop tier D
    credits = 0.0
    # AI fit check only on tier B and C; tier A is accepted on free signals
    check = pool[pool.tier != "A"]
    credits += len(check) * COST["ai_fit_row"]
    keep = pd.concat([pool[pool.tier == "A"], check[check.true_fit]])
    # enrich emails in priority order until the budget is spent
    keep = keep.sort_values("tier")
    n_afford = int((BUDGET - credits) // COST["email_lookup"])
    enriched = keep.head(n_afford)
    credits += len(enriched) * COST["email_lookup"]
    usable = enriched[enriched.has_email_findable]
    return credits, len(pool), usable
ca, na, ua = strategy_a()
cb, nb, ub = strategy_b()
summary = pd.DataFrame([
    dict(strategy="A. Enrich everything, filter later", rows_processed=na, credits_spent=round(ca),
         usable_leads=len(ua), tier_A_leads=int((ua.tier == "A").sum()), credits_per_usable_lead=round(ca / max(len(ua), 1), 1)),
    dict(strategy="B. Suppress first, tier first", rows_processed=nb, credits_spent=round(cb),
         usable_leads=len(ub), tier_A_leads=int((ub.tier == "A").sum()), credits_per_usable_lead=round(cb / max(len(ub), 1), 1)),
])
summary.to_csv(DATA / "strategy_comparison.csv", index=False)
ub.to_csv(DATA / "pilot_send_list.csv", index=False)
print(summary.to_string(index=False))

# ---------------- 3. funnel waterfall (strategy B) ----------------
steps = [("Candidates", N), ("After CRM suppression", int((~c.already_in_crm).sum())),
         ("After competitor, small-co, duplicate rules", int((~c.suppressed).sum())),
         ("Tiers A-C only", int(((~c.suppressed) & c.tier.isin(["A", "B", "C"])).sum())),
         ("Fit confirmed", len(ub) + int(round(len(ub) * (1 - FIND_RATE) / FIND_RATE))),
         ("Email found", len(ub))]
wf = pd.DataFrame(steps, columns=["step", "contacts"])
wf.to_csv(DATA / "funnel_waterfall.csv", index=False)

# ---------------- 4. Monte Carlo reply forecast ----------------
REPLY = {"A": (.04, .012), "B": (.02, .007), "C": (.006, .003)}     # mean, sd of true reply rate
sizes = ub.tier.value_counts().reindex(["A", "B", "C"]).fillna(0).astype(int)
sims = []
for _ in range(5000):
    total = 0
    for t, n in sizes.items():
        p = max(rng.normal(*REPLY[t]), 0.0005)
        total += rng.binomial(n, min(p, .5))
    sims.append(total)
sims = np.array(sims)
bulk = np.array([rng.binomial(len(ub), max(rng.normal(.0015, .0006), .0003)) for _ in range(5000)])
fc = pd.DataFrame({"scenario": ["Targeted, tiered send", "Bulk send to same size list"],
                   "mean_replies": [sims.mean().round(1), bulk.mean().round(1)],
                   "p10": [np.percentile(sims, 10), np.percentile(bulk, 10)],
                   "p90": [np.percentile(sims, 90), np.percentile(bulk, 90)],
                   "prob_at_least_5": [(sims >= 5).mean().round(2), (bulk >= 5).mean().round(2)]})
fc.round(1).to_csv(DATA / "reply_forecast.csv", index=False)
cpr = cb / max(sims.mean(), 1)
print(fc.round(1).to_string(index=False))
print(f"credits per expected reply: {cpr:.0f}")

# ---------------- 5. cost test: measure before scaling ----------------
test = pd.DataFrame({"action": ["Company and people search", "Suppression check against CRM", "AI fit score (per row)",
                                "Email lookup (per lookup)", "Verification"],
                     "credits_each": [0, 0, COST["ai_fit_row"], COST["email_lookup"], 0.0],
                     "note": ["Free preview; capped at 50 rows per table in a trial", "Local match, no credits",
                              "Run on tiers B and C only", "Waterfall of providers; cost rises with each fallback",
                              "Separate verifier for emails not found by the waterfall"]})
test.to_csv(DATA / "action_costs.csv", index=False)

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("Aurelis Life Sciences | Net-new lead generation pilot (synthetic data)", fontsize=13, weight="bold")
ax[0].barh(wf.step[::-1], wf.contacts[::-1], color=BLUE)
ax[0].set(title="Pilot funnel: suppress first", xlabel="contacts")
ax[0].tick_params(axis="y", labelsize=7)
x = np.arange(2)
ax[1].bar(x - .2, summary.credits_spent, .4, color=GREY, label="Credits spent")
ax[1].bar(x + .2, summary.usable_leads, .4, color=TEAL, label="Usable leads")
ax[1].set_xticks(x, ["A: enrich all", "B: suppress\nand tier first"])
ax[1].legend(fontsize=8)
ax[1].set(title="Same budget, different design")
for i, (cr, ul) in enumerate(zip(summary.credits_spent, summary.usable_leads)):
    ax[1].text(i - .2, cr + 20, str(cr), ha="center")
    ax[1].text(i + .2, ul + 20, str(ul), ha="center")
ax[2].hist(sims, bins=range(0, int(sims.max()) + 2), color=TEAL, alpha=.85, label="Targeted")
ax[2].hist(bulk, bins=range(0, int(sims.max()) + 2), color=RED, alpha=.7, label="Bulk")
ax[2].legend(fontsize=8)
ax[2].set(title="Forecast: replies from the send list", xlabel="replies", ylabel="simulations")
tiers = sizes
ax[3].bar(tiers.index, tiers.values, color=[TEAL, GOLD, GREY])
ax[3].set(title="Send list by tier", ylabel="contacts")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "pilot_overview.png", dpi=130)
print("done")
