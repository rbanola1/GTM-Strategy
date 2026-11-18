# How to revise a lead score and its MQL / SQL definitions

1. **Write down what the current score measures and what it misses.** List every scoring rule and ask whether it measures the contact's behaviour, the team's behaviour, or noise.
2. **Pull the outcomes.** For all contacts that existed 6-12 months ago, mark who later became a deal or customer. This is the label for every test below.
3. **Back-test the old score.** Compute how well it ranks buyers above non-buyers (AUC) and the buy rate by score band. If conversion is flat below a certain score, that part of the scale carries no information.
4. **Add the missing dimensions.**
   - **Fit** (who): segment, role, research area, company size, past buyer, region.
   - **Intent** (when): pricing visits, quote requests, new grants or papers, hand-raises.
   - **Engagement** (interest): clicks and replies, not opens.
5. **Clean the engagement rules.** Remove points for the team's own actions. Weight form types and page types by meaning. Cap points per category so one behaviour cannot dominate.
6. **Fix the weights from data.** Start from a documented split (for example 55% fit, 25% engagement, 20% intent). Adjust using the back-test, but keep the intent part non-zero, otherwise there is no reason to collect intent data.
7. **Add hard rules** for exclusions that must never qualify.
8. **Choose thresholds.**
   - Sweep thresholds and record contacts, precision and recall at each.
   - Set SQL from sales capacity: how many leads can reps work well in a week.
   - Set MQL lower, from marketing's nurture capacity and the precision you accept.
   - Check that buy rate rises at each stage; if SQL converts worse than MQL, the definitions are wrong.
9. **Run old and new side by side** for a period. Do not change lifecycle stages until the new score is proven on current data.
10. **Switch, document, monitor.** Record the change date, review the funnel monthly, and re-weight quarterly from outcomes.

## Pitfalls
- Thresholds copied from another system.
- Scoring the team's own actions.
- Letting deal value drive the contact score; use an account tier for that.
- Judging success by the number of MQLs instead of the buy rate of each stage.
- Forgetting that opens are inflated by security scanners.
