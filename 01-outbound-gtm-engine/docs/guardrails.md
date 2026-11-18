# Guardrails

## Suppress before anything is imported or sent
- Duplicates (match on email and name against the CRM)
- Existing customers (handled by the account team)
- Competitor domains: a "do not email" segment checked on every list
- Small companies already in the CRM: exclude the whole company
- Students and generic mailboxes

## Send pacing
- Cap enrollments per sender per day; never mass-enroll thousands at once.
- A mass enrollment takes weeks to drain and hides what is working.
- **Stop rule:** if reply rate stays under 1% after about 500 sends, pause and revise the list or message before sending more.
- Targeted, signal-based sends should be judged separately from broad ones.

## Data ownership
- One owner per field and per handoff. Agree who may write to the CRM (people, enrichment tools, workflows) before building.
- Marketing-contact tier is a budget: define who may enter it and who must leave it.
- Every list import carries a Lead Source and Product of Interest tag.

## Change control
Build each new score, workflow and segment next to the old one, switched off. Test on a handful of test contacts. Switch on for one segment first. Nothing changes in the CRM without sign-off from the owner.

## Reporting rules
- Count replies excluding auto-replies; do not report opens as engagement.
- Report one funnel per product and per lead source: sent, bounced, replied, meeting, deal.
