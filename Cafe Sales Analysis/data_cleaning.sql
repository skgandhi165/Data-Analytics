SELECT * FROM coffee_shop_sales

DESCRIBE coffee_shop_sales

UPDATE coffee_shop_sales
SET transaction_date = STR_TO_DATE(transaction_date, "%Y-%m-%d");

ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_date date;

UPDATE coffee_shop_sales
SET transaction_time = STR_TO_DATE(transaction_time, "%H:%i:%s");

ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_time time;

ALTER TABLE coffee_shop_sales
CHANGE COLUMN ï»¿transaction_id transaction_id int;