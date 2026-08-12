-- ==============================================================================
-- ShopPulse E-Commerce Analytics Platform: 20 Advanced Analytical SQL Queries
-- Demonstrating CTEs, Window Functions (RANK, DENSE_RANK, LAG, SUM OVER),
-- Cohort Analysis, CLV, RFM Segmentation, and Business Metrics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 01: Executive Summary KPIs (Revenue, Profit, Orders, AOV, Margin)
-- ------------------------------------------------------------------------------
-- Business Question: What are the primary macro business performance metrics?
SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    COUNT(DISTINCT product_id) AS total_products_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_percentage
FROM fact_ecommerce_sales;


-- ------------------------------------------------------------------------------
-- Query 02: Monthly Revenue & Profit Velocity
-- ------------------------------------------------------------------------------
-- Business Question: How does revenue and profit evolve month-over-month?
SELECT 
    SUBSTR(order_date, 1, 7) AS year_month,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS monthly_revenue,
    ROUND(SUM(profit), 2) AS monthly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY SUBSTR(order_date, 1, 7)
ORDER BY year_month ASC;


-- ------------------------------------------------------------------------------
-- Query 03: Month-Over-Month (MoM) Growth Analysis Using LAG() Window Function
-- ------------------------------------------------------------------------------
-- Business Question: What is our revenue growth rate compared to the preceding month?
WITH monthly_metrics AS (
    SELECT 
        SUBSTR(order_date, 1, 7) AS year_month,
        ROUND(SUM(sales), 2) AS revenue,
        ROUND(SUM(profit), 2) AS profit
    FROM fact_ecommerce_sales
    GROUP BY SUBSTR(order_date, 1, 7)
)
SELECT 
    year_month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(((revenue - LAG(revenue, 1) OVER (ORDER BY year_month)) / 
           LAG(revenue, 1) OVER (ORDER BY year_month)) * 100.0, 2) AS mom_revenue_growth_pct,
    profit,
    LAG(profit, 1) OVER (ORDER BY year_month) AS prev_month_profit,
    ROUND(((profit - LAG(profit, 1) OVER (ORDER BY year_month)) / 
           LAG(profit, 1) OVER (ORDER BY year_month)) * 100.0, 2) AS mom_profit_growth_pct
FROM monthly_metrics
ORDER BY year_month ASC;


