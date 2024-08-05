SELECT * FROM coffee_shop_sales;

describe coffee_shop_sales;

-- KPI 1.1
select CONCAT((ROUND(SUM(unit_price * transaction_qty)))/1000, "K") AS Total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- KPI 1.2
SELECT 
    MONTH(transaction_date) AS month, -- Number of month
    ROUND(SUM(unit_price * transaction_qty)) AS total_sales, -- total sales
    (SUM(unit_price * transaction_qty) - LAG(SUM(unit_price * transaction_qty), 1) -- month to month sales difference where lag is used to go to the previous month
    OVER (ORDER BY MONTH(transaction_date))) / LAG(SUM(unit_price * transaction_qty), 1) -- division by previous month sales
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage -- get the percentage sales increase with respect to previous month
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5) -- for months of April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- KPI 1.3
SELECT 
    MONTH(transaction_date) AS month, -- Number of month
    ROUND(SUM(unit_price * transaction_qty)) AS total_sales, -- total sales
	ROUND((SUM(unit_price * transaction_qty) - LAG(SUM(unit_price * transaction_qty), 1) -- month to month sales difference where lag is used to go to the previous month
    OVER (ORDER BY MONTH(transaction_date)))) AS mom_sales_difference
FROM    
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5) -- for months of April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- KPI 2.1
select COUNT(*) AS Total_orders
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- KPI 2.2
SELECT 
    MONTH(transaction_date) AS month,
    ROUND(COUNT(transaction_id)) AS total_orders,
    (COUNT(transaction_id) - LAG(COUNT(transaction_id), 1) 
    OVER (ORDER BY MONTH(transaction_date))) / LAG(COUNT(transaction_id), 1) 
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5) -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- KPI 2.3
SELECT 
    MONTH(transaction_date) AS month,
    ROUND(COUNT(transaction_id)) AS total_orders,
    (COUNT(transaction_id) - LAG(COUNT(transaction_id), 1) 
    OVER (ORDER BY MONTH(transaction_date))) AS mom_order_difference
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5) -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- KPI 3.1
select SUM(transaction_qty) AS Total_qty_sold
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- KPI 3.2
SELECT 
    MONTH(transaction_date) AS month,
    ROUND(SUM(transaction_qty)) AS total_quantity_sold,
    (SUM(transaction_qty) - LAG(SUM(transaction_qty), 1) 
    OVER (ORDER BY MONTH(transaction_date))) / LAG(SUM(transaction_qty), 1) 
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5)   -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- KPI 3.3
SELECT 
    MONTH(transaction_date) AS month,
    ROUND(SUM(transaction_qty)) AS total_quantity_sold,
    (SUM(transaction_qty) - LAG(SUM(transaction_qty), 1) 
    OVER (ORDER BY MONTH(transaction_date))) AS mom_Qty_increase
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5)   -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);
