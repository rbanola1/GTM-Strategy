# Scoring model

Two scores, kept separate, because they answer different questions.

| Score | Question | Inputs | Range |
|---|---|---|---|
| **Fit** | Is this a real buyer? | Segment, role, research area, past buyer, region | 0-100 |
| **Intent** | Is now the time? | Signals in the [catalog](signal_catalog.md) | 0-100 |

## Fit points (starting weights, tuned from won deals)
| Attribute | Points |
|---|---|
| Segment | Organ-on-chip 25, cell therapy 22, pharma 20, CRO 15, academic 10, hospital/core 8, other 0 |
| Role | PI/director 20, scientist 15, procurement 10, postdoc/student 4, other 0 |
| Research area | Core areas 25, adjacent area 12, other area 10, off-topic -15 |
| Past buyer | +20 |
| Region | US/EU +5, other -5 |

## Thresholds
Fit >= 50 is high fit. Intent >= 30 is intent now. Set them from won deals: the fit score should rank past buyers above non-buyers before it goes live.

## Decay and promotion
- Engagement points decay 20% every quarter so old activity stops counting.
- A nurture contact is promoted to a rep when the combined score crosses the threshold, or on any hand-raise.

## Monthly re-weighting
1. Join outcomes (reply, meeting, deal) back to the score inputs.
2. Compare reply and meeting rates with and without each signal and attribute.
3. Move points toward predictive inputs, away from noisy ones.
4. Record the change and the date, so score history stays explainable.
