"""GTM tool stack evaluation with weighted scoring and staged spend gates (fictional RB Tech).

Tools are generic categories with invented prices. The method: score each option against weighted criteria,
adopt only what solves a measured bottleneck, and release spend in stages behind gates.
Run: python scripts/tool_stack.py     Needs: pandas, numpy, matplotlib
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

W = {"Solves a measured bottleneck": 30, "Data quality": 20, "CRM integration": 15, "Cost": 15,
     "Effort to run": 10, "Risk (lock-in, compliance)": 10}
# scores 1-5 for each criterion
TOOLS = [
    # name, monthly cost, scores in the order of W, stage
    ("CRM scoring, workflows, sequences (existing)", 0, (5, 4, 5, 5, 4, 5), "Stage 1: Prove"),
    ("AI assistant for research, dedupe, drafting (existing)", 0, (5, 4, 4, 5, 4, 4), "Stage 1: Prove"),
    ("Academic contact and grant database (existing)", 0, (4, 3, 3, 5, 4, 4), "Stage 1: Prove"),
    ("Website and company intent data", 40, (4, 3, 5, 4, 3, 4), "Stage 1: Prove"),
    ("Enrichment waterfall platform", 190, (4, 5, 4, 3, 3, 4), "Stage 2: Scale data"),
    ("Email verification (pay as you go)", 35, (4, 5, 4, 5, 5, 5), "Stage 2: Scale data"),
    ("Social selling tool for two reps", 250, (3, 3, 3, 2, 4, 4), "Stage 3: Target system"),
    ("Workflow automation or scheduled agents", 20, (4, 4, 4, 4, 3, 3), "Stage 3: Target system"),
    ("Dedicated cold-email stack with new domains", 70, (2, 3, 2, 3, 2, 2), "Not recommended"),
    ("AI sales development agent", 300, (2, 2, 3, 1, 3, 2), "Not recommended"),
    ("Pharma intelligence feed", 500, (2, 4, 2, 1, 3, 3), "Not recommended"),
]
rows = []
wsum = sum(W.values())
for name, cost, sc, stage in TOOLS:
    score = sum(w * s for w, s in zip(W.values(), sc)) / (5 * wsum) * 100
    rows.append(dict(tool=name, monthly_cost=cost, weighted_score=round(score, 1), stage=stage,
                     **{k: v for k, v in zip(W, sc)}))
df = pd.DataFrame(rows).sort_values("weighted_score", ascending=False)
df.to_csv(DATA / "tool_scoring.csv", index=False)

# ---------------- staged budget with gates ----------------
stages = pd.DataFrame([
    ("Stage 1: Prove", "Now", "Existing tools only", 40, "Process, ICP, routing, baseline KPIs"),
    ("Stage 2: Scale data", "After gate", "Enrichment platform, verifier", 225, "About twice the targeted volume, industry contacts, signals"),
    ("Stage 3: Target system", "After gate", "Social selling for two reps, scheduled automation", 520, "Lists, enrichment and signals refresh automatically"),
], columns=["stage", "start", "adds", "monthly_spend", "unlocks"])
stages["cumulative_monthly"] = stages.monthly_spend
stages.to_csv(DATA / "stage_gates.csv", index=False)
gates = pd.DataFrame([
    ("Stage 1 to 2", "Targeted reply rate at least 1%", "Process works"),
    ("Stage 1 to 2", "Limit on volume is data: find rate under 60%, bounce over 2%, or industry roles missing", "Data is the bottleneck, not copy or reps"),
    ("Stage 1 to 2", "Reps have capacity to follow up more leads", "Capacity exists"),
    ("Stage 2 to 3", "Pipeline growing per lane", "Impact shown"),
    ("Stage 2 to 3", "Credits fully used and spend approved above the new-tools cap", "Budget approved"),
], columns=["transition", "gate", "why"])
gates.to_csv(DATA / "gates.csv", index=False)
print(df[["tool", "monthly_cost", "weighted_score", "stage"]].to_string(index=False))
print(stages[["stage", "monthly_spend"]].to_string(index=False))

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
COL = {"Stage 1: Prove": TEAL, "Stage 2: Scale data": GOLD, "Stage 3: Target system": BLUE, "Not recommended": GREY}
fig, ax = plt.subplots(1, 3, figsize=(17, 5.2))
fig.suptitle("RB Tech | GTM tool stack (synthetic data)", fontsize=13, weight="bold")
d = df.sort_values("weighted_score")
import textwrap
ax[0].barh([textwrap.fill(t, 34) for t in d.tool], d.weighted_score, color=[COL[s] for s in d.stage])
ax[0].set(title="Weighted score (0-100)", xlabel="score")
ax[0].tick_params(axis="y", labelsize=7)
for s, c in COL.items():
    sub = df[df.stage == s]
    ax[1].scatter(sub.monthly_cost, sub.weighted_score, s=90, color=c, label=s, edgecolor="k", lw=.4)
ax[1].legend(fontsize=7, loc="lower right")
ax[1].axvline(200, color="k", ls="--", lw=.7)
ax[1].text(205, 38, "new-tool\ncap $200", fontsize=7)
ax[1].set(title="Score vs monthly cost", xlabel="$ per month", ylabel="weighted score")
ax[2].bar(stages.stage.str.replace(": ", ":\n"), stages.monthly_spend, color=[TEAL, GOLD, BLUE])
for i, v in enumerate(stages.monthly_spend):
    ax[2].text(i, v + 10, f"${v}", ha="center")
ax[2].axhline(200, color="k", ls="--", lw=.7)
ax[2].set(title="Monthly new spend by stage (each behind a gate)", ylabel="$ per month")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "tool_stack.png", dpi=130)
print("done")