-- ------------------------------------------------------------------------------
-- Query 04: Cumulative Running Revenue Total Using SUM() OVER ()
-- ------------------------------------------------------------------------------
-- Business Question: What is the cumulative revenue and profit trajectory over time?
WITH daily_revenue AS (
    SELECT 
        SUBSTR(order_date, 1, 10) AS order_day,
        SUM(sales) AS daily_sales,
        SUM(profit) AS daily_profit
    FROM fact_ecommerce_sales
    GROUP BY SUBSTR(order_date, 1, 10)
)
SELECT 
    order_day,
    ROUND(daily_sales, 2) AS daily_sales,
    ROUND(SUM(daily_sales) OVER (ORDER BY order_day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue,
    ROUND(daily_profit, 2) AS daily_profit,
    ROUND(SUM(daily_profit) OVER (ORDER BY order_day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_profit
FROM daily_revenue
ORDER BY order_day ASC;


-- ------------------------------------------------------------------------------
-- Query 05: Top 10 Best-Selling Products by Revenue
-- ------------------------------------------------------------------------------
-- Business Question: Which products drive the largest share of total sales?
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- Query 06: Category Performance Ranking & Market Share
-- ------------------------------------------------------------------------------
-- Business Question: How do product categories perform in revenue and margin?
SELECT 
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS category_revenue,
    ROUND((SUM(sales) * 100.0 / (SELECT SUM(sales) FROM fact_ecommerce_sales)), 2) AS revenue_share_pct,
    ROUND(SUM(profit), 2) AS category_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY category
ORDER BY category_revenue DESC;


-- ------------------------------------------------------------------------------
-- Query 07: Product Ranking within Each Category using DENSE_RANK()
-- ------------------------------------------------------------------------------
-- Business Question: What are the top 3 revenue-generating products inside every category?
WITH category_product_sales AS (
    SELECT 
        category,
        product_name,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_category
    FROM fact_ecommerce_sales
    GROUP BY category, product_name
)
SELECT 
    category,
    rank_in_category,
    product_name,
    total_sales,
    total_profit
FROM category_product_sales
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category ASC;


-- ------------------------------------------------------------------------------
-- Query 08: Region-wise Sales & Profitability Breakdown
-- ------------------------------------------------------------------------------
-- Business Question: What is the geographic distribution of revenue and margins?
SELECT 
    region,
    COUNT(DISTINCT order_id) AS order_volume,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS regional_margin_pct
FROM fact_ecommerce_sales
GROUP BY region
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------------------------
-- Query 09: Top Category per Region using Partitioned Window Functions
-- ------------------------------------------------------------------------------
-- Business Question: Which category dominates sales inside each geographic region?
WITH regional_category_sales AS (
    SELECT 
        region,
        category,
        ROUND(SUM(sales), 2) AS category_sales,
        ROUND(SUM(profit), 2) AS category_profit,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY SUM(sales) DESC) AS ranking
    FROM fact_ecommerce_sales
    GROUP BY region, category
)
SELECT 
    region,
    category AS top_category,
    category_sales,
    category_profit
FROM regional_category_sales
WHERE ranking = 1
ORDER BY category_sales DESC;


-- ------------------------------------------------------------------------------
-- Query 10: Top 15 High-Value VIP Customers
-- ------------------------------------------------------------------------------
-- Business Question: Who are our top revenue-generating customers?
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.region,
    COUNT(DISTINCT f.order_id) AS total_orders_placed,
    SUM(f.quantity) AS total_items_bought,
    ROUND(SUM(f.sales), 2) AS total_spend,
    ROUND(SUM(f.profit), 2) AS total_profit_generated,
    ROUND(SUM(f.sales) / COUNT(DISTINCT f.order_id), 2) AS customer_aov
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.region
ORDER BY total_spend DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- Query 11: Customer Lifetime Value (CLV) Approximation
-- ------------------------------------------------------------------------------
-- Business Question: What is the CLV distribution across customer segments?
WITH customer_aggregates AS (
    SELECT 
        customer_id,
        customer_segment,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(sales) AS total_spend,
        SUM(profit) AS total_profit,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM fact_ecommerce_sales
    GROUP BY customer_id, customer_segment
)
SELECT 
    customer_segment,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(total_orders), 1) AS avg_orders_per_customer,
    ROUND(AVG(total_spend), 2) AS avg_clv_revenue,
    ROUND(AVG(total_profit), 2) AS avg_clv_profit,
    ROUND(SUM(total_spend), 2) AS segment_total_revenue,
    ROUND((SUM(total_profit) / SUM(total_spend)) * 100.0, 2) AS segment_margin_pct
FROM customer_aggregates
GROUP BY customer_segment
ORDER BY segment_total_revenue DESC;


-- ------------------------------------------------------------------------------
-- Query 12: Repeat Customers vs Single-Purchase Customers
-- ------------------------------------------------------------------------------
-- Business Question: What proportion of our customer base returns for repeat purchases?
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(sales) AS total_spend
    FROM fact_ecommerce_sales
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-Time Buyer'
        WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional Repeat (2-4 Orders)'
        WHEN order_count BETWEEN 5 AND 9 THEN 'Frequent Buyer (5-9 Orders)'
        ELSE 'Super VIP (10+ Orders)'
    END AS customer_loyalty_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / (SELECT COUNT(DISTINCT customer_id) FROM fact_ecommerce_sales), 2) AS pct_of_customers,
    ROUND(SUM(total_spend), 2) AS total_revenue_generated,
    ROUND(SUM(total_spend) * 100.0 / (SELECT SUM(sales) FROM fact_ecommerce_sales), 2) AS revenue_share_pct
FROM customer_order_counts
GROUP BY 
    CASE 
        WHEN order_count = 1 THEN 'One-Time Buyer'
        WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional Repeat (2-4 Orders)'
        WHEN order_count BETWEEN 5 AND 9 THEN 'Frequent Buyer (5-9 Orders)'
        ELSE 'Super VIP (10+ Orders)'
    END
ORDER BY total_revenue_generated DESC;


-- ------------------------------------------------------------------------------
-- Query 13: Discount Depth vs. Profitability Impact
-- ------------------------------------------------------------------------------
-- Business Question: How do higher discount rates impact overall profit margins?
SELECT 
    CASE 
        WHEN discount = 0.00 THEN '0% (Full Price)'
        WHEN discount > 0.00 AND discount <= 0.10 THEN '1% - 10% (Low Discount)'
        WHEN discount > 0.10 AND discount <= 0.20 THEN '11% - 20% (Moderate Discount)'
        ELSE '21%+ (Deep Discount)'
    END AS discount_bracket,
    COUNT(order_id) AS total_transactions,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS realized_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    CASE 
        WHEN discount = 0.00 THEN '0% (Full Price)'
        WHEN discount > 0.00 AND discount <= 0.10 THEN '1% - 10% (Low Discount)'
        WHEN discount > 0.10 AND discount <= 0.20 THEN '11% - 20% (Moderate Discount)'
        ELSE '21%+ (Deep Discount)'
    END
ORDER BY realized_margin_pct DESC;


-- ------------------------------------------------------------------------------
-- Query 14: Underperforming Products (High Sales Volume, Lower Profitability Margins)
-- ------------------------------------------------------------------------------
-- Business Question: Which products generate high revenue but sub-par profit margins?
SELECT 
    product_name,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY product_name, category
HAVING SUM(sales) > 3000 AND (SUM(profit) / SUM(sales)) * 100.0 < 35.0
ORDER BY profit_margin_pct ASC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- Query 15: Payment Method Market Share and Value
-- ------------------------------------------------------------------------------
-- Business Question: What is the preferred payment method and average transaction value?
SELECT 
    payment_method,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(COUNT(DISTINCT order_id) * 100.0 / (SELECT COUNT(DISTINCT order_id) FROM fact_ecommerce_sales), 2) AS transaction_share_pct,
    ROUND(SUM(sales), 2) AS total_volume_sales,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_transaction_value
FROM fact_ecommerce_sales
GROUP BY payment_method
ORDER BY total_volume_sales DESC;


-- ------------------------------------------------------------------------------
-- Query 16: City-Level Revenue & Profit Efficiency
-- ------------------------------------------------------------------------------
-- Business Question: What are the top 10 most profitable metropolitan markets?
SELECT 
    region,
    city,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS city_revenue,
    ROUND(SUM(profit), 2) AS city_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS city_margin_pct
FROM fact_ecommerce_sales
GROUP BY region, city
ORDER BY city_profit DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- Query 17: Quarterly Performance Comparison
-- ------------------------------------------------------------------------------
-- Business Question: How does revenue and profit trend on a quarterly basis?
SELECT 
    SUBSTR(order_date, 1, 4) AS order_year,
    CASE 
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    COUNT(DISTINCT order_id) AS order_volume,
    ROUND(SUM(sales), 2) AS quarterly_revenue,
    ROUND(SUM(profit), 2) AS quarterly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS quarterly_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    SUBSTR(order_date, 1, 4),
    CASE 
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END
ORDER BY order_year ASC, quarter ASC;


-- ------------------------------------------------------------------------------
-- Query 18: Pareto 80/20 Cumulative Product Revenue Contribution
-- ------------------------------------------------------------------------------
-- Business Question: What percentage of products account for 80% of total revenue?
WITH product_totals AS (
    SELECT 
        product_name,
        category,
        ROUND(SUM(sales), 2) AS product_sales
    FROM fact_ecommerce_sales
    GROUP BY product_name, category
),
ranked_products AS (
    SELECT 
        product_name,
        category,
        product_sales,
        SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sales,
        SUM(product_sales) OVER () AS total_enterprise_sales
    FROM product_totals
)
SELECT 
    product_name,
    category,
    product_sales,
    ROUND(cumulative_sales, 2) AS running_cumulative_sales,
    ROUND((cumulative_sales / total_enterprise_sales) * 100.0, 2) AS cumulative_revenue_percentage
FROM ranked_products
LIMIT 20;


-- ------------------------------------------------------------------------------
-- Query 19: High-Ticket vs Low-Ticket Product Margin Comparison
-- ------------------------------------------------------------------------------
-- Business Question: How do high unit price items compare to low unit price items in volume and margin?
SELECT 
    CASE 
        WHEN unit_price < 50.00 THEN '1. Low (< $50)'
        WHEN unit_price BETWEEN 50.00 AND 200.00 THEN '2. Medium ($50 - $200)'
        WHEN unit_price BETWEEN 200.01 AND 600.00 THEN '3. High ($200 - $600)'
        ELSE '4. Premium (> $600)'
    END AS price_bracket,
    COUNT(order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS price_tier_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    CASE 
        WHEN unit_price < 50.00 THEN '1. Low (< $50)'
        WHEN unit_price BETWEEN 50.00 AND 200.00 THEN '2. Medium ($50 - $200)'
        WHEN unit_price BETWEEN 200.01 AND 600.00 THEN '3. High ($200 - $600)'
        ELSE '4. Premium (> $600)'
    END
ORDER BY price_bracket ASC;


-- ------------------------------------------------------------------------------
-- Query 20: Customer RFM Scoring and Segmentation Distribution
-- ------------------------------------------------------------------------------
-- Business Question: What is the monetary contribution across RFM customer tiers?
WITH rfm_raw AS (
    SELECT 
        customer_id,
        customer_name,
        customer_segment,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(sales) AS monetary,
        SUM(profit) AS total_profit
    FROM fact_ecommerce_sales
    GROUP BY customer_id, customer_name, customer_segment
)
SELECT 
    CASE 
        WHEN frequency >= 8 AND monetary >= 2500 THEN 'Tier 1: VIP Champions'
        WHEN frequency >= 5 AND monetary >= 1500 THEN 'Tier 2: Loyal Core'
        WHEN frequency >= 3 THEN 'Tier 3: Regular Buyers'
        ELSE 'Tier 4: Casual / Occasional'
    END AS rfm_customer_tier,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(frequency), 1) AS avg_orders,
    ROUND(SUM(monetary), 2) AS total_segment_spend,
    ROUND(SUM(total_profit), 2) AS total_segment_profit,
    ROUND((SUM(total_profit) / SUM(monetary)) * 100.0, 2) AS segment_profit_margin_pct
FROM rfm_raw
GROUP BY 
    CASE 
        WHEN frequency >= 8 AND monetary >= 2500 THEN 'Tier 1: VIP Champions'
        WHEN frequency >= 5 AND monetary >= 1500 THEN 'Tier 2: Loyal Core'
        WHEN frequency >= 3 THEN 'Tier 3: Regular Buyers'
        ELSE 'Tier 4: Casual / Occasional'
    END
ORDER BY total_segment_spend DESC;
