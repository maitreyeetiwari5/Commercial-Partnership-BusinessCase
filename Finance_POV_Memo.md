# Finance Point of View: Live Sports Package Partnership

**Decision:** Whether to sign a 5-year exclusive license for a mid-tier league's out-of-market live-games package, and under which deal structure.
**Scope:** Hypothetical deal, sized with public benchmarks (NFL Sunday Ticket on YouTube; MLS on Apple). Pre-tax contribution, 10% discount rate, $mm.

## 1. Recommendation

**Sign only under Structure B (minimum guarantee + 40% revenue share), and negotiate the MG down or into a step-up tied to subscriber milestones, plus an exit right after Year 2.** B is the only structure with positive value in both the Base case and on a probability-weighted basis. A flat fee destroys value unless the Upside materializes. Pure revenue share looks safest but gives the partner too much of every outcome, so it never creates value outside the Upside.

## 2. Key numbers

| 5-yr NPV ($mm) | Downside | Base | Upside | Prob-weighted (25/50/25) |
|---|---|---|---|---|
| A: Flat fee ($200M, +4%/yr) | (734) | (303) | 569 | (193) |
| **B: $100M MG + 40% share** | **(298)** | **101** | **585** | **122** |
| C: 60% revenue share | (213) | (92) | 185 | (53) |

- **Base case, Structure B:** Year-1 deal revenue about $230M; payback in Year 3.
- **Breakeven:** about 0.72M Year-1 subscribers vs. 1.0M in the Base case. That is a real but thin cushion of roughly 28%.
- **Largest driver:** Year-1 subscribers (±20% moves NPV by about -$80M / +$66M). Viewing hours and CPM rank next with equal effect, because ad revenue is proportional to both.

## 3. What has to be true

1. Year-1 subscribers clear about 0.72M. For scale, Sunday Ticket was estimated at about 1.5M subscribers in its first season with the most popular league in the U.S.
2. Live-sports CPMs hold in the premium $30–65 range rather than compressing toward the ~$26 average for CTV.
3. Most viewing is incremental; cannibalization of existing viewing stays near 25% or lower.

## 4. Risks and negotiation levers

- **Downside exposure:** if demand disappoints, deal contribution covers well under half of the MG each year and every structure loses money. Protection has to come from contract terms, not structure choice alone.
- **Levers:**
  - A lower Year-1/2 MG that steps up once subscriber milestones are hit. The MG binds in Years 1–2 of the Base case, so this directly reduces the downside.
  - A renegotiation or exit right if Year-2 subscribers miss plan.
  - A longer term in exchange for a lower revenue share.
- **Not modeled:** strategic value, such as engagement, cross-sell into other paid subscriptions, and advertiser relationships. Including it would only strengthen the case; excluding it keeps the recommendation conservative.

## 5. Tracking plan

Report quarterly against the business case on four KPIs: subscribers, viewing hours, CPM, and incremental revenue. Flag variances beyond self-calibrating thresholds (median + scaled MAD). Commentary is written only when a documented driver exists; anything unexplained is routed for analyst review (see `variance_tracking.py`).
