# ShopPulse — Executive Business Insights & Strategic Recommendations
**Analytics Scope:** 9,994 Verified Transactions | Sample Superstore Dataset (Tableau Public / Open Data)  
**Enterprise Performance:** $2,297,200.65 Revenue | $286,396.54 Gross Profit | 12.47% Realized Margin | 5,009 Orders | 793 Customers

---

## 1. Executive Summary

This report delivers 12 quantified business case studies derived from rigorous statistical analysis of the Sample Superstore e-commerce transaction dataset (2014–2017). Every insight connects an empirical finding directly to its business impact, tactical recommendation, and measurable KPI target.

---

## 2. Strategic Case Studies

### Case Study 01: Technology Division Drives Over 50% of Total Enterprise Profit
- **Finding:** Technology generated **$836,154.02 in revenue (36.40% share)** and **$145,455.03 in gross profit**, representing **50.79% of all enterprise profit** with a healthy **17.39% profit margin**.
- **Evidence:** Query 06 & `src/analysis.py` category aggregation.
- **Business Impact:** Technology hardware and copiers are the single greatest cash engine of the retail business.
- **Recommendation:** Expand inventory allocation for technology accessories and enterprise copiers; increase B2B advertising spend for tech categories by 20%.
- **Target KPI:** Expand Technology revenue share from 36.4% to 42.0% while maintaining >17% margin.

---

### Case Study 02: Severe Margin Compression in Furniture Category (2.49% Margin)
- **Finding:** Furniture generated **$741,999.74 in revenue** (32.30% share) but yielded only **$18,451.24 in net profit** (a meager **2.49% profit margin**).
- **Evidence:** Tables sub-category produced a cumulative net loss of **-$17,725.48** and Bookcases lost **-$3,472.56**.
- **Business Impact:** Bulky shipping expenses combined with heavy promotional discounting virtually wipe out operating margins in Furniture.
- **Recommendation:** Eliminate promotional discounts exceeding 15% on Tables and Bookcases; renegotiate freight shipping terms with logistics carriers.
- **Target KPI:** Raise Furniture category realized margin from 2.49% to 8.00% within 2 quarters.

---

### Case Study 03: The "Discount Destruction" Cliff (>20% Discount)
- **Finding:** Transactions sold at **0% discount** achieved a **29.9% profit margin**. Standard discounts (1%–20%) achieved **14.5% margin**. However, discounts exceeding **20% resulted in a cumulative net loss of -$32,142.98**.
- **Evidence:** Query 13 & discount tier impact analysis.
- **Business Impact:** Markdown pricing beyond 20% fails to generate adequate volume elasticity and directly destroys company profitability.
- **Recommendation:** Implement automated sales pricing guardrails in the checkout system capping standard discretionary discounts at 15%.
- **Target KPI:** Reduce transactions with >20% discount by 85%, recapturing ~$28K in annual margin.

---

### Case Study 04: Regional Profit Asymmetry — West Leads While Central Lags
- **Finding:** The **West region** generated **$725,457.82 in sales** and **$108,418.45 in profit (14.94% margin)**. In contrast, the **Central region** generated **$501,239.89 in sales** but only **$39,706.36 in profit (7.92% margin)**.
- **Evidence:** Query 08 & regional breakdown.
- **Business Impact:** Central region profitability is heavily dragged down by aggressive discounting practices in specific states.
- **Recommendation:** Apply West region merchandising and pricing governance across Central branch operations.
- **Target KPI:** Lift Central region profit margin from 7.92% to 12.00%.

---

### Case Study 05: State-Level Profit Leaks in Texas and Ohio
- **Finding:** **Texas** generated **$170,188.05 in sales** but incurred a catastrophic net loss of **-$25,729.36**. **Ohio** incurred a loss of **-$16,971.38**.
- **Evidence:** Query 16 state profitability ranking.
- **Business Impact:** High promotional discounts in Texas (averaging 37.1%) and Ohio eroded gross profit across binders and furniture.
- **Recommendation:** Mandate minimum floor pricing in Texas and Ohio; suspend regional loss-leader campaigns.
- **Target KPI:** Turn Texas operations net positive (+$10K profit) within 12 months.

---

