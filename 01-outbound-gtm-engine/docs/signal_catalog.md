# Signal catalog

| Signal | Source | Cost | Intent points | How it is used |
|---|---|---|---|---|
| Email reply | CRM | Free | 40 | Hand-raise: always routes to a rep |
| Form fill (sample, quote, contact) | Website | Free | 35 | Hand-raise |
| Pricing or product page visit | Website intent | Free | 30 | Strong buying signal |
| New grant award | Public grant database | Free | 25 | Funded project, budget exists |
| New paper on topic | Literature API | Free | 20 | Active research in the area |
| Protocol download | Website | Free | 20 | Technical evaluation under way |
| Competitor citation | Literature API | Free | 15 | Uses a competing product, switching angle |
| Hiring signal | Job posts | Free | 10 | Team growing in the area |

## Rules
- Signals add up and are capped at 100.
- Count **replies and clicks**, not opens: opens are inflated by security scanners, and replies must exclude auto-replies.
- A hand-raise (reply, form, quote or sample request, pricing visit) always promotes a contact out of nurture, whatever the score.
- Start with free public signals; add paid sources only after the free ones prove their lift.
- Re-check each signal's reply lift monthly (the `signal_lift.csv` output) and move points toward the signals that predict replies.
