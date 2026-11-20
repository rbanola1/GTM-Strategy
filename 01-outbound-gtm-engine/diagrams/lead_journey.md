# Lead journey: signal to sale in six boxes

```mermaid
flowchart LR
    A["1 Find: signals from papers, grants and site visits"] --> B["2 Clean and enrich"]
    B --> C["3 Score: fit and intent"]
    C --> D{"4 Route"}
    D -->|"good fit and intent"| E["Rep emails within 48 hours"]
    D -->|"good fit, no intent"| F["Marketing nurture"]
    D -->|"weak fit"| G["Review or hold"]
    E --> H["5 Engage and 6 measure"]
    F --> H
    G --> H
    H -.->|"monthly re-weight"| C
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef y fill:#FBE5B6,stroke:#E9A23B,color:#222
    class A,B,C a
    class D y
    class E,F,G,H g
```

How to read it: find people with a reason to buy, clean and score them, send each to the right route, and use results each month to improve the score.

Full detail with every connection: [lead_journey_full_detail.md](lead_journey_full_detail.md).
