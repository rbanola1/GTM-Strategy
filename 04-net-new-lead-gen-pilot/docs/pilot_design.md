# Pilot design

## Tracks
| Track | Source | Method |
|---|---|---|
| Industry | Company and people search in the enrichment platform: pharma, CRO, organ-on-chip and need-area biotech | Free search, suppress, tier, then paid email lookup for tiers A and B |
| Academic | Free public sources: literature databases, grant databases, lab pages, author records | Claude-style research, verify emails from paper correspondence lines, no paid enrichment |

Keep tracks as separate files and lead sources so results can be compared.

## Fit tiers
| Tier | Definition | Treatment |
|---|---|---|
| A | Uses a competitor's product, or produces the target cell type in-house | Enrich first, personal outreach |
| B | Uses an alternative primary cell type | Enrich after A |
| C | Works in an area that needs our product, no evidence yet | Nurture or later wave |
| D | Low relevance | Dropped |

Evidence is stored beside each tier (paper, grant, page) so a rep can see why a lead is on the list.

## Rules
- Region first: start with one region and expand.
- One to three people per large company, up to two per small company.
- Medium companies already in the CRM: new people are allowed; small companies already in the CRM: exclude the whole company.
- Competitors are excluded by domain and company list.
- Re-check each contact against the CRM on the day of import.
- Never mix this pilot's files with other targeting campaigns.

## Workflow
1. Source candidates (free).
2. Suppress against the CRM export.
3. Tier with free signals; attach evidence.
4. AI fit check on tiers B and C (cost estimate first).
5. 10-row paid test; review actual cost.
6. Email lookup in priority order within the approved budget.
7. Verify emails not produced by the waterfall; drop invalid.
8. Import to the CRM with lead source and a hold from e-blasts.
9. Run the signal-based sequence from the CRM.
10. Report against the control process.

## Output files
One file per product focus, each with tier, evidence, email status (ready, verify, none) and lead source. Contacts without an email stay in the file for later.
