# Cost control

## Rules
1. **No paid run without an estimate and an approval.** State the action, rows, expected credits and the result you expect.
2. **Auto-run off** on every enrichment column. Run on 10 rows first.
3. **Measure the real unit cost.** Headline rates understate waterfall lookups, because each fallback provider adds cost.
4. **Free before paid.** Search and save are free in most platforms, but the save wizard may preselect paid enrichments; close the wizard without enriching.
5. **Cheapest model that works.** Use a small model for classification columns and test it; web-research agents can cost several times more per row and the cheapest model may misclassify.
6. **One provider per job.** Do not pay twice for the same email: if the waterfall found it, skip the separate verifier.
7. **Cap per user and per month.** Know the account's monthly credit limit and who can raise it.
8. **Keep a reserve** for fixes and re-runs (about 15% of the budget).

## Budget view (example, 2,000 credits)
| Use | Credits |
|---|---|
| Cost test (10 to 50 rows) | about 100 |
| AI fit check, tiers B and C | about 1,100 |
| Email lookups, tier A and best of B | about 700 |
| Reserve | about 100 |

## Lessons
- A default "research the company's ICP" column researches the target's own customers, not yours; write your own prompt.
- Auto-enrichment on creation can burn credits unseen.
- Trial accounts may cap tables and previews (for example 50 rows), so slice searches by region or size.
- Expect list inflation: only a minority of candidates survive suppression and tiering, so size the list accordingly.