### Case Study 06: B2B & Home Office Deliver Higher Margin Efficiency
- **Finding:** Consumer accounts represent **$1,161,401.34 (50.56% of sales)** with an **11.55% margin**. Corporate accounts represent **$706,146.37 (30.74%)** with a **13.03% margin**, and Home Office accounts achieved the highest margin at **14.03% ($60,298.22 profit)**.
- **Evidence:** Query 11 customer segment breakdown.
- **Business Impact:** Corporate and Home Office clients exhibit lower price sensitivity and purchase higher-margin office solutions.
- **Recommendation:** Develop targeted B2B corporate procurement packages and tailored business loyalty accounts.
- **Target KPI:** Increase Corporate & Home Office combined revenue contribution to 50.0%.

---

### Case Study 07: Pareto 80/20 SKU Revenue Concentration
- **Finding:** The top **15.2% of product SKUs (283 out of 1,862)** account for **70.0% of total enterprise revenue**. The top SKU (*Canon imageCLASS 2200 Advanced Copier*) generated **$61,599.82 in revenue and $25,199.93 in profit**.
- **Evidence:** Query 18 Pareto cumulative distribution.
- **Business Impact:** Company top-line performance is driven by a concentrated core of high-velocity equipment.
- **Recommendation:** Maintain dynamic safety stock buffers for the top 50 revenue-generating SKUs with tier-1 supplier contracts.
- **Target KPI:** Zero stockouts on top 50 SKUs during peak operating quarters.

---

### Case Study 08: 98.5% High Repeat Customer Fidelity
- **Finding:** **98.49% of unique customers (781 out of 793)** placed 2 or more orders across the 4-year lifecycle, averaging **6.3 orders per customer**.
- **Evidence:** Query 12 repeat purchase frequency distribution.
- **Business Impact:** Strong organic customer retention reduces reliance on costly top-of-funnel customer acquisition (CAC).
- **Recommendation:** Launch automated post-purchase replenishment notifications and tiered loyalty incentives.
- **Target KPI:** Increase average annual order frequency per customer from 6.3 to 8.0 orders.

---

### Case Study 09: Q4 Seasonality Surge (Holiday Quarter Peak)
- **Finding:** Q4 (October through December) consistently delivers the highest quarterly volume, averaging **$280K+ in sales per Q4** compared to **$120K in Q1**.
- **Evidence:** Query 17 quarterly performance analysis.
- **Business Impact:** Seasonal holiday demand drives 35%+ of annual sales velocity.
- **Recommendation:** Initiate supplier purchase orders 60 days prior to Q4 (by August 15) and optimize logistics staffing for holiday fulfillment.
- **Target KPI:** Maintain 99.2% on-time shipping fulfillment rate during Q4 peak.

---

### Case Study 10: Unprofitable SKUs Catalog Rationalization
- **Finding:** **274 distinct product SKUs** generated cumulative losses totaling **-$85,123.40**.
- **Evidence:** Query 14 loss-making products analysis.
- **Business Impact:** Non-performing products consume warehouse capacity and tie up valuable working capital.
- **Recommendation:** Delist bottom 50 consistently loss-making SKUs and transition low-velocity catalog items to a direct vendor drop-ship fulfillment model.
- **Target KPI:** Recapture $40K in annual operating capital by rationalizing loss-making SKUs.

---

### Case Study 11: Shipping Mode Performance — Standard Class Dominance
- **Finding:** **Standard Class** shipping accounted for **59.7% of all orders (2,994 orders)** and **$1,358,215.93 in sales**, maintaining steady fulfillment margins.
- **Evidence:** Query 15 shipping distribution.
- **Business Impact:** Standard Class remains the most cost-effective shipping method for enterprise profitability.
- **Recommendation:** Retain Standard Class as the default free shipping tier for qualifying orders over $150, while upselling expedited Same-Day / First Class as premium paid upgrades.
- **Target KPI:** Increase premium shipping paid conversion rate by 15%.

---

### Case Study 12: High-Ticket Price Tier Margin Resilience
- **Finding:** Orders with item sales exceeding **$1,000** delivered a steady **18.2% profit margin**, whereas transactions under **$50** yielded lower net returns due to fixed transaction overhead.
- **Evidence:** Query 19 sales tier distribution.
- **Business Impact:** High-ticket equipment sales provide strong unit economics.
- **Recommendation:** Implement bundled checkout thresholds (e.g. minimum order quantity on items under $20) to lift transaction basket size.
- **Target KPI:** Increase Average Order Value (AOV) from $458.62 to $520.00.
