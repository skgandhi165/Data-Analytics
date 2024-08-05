SELECT * FROM coffee_shop_sales;

-- CALENDAR TABLE – DAILY SALES, QUANTITY and TOTAL ORDERS
SELECT 
	ROUND(SUM(transaction_qty * unit_price)) AS Total_sales,
    SUM(transaction_qty) AS Total_Qty_Sold,
    count(transaction_id) AS Total_Orders
FROM coffee_shop_sales
WHERE 
	transaction_date = '2023-05-18';

-- Sales Analysis for WEEKDAYS and WEEKENDS 
-- For day number - Sun = 1, ......, Sat = 7
SELECT 
	CASE WHEN dayofweek(transaction_date) IN (1,7) THEN 'Weekends'
    ELSE 'Weekdays'
    END AS day_type,
    ROUND(SUM(transaction_qty * unit_price)) AS Total_sales
FROM
	coffee_shop_sales
WHERE
	month(transaction_date) = 5
GROUP BY day_type;

-- Sales analysis by store Location
SELECT 
	store_location,
    ROUND(SUM(transaction_qty * unit_price)) AS Total_sales
FROM 
	coffee_shop_sales
WHERE
	month(transaction_date) = 5
GROUP BY store_location;

-- Sales Trend Over a period
SELECT ROUND(AVG(total_sales)) AS average_sales
FROM (
    SELECT 
        SUM(unit_price * transaction_qty) AS total_sales
    FROM 
        coffee_shop_sales
	WHERE 
        MONTH(transaction_date) = 5  -- Filter for May
    GROUP BY 
        transaction_date
) AS internal_query;

-- Daily sales for a particular month
SELECT
	DAY(transaction_date) AS Day_of_month,
    ROUND(SUM(unit_price*transaction_qty)) AS Total_Sales
FROM 
        coffee_shop_sales
	WHERE 
        MONTH(transaction_date) = 5  -- Filter for May
    GROUP BY 
        Day_of_month;

-- COMPARING DAILY SALES WITH AVERAGE SALES – IF GREATER THAN “ABOVE AVERAGE” and LESSER THAN “BELOW AVERAGE”
SELECT 
    day_of_month,
    CASE 
        WHEN total_sales > avg_sales THEN 'Above Average'
        WHEN total_sales < avg_sales THEN 'Below Average'
        ELSE 'Average'
    END AS sales_status,
    total_sales
FROM (
    SELECT 
        DAY(transaction_date) AS day_of_month,
        SUM(unit_price * transaction_qty) AS Total_sales,
        AVG(SUM(unit_price * transaction_qty)) OVER () AS avg_sales
    FROM 
        coffee_shop_sales
    WHERE 
        MONTH(transaction_date) = 5  -- Filter for May
    GROUP BY 
        DAY(transaction_date)
) AS sales_data
ORDER BY 
    day_of_month;

-- Sales With respect to product category
SELECT
	product_category,
    round(SUM(unit_price * transaction_qty)) AS total_Sales
FROM 
	coffee_shop_sales
WHERE 
	MONTH(transaction_date) = 5 
GROUP BY product_category;

-- Top 10 product by sales
SELECT
	product_type,
    round(SUM(unit_price * transaction_qty)) AS Total_Sales
FROM 
	coffee_shop_sales
WHERE 
	MONTH(transaction_date) = 5 
GROUP BY product_type
ORDER BY total_sales desc
limit 10;

-- SALES ANALYSIS by Days and Hours

-- Sales by day/hour
SELECT 
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales,
    SUM(transaction_qty) AS Total_Quantity,
    COUNT(*) AS Total_Orders
FROM 
    coffee_shop_sales
WHERE 
    DAYOFWEEK(transaction_date) = 3 -- Filter for Tuesday (1 is Sunday, 2 is Monday, ..., 7 is Saturday)
    AND HOUR(transaction_time) = 8 -- Filter for hour number 8
    AND MONTH(transaction_date) = 5; -- Filter for May (month number 5)

-- SALES FROM MONDAY TO SUNDAY FOR MONTH OF MAY
SELECT 
    CASE 
        WHEN DAYOFWEEK(transaction_date) = 2 THEN 'Monday'
        WHEN DAYOFWEEK(transaction_date) = 3 THEN 'Tuesday'
        WHEN DAYOFWEEK(transaction_date) = 4 THEN 'Wednesday'
        WHEN DAYOFWEEK(transaction_date) = 5 THEN 'Thursday'
        WHEN DAYOFWEEK(transaction_date) = 6 THEN 'Friday'
        WHEN DAYOFWEEK(transaction_date) = 7 THEN 'Saturday'
        ELSE 'Sunday'
    END AS Day_of_Week,
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) = 5 -- Filter for May (month number 5)
GROUP BY Day_of_Week;

-- SALES FOR ALL HOURS FOR MONTH OF MAY
SELECT 
    HOUR(transaction_time) AS Hour_of_Day,
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) = 5 -- Filter for May (month number 5)
GROUP BY 
    HOUR(transaction_time)
ORDER BY 
    HOUR(transaction_time);