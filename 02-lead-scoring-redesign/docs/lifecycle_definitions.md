# Lifecycle definitions: old and new

## Old (engagement only)
| Stage | Rule |
|---|---|
| Lead | Contact exists |
| MQL | Engagement score of 15 or more |
| SQL | Engagement score of 30 or more |
| Opportunity | Deal created |
| Customer | Deal closed won |

## New (fit, engagement, intent)
| Stage | Rule | Owner |
|---|---|---|
| Lead | Contact exists, or good fit with no signal yet, or excluded | Nobody (data hygiene) |
| MQL | Combined score of 45 or more and not excluded: good fit with some interest | Marketing: nurture by product |
| SQL | A hand-raise from a contact scoring 50 or more, or a combined score of 65 or more | Rep, follow up within 48 hours |
| Check | A hand-raise from a contact scoring under 50 | Reviewed by hand weekly: real buyer or noise |
| Opportunity | Deal created, linked to company and contact | Rep |
| Customer | Deal closed won | Account owner |

## Hand-raises
Reply to a sales email, quote or sample request, pricing-page visit, meeting booked. They always trigger a response; fit decides whether the response is a rep (SQL) or a hand review (Check).

## Hard rules (score is zero, never MQL)
Competitor domains, companies below the minimum size, student-only contacts, existing customers handled by the account team.

## Decay
Engagement and intent points fade (20% every 3 months) so old activity stops counting. Fit does not decay but is refreshed when data changes.

## Why the thresholds differ from the old ones
The new score has a different scale and meaning, so 15 and 30 do not carry over. Set thresholds from a back-test and sales capacity, as described in the [revision playbook](revision_playbook.md).
