Select * from coffee_shop_sales

-- First let's do some data cleaning

-- change the name and datatype of trasaction date column

UPDATE coffee_shop_sales
SET transaction_date = STR_TO_DATE(transaction_date, "%Y-%m-%d");

ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_date date;

-- change the name and datatype of trasaction time column

UPDATE coffee_shop_sales
SET transaction_time = STR_TO_DATE(transaction_time, "%H:%i:%s");

ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_time time;

-- Now we find the KPI which gives us vital information about the sales of the cafe

Select * from coffee_shop_sales;

-- Find the Total Sales of each month (For eg. May)

Select CONCAT((ROUND(SUM(unit_price * transaction_qty)))/1000, "K") AS Total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- Find the month to month increase or decrease in sales (For eg. April and may)

Select 
    MONTH(transaction_date) AS month, -- Number of month
    ROUND(SUM(unit_price * transaction_qty)) AS total_sales, -- total sales
    (SUM(unit_price * transaction_qty) - LAG(SUM(unit_price * transaction_qty), 1) -- month to month sales difference where lag is used to go to the previous month
    OVER (order by MONTH(transaction_date))) / LAG(SUM(unit_price * transaction_qty), 1) -- division by previous month sales
    OVER (order by MONTH(transaction_date)) * 100 AS mom_increase_percentage -- get the percentage sales increase with respect to previous month
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5) -- for months of April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

-- Find the difference in sales between the selected month and previous month (For Eg. April and May)

Select 
    MONTH(transaction_date) AS month, 
    ROUND(SUM(unit_price * transaction_qty)) AS total_sales, 
	ROUND((SUM(unit_price * transaction_qty) - LAG(SUM(unit_price * transaction_qty), 1) 
    OVER (order by MONTH(transaction_date)))) AS mom_sales_difference
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5) -- for months of April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

-- Find the total number of orders for each month (For Eg. May)

Select COUNT(*) AS Total_orders
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- Find the month to month increase or decrease in number of orders (For eg. April and may)

Select 
    MONTH(transaction_date) AS month,
    ROUND(COUNT(transaction_id)) AS total_orders,
    (COUNT(transaction_id) - LAG(COUNT(transaction_id), 1) 
    OVER (order by MONTH(transaction_date))) / LAG(COUNT(transaction_id), 1) 
    OVER (order by MONTH(transaction_date)) * 100 AS mom_increase_percentage
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5) -- for April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

-- Find the difference in number of orders between the selected month and previous month (For Eg. April and May)

Select 
    MONTH(transaction_date) AS month,
    ROUND(COUNT(transaction_id)) AS total_orders,
    (COUNT(transaction_id) - LAG(COUNT(transaction_id), 1) 
    OVER (order by MONTH(transaction_date))) AS mom_order_difference
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5) -- for April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

-- Find the total Qty Sold for each month (For Eg. May)

Select SUM(transaction_qty) AS Total_qty_sold
from coffee_shop_sales
where MONTH(transaction_date) = 5; -- May Month

-- Find the month to month increase or decrease in total Qty sold (For eg. April and may)

Select 
    MONTH(transaction_date) AS month,
    ROUND(SUM(transaction_qty)) AS total_quantity_sold,
    (SUM(transaction_qty) - LAG(SUM(transaction_qty), 1) 
    OVER (order by MONTH(transaction_date))) / LAG(SUM(transaction_qty), 1) 
    OVER (order by MONTH(transaction_date)) * 100 AS mom_increase_percentage
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5)   -- for April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

-- Find the difference in total Qty sold between the selected month and previous month (For Eg. April and May)

Select 
    MONTH(transaction_date) AS month,
    ROUND(SUM(transaction_qty)) AS total_quantity_sold,
    (SUM(transaction_qty) - LAG(SUM(transaction_qty), 1) 
    OVER (order by MONTH(transaction_date))) AS mom_Qty_increase
from coffee_shop_sales
where MONTH(transaction_date) IN (4, 5)   -- for April and May
group by MONTH(transaction_date)
order by MONTH(transaction_date);

