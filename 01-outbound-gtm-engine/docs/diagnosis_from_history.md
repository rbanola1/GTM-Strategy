# Diagnosis: why a high-volume outbound process produced few deals

A review of the go-to-market process, using the CRM's own history (numbers rounded and scaled).

## How outbound ran
1. **Keywords:** the product team supplied keywords for each launch (cell identity and cell application).
2. **List build:** a scientific contact database produced lists; emails were verified (about 0.7% bounce).
3. **Marketing blast:** the first email came from marketing; reps followed up opens and clicks.
4. **Sequences:** commercial operations built further lists and ran sequences (about 90 sequences, over 90,000 enrolments, roughly 150,000 emails).
5. **Handover:** warm replies went to reps for calls, meetings and samples.
Alongside ran trade shows, webinars, field visits and regional outreach.
**Not in the process:** buyer intent and purchase signals, and a second ICP check on each contact. Selection was by keyword only.

## The real problem: raw material sitting idle
- Bounces and unsubscribes were low. The wastage was leads that never moved at all.
- In one year about 58,000 leads were created and only about 60 became deals (roughly 0.02% became customers).
- Lead score and touches climbed together with the result, so the signal was real but not acted on:

| | Idle lead | Became a deal | Closed won |
|---|---|---|---|
| Average touches | about 3 | about 15 | about 31 |
| Average lead score | about 3 | about 14 | about 19 |

- About 90% of contacts had three or fewer touches. Every lead got roughly the same treatment regardless of score.

## What separated idle leads from won deals
Won deals had many more touches and higher scores. Working a deal also creates touches, so this shows depth of follow-up, not the sole cause; the point is that effort was not routed toward leads showing early signal.

## Root cause: awareness, not effort
- **Thin portfolio:** fewer product lines than competitors to lead with.
- **Similar products:** some products compete on parity, not differentiation.
- **Zero-awareness products:** a genuinely novel product that even the ideal customers did not know existed.
- **Two-sided identification gap:** a non-responder is either locked into a competitor or does not need the material, and the CRM could not tell which.

## Was it over-mailing? No
| Year | Contacts | Opt-out rate | Emails sent |
|---|---|---|---|
| Year 1 | about 2,000 | about 1% | about 1,000 |
| Year 2 | about 48,000 | about 3% | about 150,000 |
| Year 3 (to date) | about 58,000 | about 1% | about 200,000 |
Opt-out rates stayed inside the usual 0.5% to 2% range except in the first big volume year, so the stalled funnel was not caused by over-mailing. Qualitatively, some emails were being blocked, which is a deliverability issue to track.

## What sequences actually produced (by list type)
| List type | Real reply rate | Note |
|---|---|---|
| Bulk keyword lists | about 0.15% | Most enrolments, most deals opened, no paid wins traced |
| Past-attendee cold list | about 0.04% | Almost no replies |
| Event follow-up | about 0.7% | About 5x the bulk rate |
| Targeted accounts | about 0.9% | About 6x the bulk rate |
- About 27% of real replies said "wrong person or field".
- Open rates did not predict replies: a list with a higher open rate produced fewer real replies.
- Daily sending limits meant thousands of emails in one large sequence were never sent.
- Paid wins came mostly from conferences, field sales, referrals and launches, not from sequences.

## Funnel velocity after the lifecycle workflows went live
| Stage | Quarter 2 | Quarter 3 (partial) |
|---|---|---|
| Lead to MQL | 7% | 16.5% |
| MQL to SQL | 7.8% | 5.5% |
| SQL to opportunity | 10% | 26.5% |
| Opportunity to customer | 19% | 15% |
Volume fell sharply when bulk sequencing stopped, lead-to-MQL more than doubled and SQL-to-opportunity nearly tripled; the dips are worth watching.

## Ideas brainstormed (not decided)
Newsletter plus discount · monthly commitment model (needs finance support) · scientific content library that doubles as sales enablement · presence in generative-engine answers · seeding target labs with consumables · different messaging for small labs (emotional) and large accounts (attribute and cost led).

## Draft response: filter leads in stages before anyone emails
1. Keyword pool from the contact database.
2. ICP match, company first and then contact, with CRM suppression.
3. Signals and buyer intent.
4. Personal opener, reviewed, then send from sequences within daily limits.
Warm replies go to reps; everyone else goes to marketing nurture. This is the design built out in the rest of this repository.

## Decisions asked of the team
How to grow inbound (only a handful of deals in three years) · backfill contact associations on older deals so history can be scored · feasibility of a subscription or commitment model · re-run and, if it holds, schedule the research-publication lead pilot · split messaging by segment.
