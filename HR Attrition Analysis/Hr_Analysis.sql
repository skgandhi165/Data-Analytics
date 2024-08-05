select * from HR_data;

-- 1. KPI

-- Total Number of Employees 

select count(*) as Total_Employees 
from HR_data;

-- Total Attrition 

select count(*) as Total_Attrition
from HR_data
where Attrition like 'Yes';

-- Total Active Employees

select count(*) as Total_Active_Employees
from HR_data
where Attrition like 'No';

-- Rate of attrition

select top 1 cast(count(*) *100.0 /sum(count(*)) over() as decimal(10,2)) as Attrition_Rate
from HR_data
group by Attrition;

-- Average Age of Active Employees

select AVG(Age) as Average_Age
from HR_data
where Attrition like 'No';

-- 2. Attrition by Gender

select Gender, count(*) as Total_Attrition
from HR_data
where Attrition like 'Yes'
group by Gender;

-- 3. Attrition by Department

select Department, count(*) as Total_Attrition, CAST( count(*) * 100.0 / SUM(COUNT(*)) over() as decimal(10,2)) as Attrition_Rate
from HR_data
where Attrition like 'Yes'
group by Department;

-- 4. Number of Employees by age group	

-- 5. Job Satisfaction Rating of all Employees

select Job_Role, Job_Satisfaction, count(*) as Total_Attrition
from HR_data
group by Job_Role, Job_Satisfaction
order by Job_Satisfaction;

-- 6. Attrition by Education Field

select Education_Field, count(*) as Total_Attrition
from HR_data
where Attrition like 'Yes'
group by Education_Field
order by Total_Attrition desc;

-- 7. Attrition based on Gender for different age groups

select Gender, CF_age_band, count(*) as Total_Attrition, CAST( count(*) * 100.0 / SUM(COUNT(*)) over() as decimal(10,2)) as Attrition_Rate
from HR_data
where Attrition like 'Yes'
group by Gender, CF_age_band;
