select * from Electric_Vehicle_Population_Data;

-- 1. KPI

-- Avergae Electic Vehicle Range

alter table Electric_Vehicle_Population_Data
alter column Electric_Range float;

select cast(avg(Electric_Range) as decimal(10,2)) as Avg_Electric_Range
from Electric_Vehicle_Population_Data;

-- Total Electric Vehicles

select count(*) as Total_Vehicles
from Electric_Vehicle_Population_Data;

-- Total Vehicle by Vehicle Type (BEV/ PHEV)

select Electric_Vehicle_Type ,count(*) as Total_Vehicles, cast(count(*) *100.0 /sum(count(*)) over() as decimal(10,2)) as Vehicle_Percentage
from Electric_Vehicle_Population_Data
group by Electric_Vehicle_Type;

-- 2. Total Vehicles by Model Year from 2012

select Model_Year, count(DOL_Vehicle_ID) as Total_Vehicles
from Electric_Vehicle_Population_Data
where Model_Year >= 2012
group by Model_Year
order by Model_Year;

-- 3. Total Vehicles by States

select State, count(DOL_Vehicle_ID) as Total_Vehicles
from Electric_Vehicle_Population_Data
group by State
order by Total_Vehicles desc;

-- 4. Total Vehicles by Make

select Make, count(DOL_Vehicle_ID) as Total_Vehicles, cast(count(*) *100.0 /sum(count(*)) over() as decimal(10,2)) as Vehicle_Percentage
from Electric_Vehicle_Population_Data
group by Make
order by Total_Vehicles desc;

-- 5. Total Vehicles 

select Clean_Alternative_Fuel_Vehicle_CAFV_Eligibility, count(DOL_Vehicle_ID) as Total_Vehicles, cast(count(*) *100.0 /sum(count(*)) over() as decimal(10,2)) as Vehicle_Percentage
from Electric_Vehicle_Population_Data
group by Clean_Alternative_Fuel_Vehicle_CAFV_Eligibility
order by Total_Vehicles desc;

-- 6. Total Vehicles by Model

select Model, Make, Electric_Vehicle_Type, count(DOL_Vehicle_ID) as Total_Vehicles, cast(count(*) *100.0 /sum(count(*)) over() as decimal(10,2)) as Vehicle_Percentage
from Electric_Vehicle_Population_Data
group by Model, Make, Electric_Vehicle_Type
order by Total_Vehicles desc;