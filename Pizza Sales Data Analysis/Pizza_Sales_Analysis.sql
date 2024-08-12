select * from pizza_sales;

-- 1. KPI

-- Total Revenue

select SUM(total_price) AS Total_Revenue 
from pizza_sales;

-- Average Order Value

select sum(total_price) / COUNT(DISTINCT order_id) AS Avg_Order_Value 
from pizza_sales;

-- Total Quantity Sold

select sum(quantity) AS Total_Qty_Sold 
from pizza_sales;

-- Total Orders Placed

select COUNT(DISTINCT order_id) AS Total_Orders 
from pizza_sales;
 
-- Average Pizzas per Order

select CAST(CAST(SUM(quantity) AS DECIMAL(10,2))/ CAST(COUNT (DISTINCT order_id) AS decimal(10,2)) AS decimal(10,2)) as Avg_Pizza_Per_Order 
from pizza_sales;

-- 2. Daily Trends for Total Orders

select DATENAME(DW, order_date) AS Order_day, COUNT(DISTINCT order_id) AS Total_orders 
from pizza_sales
GROUP BY DATENAME(DW, order_date);

-- 3. Monthly Trend for Total Orders

select DATENAME(MONTH, order_date) AS Order_month, COUNT(DISTINCT order_id) AS Total_orders 
from pizza_sales
GROUP BY DATENAME(MONTH, order_date);

-- 4. Percentage of Pizza Sales by Category

select pizza_category, sum(total_price) * 100/ (select sum(total_price) from pizza_sales) as Total_sales_percentage
from pizza_sales
group by pizza_category;

-- The percentage of sales by category for a particular month (E.g. January)

select pizza_category, sum(total_price) * 100/ (select sum(total_price) from pizza_sales where MONTH(order_date) = 1) as Total_sales_percentage
from pizza_sales
where MONTH(order_date) = 1
group by pizza_category;

-- 5. Percentage of Pizza Sales by Size

select pizza_size, sum(total_price) * 100/ (select sum(total_price) from pizza_sales) as Total_sales_percentage
from pizza_sales
group by pizza_size
order by Total_sales_percentage desc;

-- 6. Total Pizza Sold by Category

select pizza_category, sum (quantity) as Total_Qty_Sold
from pizza_sales
group by pizza_category
order by Total_Qty_Sold desc;

-- 7. Top 5 Pizza Sold by Revenue

select top 5 pizza_name, sum(total_price) as Total_Revenue 
from pizza_sales
group by pizza_name
order by Total_Revenue desc;

-- 8. Bottom 5 Pizza Sold by Revenue

select top 5 pizza_name, sum(total_price) as Total_Revenue 
from pizza_sales
group by pizza_name
order by Total_Revenue;

-- 9. Top 5 Pizza sold by total Qty

select top 5 pizza_name, sum(quantity) as Total_Qty
from pizza_sales
group by pizza_name
order by Total_Qty desc;

-- 10. Bottom 5 Pizza sold by Total Qty

select top 5 pizza_name, sum(quantity) as Total_Qty
from pizza_sales
group by pizza_name
order by Total_Qty;

-- 11. Top 5 Pizza Sold by Total Number of Orders

select top 5 pizza_name, count(distinct order_id) as Total_Orders
from pizza_sales
group by pizza_name
order by Total_Orders desc;

-- 12. Bottom 5 Pizza Sold by Total Number of Orders

select top 5 pizza_name, count(distinct order_id) as Total_Orders
from pizza_sales
group by pizza_name
order by Total_Orders;