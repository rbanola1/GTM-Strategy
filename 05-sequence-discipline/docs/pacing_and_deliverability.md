# Pacing and deliverability

## Pacing
| Rule | Value |
|---|---|
| Daily send cap per sender | About 50 for targeted sequences; never above the platform's hard limit |
| Send days | Tuesday to Thursday |
| Enrolment | In small batches; enrol only what drains in about a week |
| Mass enrolment | Not allowed: a large enrolment drains over weeks, hides performance and fills the failed-send queue |

When a platform caps total sends per day, enrolments beyond that wait in a queue and fail or delay; the queue is not a sign of a deliverability problem, it is a capacity problem.

## Deliverability
- Target bounce rate under 2%. Verify emails not produced by a verified source before sending.
- Do not send from a freshly created domain at volume; warm up gradually.
- Remove hard bounces immediately and never re-enrol them.
- Honour unsubscribes at once.
- Keep complaint signals near zero: relevant targeting is the best deliverability tool.
- Check that messages arrive: seed test addresses, and for missing deliveries ask the mail provider for a message trace.

## Suppression before enrolment
Competitor domains, customers, open deals, contacts already in a sequence, small-company exclusions, anyone who asked to stop.

## Stop rule
After about 500 sends, if the real reply rate is under 1%, pause the list. Review in this order: list fit, signal quality, message length and ask, then send timing. Resume with a revised batch.

## Monitoring
Daily: sends, bounces, failures. Weekly: real replies, positive replies, meetings, by list and by sender. Monthly: compare lists and templates.
