-- Customer Segmentation - Dynamic Recency-Monetary-Frequency Scoring view 
USE db_olist_analytics;

-- Remove older view if existed 
DROP VIEW IF EXISTS view_rmf_base; 

-- Recency is calculated using the current date but since this is a project with statis dataset, I'll use the latest date in the dataset.
-- Find the latest date in the dataset to calculate recency.
-- Create the view 
CREATE VIEW view_rmf_base as 
SELECT 
	c.customer_unique_sk,
    -- RECENCY
	DATEDIFF(
		(SELECT 
			GREATEST(
				MAX(order_purchase_timestamp),
				MAX(order_approved_at),
				MAX(order_delivered_carrier_date),
				MAX(order_delivered_customer_date)
                )
		 FROM fct_orders),
         MAX(o.order_purchase_timestamp)
         ) as recency,
	-- Frequecy
    COUNT(o.order_sk) as frequency,
    -- Monetary 
    SUM(i.price) as monetary
FROM dim_customers c 
JOIN fct_orders o ON o.customer_sk = c.customer_sk 
JOIN fct_order_items i ON i.order_sk = o.order_sk 
WHERE o.order_status = 'delivered' 
GROUP BY 1 
ORDER BY 1 ASC
;

SELECT * FROM view_rmf_base;

