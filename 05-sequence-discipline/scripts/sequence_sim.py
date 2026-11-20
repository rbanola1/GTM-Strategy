"""Sequence discipline: mass enrollment vs paced, signal-based sending (fictional RB Tech).

Simulates a 3-step email sequence under two operating styles and applies the stop rule
(pause if the reply rate is under 1% after about 500 sends). All numbers are synthetic.
Run: python scripts/sequence_sim.py       Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(3)

STEPS = 3
STEP_GAP_DAYS = 3

def run(name, contacts, daily_cap, weekdays_only, send_days, reply_p, bounce_p, auto_reply_share, days=120):
    """Return a daily table of sends, bounces, real replies, auto replies."""
    queue = [(0, s) for s in range(STEPS) for _ in range(contacts)]       # (earliest day, step) per planned send
    pending = {s: contacts for s in range(STEPS)}                            # sends left per step
    ready_day = {0: 0, 1: STEP_GAP_DAYS, 2: 2 * STEP_GAP_DAYS}
    rows, sent_total, replies_total, stopped = [], 0, 0, False
    for day in range(days):
        dow = day % 7
        can_send = (dow in send_days) if weekdays_only else dow < 5
        sent_today = 0
        if can_send and not stopped:
            for s in range(STEPS):
                if day >= ready_day[s] + 0 and pending[s] > 0 and sent_today < daily_cap:
                    n = min(daily_cap - sent_today, pending[s])
                    pending[s] -= n
                    sent_today += n
        bounces = rng.binomial(sent_today, bounce_p) if sent_today else 0
        delivered = sent_today - bounces
        real = rng.binomial(delivered, reply_p / STEPS) if delivered else 0
        auto = rng.binomial(delivered, auto_reply_share) if delivered else 0
        sent_total += sent_today
        replies_total += real
        # stop rule: after ~500 sends, pause if real reply rate is under 1%
        if STOP_RULE and sent_total >= 500 and replies_total / max(sent_total, 1) < 0.01 and not stopped:
            stopped = True
        rows.append(dict(style=name, day=day, sends=sent_today, bounces=bounces, real_replies=real, auto_replies=auto,
                         cum_sends=sent_total, cum_real_replies=replies_total, paused=stopped))
    return pd.DataFrame(rows)

STOP_RULE = False
bulk = run("Bulk: mass enrollment", contacts=6000, daily_cap=400, weekdays_only=False, send_days=range(7),
           reply_p=0.0015 * STEPS, bounce_p=0.035, auto_reply_share=0.02)
STOP_RULE = True
bulk_stop = run("Bulk with stop rule", contacts=6000, daily_cap=400, weekdays_only=False, send_days=range(7),
                reply_p=0.0015 * STEPS, bounce_p=0.035, auto_reply_share=0.02)
STOP_RULE = False
paced = run("Paced: targeted, signal-based", contacts=600, daily_cap=50, weekdays_only=True, send_days=(1, 2, 3),
            reply_p=0.03 * STEPS, bounce_p=0.012, auto_reply_share=0.02)
allr = pd.concat([bulk, bulk_stop, paced])
allr.to_csv(DATA / "daily_simulation.csv", index=False)

def summ(df, label):
    s = df.cum_sends.iloc[-1]
    done = df[df.cum_sends >= s * .999].day.min() if s else None
    return dict(style=label, contacts=6000 if "ulk" in label else 600, total_sends=int(s),
                days_to_finish=int(done) if done is not None else None,
                real_reply_rate=round(df.cum_real_replies.iloc[-1] / s, 4) if s else 0,
                real_replies=int(df.cum_real_replies.iloc[-1]), bounce_rate=round(df.bounces.sum() / s, 4) if s else 0,
                auto_replies=int(df.auto_replies.sum()))
tab = pd.DataFrame([summ(bulk, "Bulk: mass enrollment"), summ(bulk_stop, "Bulk with stop rule"),
                    summ(paced, "Paced: targeted, signal-based")])
tab["sends_per_real_reply"] = (tab.total_sends / tab.real_replies.replace(0, np.nan)).round(0)
tab.to_csv(DATA / "style_comparison.csv", index=False)
print(tab.to_string(index=False))

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Sequence discipline (synthetic data)", fontsize=13, weight="bold")
for df, c, lab in ((bulk, RED, "Bulk"), (paced, TEAL, "Paced, targeted")):
    ax[0].plot(df.day, df.cum_sends, color=c, label=lab)
ax[0].legend(fontsize=8)
ax[0].set(title="Cumulative sends", xlabel="day", ylabel="emails sent")
for df, c, lab in ((bulk, RED, "Bulk"), (paced, TEAL, "Paced, targeted")):
    ax[1].plot(df.day, df.cum_real_replies, color=c, label=lab)
ax[1].legend(fontsize=8)
ax[1].set(title="Cumulative real replies", xlabel="day", ylabel="replies")
x = np.arange(3)
ax[2].bar(x, tab.real_reply_rate * 100, color=[RED, GOLD, TEAL])
ax[2].set_xticks(x, ["Bulk", "Bulk +\nstop rule", "Paced"])
ax[2].axhline(1, color="k", ls="--", lw=.8)
ax[2].text(2.3, 1.05, "1% line", fontsize=8)
ax[2].set(title="Real reply rate (%)", ylabel="%")
ax[3].bar(x, tab.total_sends, color=[RED, GOLD, TEAL])
ax[3].set_xticks(x, ["Bulk", "Bulk +\nstop rule", "Paced"])
ax[3].set_yscale("log")
for i, (s, r) in enumerate(zip(tab.total_sends, tab.real_replies)):
    ax[3].text(i, s * 1.15, f"{r} replies", ha="center", fontsize=8)
ax[3].set(title="Emails sent (log scale) and replies", ylabel="emails")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "sequence_discipline.png", dpi=130)
print("done")