Select * from coffee_shop_sales;

-- Find daily sales, number of orders and total Qty sold (For Eg. May 18 2023)

Select 
	ROUND(SUM(transaction_qty * unit_price)) AS Total_sales,
    SUM(transaction_qty) AS Total_Qty_Sold,
    count(transaction_id) AS Total_Orders
from coffee_shop_sales
where transaction_date = '2023-05-18';

-- Find total Sales for WEEKDAYS and WEEKENDS (Sunday = 1, .... Saturday = 7)

Select 
	CASE WHEN dayofweek(transaction_date) IN (1,7) THEN 'Weekends'
    ELSE 'Weekdays'
    END AS day_type,
    ROUND(SUM(transaction_qty * unit_price)) AS Total_sales
fromcoffee_shop_sales
where month(transaction_date) = 5
group by day_type;

-- Find total Sales by store Location for each month (For Eg. May)

Select 
	store_location,
    ROUND(SUM(transaction_qty * unit_price)) AS Total_sales
from coffee_shop_sales
where month(transaction_date) = 5
group by store_location;

-- Find Avg Sales Trend Over a period/Month (For Eg. May)

Select ROUND(AVG(total_sales)) AS average_sales
from (
    Select 
        SUM(unit_price * transaction_qty) AS total_sales
    from coffee_shop_sales
	where MONTH(transaction_date) = 5  -- Filter for May
    group by transaction_date
) AS internal_query;

-- Find Daily total sales for a particular month (For Eg. May)

Select
	DAY(transaction_date) AS Day_of_month,
    ROUND(SUM(unit_price*transaction_qty)) AS Total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5  -- Filter for May
group by Day_of_month;

-- Comapre Daily total sales with the Avg sales of that month to find if its 'Above Avg' or 'Below Avg' (For Eg. May)

Select 
    day_of_month,
    CASE 
        WHEN total_sales > avg_sales THEN 'Above Average'
        WHEN total_sales < avg_sales THEN 'Below Average'
        ELSE 'Average'
    END AS sales_status,
    total_sales
from (
    Select 
        DAY(transaction_date) AS day_of_month,
        SUM(unit_price * transaction_qty) AS Total_sales,
        AVG(SUM(unit_price * transaction_qty)) OVER () AS avg_sales
    from coffee_shop_sales
    where MONTH(transaction_date) = 5  -- Filter for May
    group by DAY(transaction_date)
) AS sales_data
order by day_of_month;

-- Find total sales With respect to each product category for each month (For Eg. May)

Select
	product_category,
    round(SUM(unit_price * transaction_qty)) AS total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5 
group by product_category;

-- Find top 10 product by sales for each month (For Eg. May)

Select
	product_type,
    round(SUM(unit_price * transaction_qty)) AS Total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5 
group by product_type
order by total_sales desc
limit 10;

-- Find total sales by each hour of the day for each month (For Eg. 3 May at 8:00 am)
Select 
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales,
    SUM(transaction_qty) AS Total_Quantity,
    COUNT(*) AS Total_Orders
from coffee_shop_sales
where DAYOFWEEK(transaction_date) = 3 -- Filter for Tuesday (1 is Sunday, 2 is Monday, ..., 7 is Saturday)
and HOUR(transaction_time) = 8 -- Filter for hour number 8
and MONTH(transaction_date) = 5; -- Filter for May (month number 5)

-- Find total sales from monday to sunday for each month (For Eg. May)

Select 
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
from coffee_shop_sales
where MONTH(transaction_date) = 5 -- Filter for May (month number 5)
group by Day_of_Week;

-- Find total sales for all hours for each month (For Eg. May)

Select 
    HOUR(transaction_time) AS Hour_of_Day,
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales
from coffee_shop_sales
where MONTH(transaction_date) = 5 -- Filter for May (month number 5)
group by HOUR(transaction_time)
order by HOUR(transaction_time);