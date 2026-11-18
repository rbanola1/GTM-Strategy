"""Build ICP cards from synthetic won/lost deals and simulate nurture tracks (fictional Aurelis Life Sciences).

1. Profile 360 closed deals by segment, role, organisation size and product to find who buys.
2. Turn the pattern into ICP cards and account tiers (A / B / C).
3. Simulate three product nurture tracks with entry, engagement, promotion and exit rules.
Run: python scripts/icp_and_nurture.py       Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(21)

# ---------------- 1. closed deals ----------------
N = 360
SEG = {"Academic / research hospital / gov lab": ("Lab buyer", .44), "Therapeutic biotech / pharma": ("Programme buyer", .22),
       "Organ-on-chip developer": ("Programme buyer", .12), "CRO / CDMO": ("Service buyer", .12), "Tools and other": ("Other", .10)}
ROLES = {"PI / professor": .15, "Scientist / lab manager": .32, "Postdoc": .13, "Director / VP science": .10,
         "Founder / C-level": .17, "BD / commercial": .08, "Procurement": .05}
PRODUCT = {"Endothelial cells": .35, "Progenitor cells": .30, "Small molecules": .25, "Media kits": .10}
SIZE = {"1-10": .18, "11-250": .30, "251-5K": .22, "5K+": .30}
d = pd.DataFrame({
    "segment": rng.choice(list(SEG), N, p=[v[1] for v in SEG.values()]),
    "role": rng.choice(list(ROLES), N, p=list(ROLES.values())),
    "product": rng.choice(list(PRODUCT), N, p=list(PRODUCT.values())),
    "size": rng.choice(list(SIZE), N, p=list(SIZE.values())),
})
base = -1.4
seg_eff = {"Academic / research hospital / gov lab": .5, "Therapeutic biotech / pharma": .1, "Organ-on-chip developer": .55,
           "CRO / CDMO": -.1, "Tools and other": -.6}
role_eff = {"PI / professor": .9, "Scientist / lab manager": .6, "Postdoc": .3, "Director / VP science": .0,
            "Founder / C-level": -.4, "BD / commercial": -1.2, "Procurement": .0}
size_eff = {"1-10": -.9, "11-250": -.1, "251-5K": 0, "5K+": .7}
logit = base + d.segment.map(seg_eff) + d.role.map(role_eff) + d["size"].map(size_eff)
d["won"] = rng.random(N) < 1 / (1 + np.exp(-logit))
price = {"Endothelial cells": 3200, "Progenitor cells": 2600, "Small molecules": 450, "Media kits": 900}
d["amount"] = np.where(d.won, d["product"].map(price) * rng.lognormal(0, .5, N) *
                       np.where(d.segment.isin(["Therapeutic biotech / pharma", "Organ-on-chip developer"]), 3.2, 1), 0).round(-1)
d.to_csv(DATA / "closed_deals.csv", index=False)

def rate(col):
    g = d.groupby(col).agg(deals=("won", "size"), won=("won", "sum"), avg_won_amount=("amount", lambda x: x[x > 0].mean()))
    g["win_rate"] = (g.won / g.deals).round(3)
    return g.sort_values("win_rate", ascending=False).round(0)
seg_t, role_t, size_t = rate("segment"), rate("role"), rate("size")
seg_t.to_csv(DATA / "win_rate_by_segment.csv")
role_t.to_csv(DATA / "win_rate_by_role.csv")
size_t.to_csv(DATA / "win_rate_by_size.csv")

# ---------------- 2. account tiers ----------------
def tier(r):
    pts = seg_eff[r.segment] + role_eff[r.role] + size_eff[r["size"]]
    return "A" if pts >= 1.6 else "B" if pts >= .7 else "C"
d["tier"] = d.apply(tier, axis=1)
tt = d.groupby("tier").agg(deals=("won", "size"), win_rate=("won", "mean"),
                           avg_deal=("amount", lambda x: x[x > 0].mean())).round(2)
tt.to_csv(DATA / "tier_performance.csv")
print(tt.to_string())

# ---------------- 3. nurture simulation ----------------
TRACKS = {"Endothelial": 2400, "Progenitor": 1800, "Small molecules": 3000}
WEEKS = 16
rows = []
for track, n in TRACKS.items():
    fit_ok = rng.random(n) < .55                              # entry rule: fit score passes
    engaged = np.zeros(n)
    promoted = np.zeros(n, bool)
    exited = np.zeros(n, bool)
    for w in range(WEEKS):
        active = fit_ok & ~promoted & ~exited
        click = (rng.random(n) < (0.05 if track != "Small molecules" else 0.07)) & active
        visit = (rng.random(n) < .015) & active
        engaged += click * 5 + visit * 8
        handraise = (rng.random(n) < .004) & active          # reply, quote, sample request
        promoted |= handraise | (engaged >= 30)
        exited |= (active & (w >= 10) & (engaged < 5) & (rng.random(n) < .12))   # no engagement after 10 weeks
        rows.append(dict(track=track, week=w + 1, in_track=int(active.sum()), promoted_total=int(promoted.sum()),
                         exited_total=int(exited.sum())))
nur = pd.DataFrame(rows)
nur.to_csv(DATA / "nurture_simulation.csv", index=False)
last = nur[nur.week == WEEKS].set_index("track")
last["promotion_rate"] = (last.promoted_total / pd.Series(TRACKS)).round(3)
last.to_csv(DATA / "nurture_summary.csv")
print(last.to_string())

# ---------------- ICP cards (data) ----------------
cards = []
for seg in seg_t.index[:3]:
    g = d[d.segment == seg]
    top_role = g[g.won].role.value_counts().index[0]
    top_prod = g[g.won]["product"].value_counts().index[0]
    cards.append(dict(segment=seg, deals=len(g), win_rate=round(g.won.mean(), 2),
                      best_role=top_role, best_product=top_prod,
                      avg_won_amount=round(g[g.won].amount.mean(), -1),
                      buyer_type=SEG[seg][0]))
pd.DataFrame(cards).to_csv(DATA / "icp_cards.csv", index=False)
print(pd.DataFrame(cards).to_string(index=False))

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("Aurelis Life Sciences | ICP and nurture (synthetic data)", fontsize=13, weight="bold")
s = seg_t.sort_values("win_rate")
ax[0].barh([x[:28] for x in s.index], s.win_rate * 100, color=BLUE)
ax[0].axvline(d.won.mean() * 100, color="k", ls="--", lw=.8)
ax[0].set(title="Win rate by segment (%)", xlabel="% of deals won")
r = role_t.sort_values("win_rate")
ax[1].barh(r.index, r.win_rate * 100, color=[TEAL if x > d.won.mean() * 100 else GREY for x in r.win_rate * 100])
ax[1].axvline(d.won.mean() * 100, color="k", ls="--", lw=.8)
ax[1].set(title="Win rate by role (%)", xlabel="% of deals won")
t = tt
ax[2].bar(t.index, t.win_rate * 100, color=[TEAL, GOLD, GREY])
ax2 = ax[2].twinx()
ax2.plot(t.index, t.avg_deal, color=BLUE, marker="o")
ax2.spines["top"].set_visible(False)
ax[2].set(title="Account tier: win rate (bars), avg deal (line)", ylabel="win rate %")
ax2.set_ylabel("avg won deal $")
for track, c in zip(TRACKS, [BLUE, TEAL, GOLD]):
    g = nur[nur.track == track]
    ax[3].plot(g.week, g.promoted_total / TRACKS[track] * 100, color=c, label=track)
ax[3].legend(fontsize=8)
ax[3].set(title="Nurture: share promoted to a rep", xlabel="week", ylabel="% of contacts")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "icp_nurture_overview.png", dpi=130)
print("done")
