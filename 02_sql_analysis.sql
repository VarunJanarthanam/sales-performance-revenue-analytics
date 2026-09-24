-- =========================================================================
-- Superstore Sales Performance & Revenue Analytics — SQL Analysis
-- Run against superstore.db (table: orders, one row per order line item)
-- =========================================================================

-- 1. HEADLINE KPIs -------------------------------------------------------
SELECT
    COUNT(DISTINCT "Order ID")                     AS total_orders,
    COUNT(DISTINCT "Customer ID")                   AS total_customers,
    ROUND(SUM(Sales), 2)                            AS total_revenue,
    ROUND(SUM(Profit), 2)                           AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)      AS overall_margin_pct,
    ROUND(SUM(Sales) * 1.0 / COUNT(DISTINCT "Order ID"), 2) AS avg_order_value
FROM orders;


-- 2. REVENUE & PROFIT BY YEAR (year-over-year growth) --------------------
SELECT
    "Order Year"                                    AS year,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)      AS margin_pct,
    COUNT(DISTINCT "Order ID")                      AS orders
FROM orders
GROUP BY "Order Year"
ORDER BY "Order Year";


-- 3. MONTHLY REVENUE TREND (seasonality) ----------------------------------
SELECT
    "Order Year-Month"                              AS month,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit
FROM orders
GROUP BY "Order Year-Month"
ORDER BY "Order Year-Month";


-- 4. PERFORMANCE BY REGION -------------------------------------------------
SELECT
    Region,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)      AS margin_pct,
    COUNT(DISTINCT "Order ID")                      AS orders
FROM orders
GROUP BY Region
ORDER BY revenue DESC;


-- 5. PERFORMANCE BY CATEGORY / SUB-CATEGORY --------------------------------
SELECT
    Category,
    "Sub-Category",
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)      AS margin_pct,
    ROUND(AVG(Discount), 3)                         AS avg_discount
FROM orders
GROUP BY Category, "Sub-Category"
ORDER BY profit ASC;                                -- worst profit first


-- 6. TOP 10 CUSTOMERS BY REVENUE -------------------------------------------
SELECT
    "Customer Name",
    Segment,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    COUNT(DISTINCT "Order ID")                      AS orders
FROM orders
GROUP BY "Customer ID", "Customer Name", Segment
ORDER BY revenue DESC
LIMIT 10;


-- 7. TOP 10 PRODUCTS BY PROFIT, AND BIGGEST LOSS-MAKERS --------------------
SELECT "Product Name", Category,
       ROUND(SUM(Sales),2) AS revenue, ROUND(SUM(Profit),2) AS profit
FROM orders GROUP BY "Product ID", "Product Name", Category
ORDER BY profit DESC LIMIT 10;

SELECT "Product Name", Category,
       ROUND(SUM(Sales),2) AS revenue, ROUND(SUM(Profit),2) AS profit,
       ROUND(AVG(Discount),2) AS avg_discount
FROM orders GROUP BY "Product ID", "Product Name", Category
ORDER BY profit ASC LIMIT 10;


-- 8. DISCOUNT vs PROFITABILITY ---------------------------------------------
-- Buckets discount level to show how margin erodes as discount increases
SELECT
    CASE
        WHEN Discount = 0 THEN '0% (no discount)'
        WHEN Discount <= 0.2 THEN '1-20%'
        WHEN Discount <= 0.4 THEN '21-40%'
        WHEN Discount <= 0.6 THEN '41-60%'
        ELSE '60%+'
    END AS discount_band,
    COUNT(*)                                        AS line_items,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)      AS margin_pct
FROM orders
GROUP BY discount_band
ORDER BY MIN(Discount);


-- 9. SHIP MODE — COST/SPEED TRADEOFF ---------------------------------------
SELECT
    "Ship Mode",
    ROUND(AVG("Days to Ship"), 2)                   AS avg_days_to_ship,
    COUNT(DISTINCT "Order ID")                      AS orders,
    ROUND(SUM(Sales), 2)                            AS revenue
FROM orders
GROUP BY "Ship Mode"
ORDER BY avg_days_to_ship;


-- 10. CUSTOMER SEGMENT PROFITABILITY ----------------------------------------
SELECT
    Segment,
    COUNT(DISTINCT "Customer ID")                   AS customers,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit,
    ROUND(SUM(Sales) * 1.0 / COUNT(DISTINCT "Customer ID"), 2) AS revenue_per_customer
FROM orders
GROUP BY Segment
ORDER BY revenue DESC;


-- 11. RETURN RATE IMPACT ON PROFIT ------------------------------------------
SELECT
    "Is Returned",
    COUNT(DISTINCT "Order ID")                      AS orders,
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit
FROM orders
GROUP BY "Is Returned";


-- 12. STATE-LEVEL LEADERBOARD (top 10 by revenue) ----------------------------
SELECT
    "State/Province",
    ROUND(SUM(Sales), 2)                            AS revenue,
    ROUND(SUM(Profit), 2)                           AS profit
FROM orders
GROUP BY "State/Province"
ORDER BY revenue DESC
LIMIT 10;
