Select count(*)
From layoffs.layoffs;

-- Creating a dummy table to work with and clean the data. The original table with the raw data is preserved in case something goes wrong
Create table layoffs.sample_layoffs 
Like layoffs.layoffs;

Insert into layoffs.sample_layoffs 
Select * From layoffs.layoffs;

-- 1. Remove Duplicates

# First let's check for duplicates

Select *
From layoffs.sample_layoffs;

Select company, industry, total_laid_off,`date`, row_number() over (
			partition by company, industry, total_laid_off,`date`) as row_num
From layoffs.sample_layoffs;

Select *
From (
	Select company, industry, total_laid_off,`date`, row_number() over (
			partition by company, industry, total_laid_off,`date`) as row_num
	From layoffs.sample_layoffs
) duplicates
Where row_num > 1;

-- let's just look at company 'oda' to confirm
Select *
From layoffs.sample_layoffs
Where company = 'Oda';
-- it looks like these are all legitimate entries and shouldn't be deleted. We need to really look at every single row to be accurate

-- these are our real duplicates 
Select *
From (
	Select company, location, industry, total_laid_off,percentage_laid_off,`date`, stage, country, funds_raised_millions, row_number() over (
			partition by company, location, industry, total_laid_off,percentage_laid_off,`date`, stage, country, funds_raised_millions) as row_num
	From layoffs.sample_layoffs
) duplicates
Where row_num > 1;

-- one solution, which I think is a good one. Is to create a new column and add those row numbers in. Then delete Where row numbers are over 2, then delete that column
-- so let's do it!!

Alter table layoffs.sample_layoffs 
ADD row_num INT;

Select *
From layoffs.sample_layoffs;

CREATE table `layoffs`.`sample_layoffs2` (
`company` text,
`location`text,
`industry`text,
`total_laid_off` int,
`percentage_laid_off` text,
`date` text,
`stage`text,
`country` text,
`funds_raised_millions` int,
row_num int
);

INSERT INTO `layoffs`.`sample_layoffs2`
(`company`,
`location`,
`industry`,
`total_laid_off`,
`percentage_laid_off`,
`date`,
`stage`,
`country`,
`funds_raised_millions`,
`row_num`)
Select `company`,
`location`,
`industry`,
`total_laid_off`,
`percentage_laid_off`,
`date`,
`stage`,
`country`,
`funds_raised_millions`,
		row_number() over (
			partition by company, location, industry, total_laid_off,percentage_laid_off,`date`, stage, country, funds_raised_millions
			) as row_num
	From layoffs.sample_layoffs;
    
Select *
From layoffs.sample_layoffs2;

-- now that we have this we can delete rows were row_num is greater than 2

Delete From layoffs.sample_layoffs2
Where row_num >= 2;

-- 2. Standardize Data

-- if we look at industry it looks like we have some null and empty rows, let's take a look at these
Select DISTINCT industry
From layoffs.sample_layoffs2
Order By industry;

Select *
From layoffs.sample_layoffs2
Where industry IS NULL 
or industry = ''
Order By industry;

-- let's take a look at these
Select *
From layoffs.sample_layoffs2
Where company LIKE 'Bally%';

-- nothing wrong here

Select *
From layoffs.sample_layoffs2
Where company LIKE 'airbnb%';

Update layoffs.sample_layoffs2
Set industry = NULL
Where industry = '';

-- now if we check those are all null

Select *
From layoffs.sample_layoffs2
Where industry IS NULL 
or industry = ''
Order By industry;

-- now we need to populate those nulls if possible

Update layoffs.sample_layoffs2 t1
JOIN layoffs.sample_layoffs2 t2
ON t1.company = t2.company
Set t1.industry = t2.industry
Where t1.industry IS NULL
and t2.industry IS NOT NULL;

-- and if we check it looks like Bally's was the only one without a populated row to populate this null values
Select *
From layoffs.sample_layoffs2
Where industry IS NULL 
or industry = ''
Order By industry;

-- I also noticed the Crypto has multiple different variations. We need to standardize that - let's say all to Crypto
Select DISTINCT industry
From layoffs.sample_layoffs2
ORDER BY industry;

Update layoffs.sample_layoffs2
Set industry = 'Crypto'
Where industry IN ('Crypto Currency', 'CryptoCurrency');

-- now that's taken care of:
Select DISTINCT industry
From layoffs.sample_layoffs2
Order By industry;

Select *
From layoffs.sample_layoffs2;

-- everything looks good except apparently we have some "United States" and some "United States." with a period at the end. Let's standardize this.
Select DISTINCT country
From layoffs.sample_layoffs2
Order By country;

Update layoffs.sample_layoffs2
Set country = TRIM(TRAILING '.' From country);

-- now if we run this again it is fixed
Select DISTINCT country
From layoffs.sample_layoffs2
Order By country;

-- Let's also fix the date columns:
-- we can use str to date to update this field
Update layoffs.sample_layoffs2
Set `date` = STR_TO_DATE(`date`, '%m/%d/%Y');

Alter table layoffs.sample_layoffs2
Modify COLUMN `date` DATE;

Select *
From layoffs.sample_layoffs2;

-- 4. remove any columns and rows we need to

Select *
From layoffs.sample_layoffs2
Where total_laid_off IS NULL;

Select *
From layoffs.sample_layoffs2
Where total_laid_off IS NULL
and percentage_laid_off IS NULL;

-- Delete Useless data we can't really use
Delete From layoffs.sample_layoffs2
Where total_laid_off IS NULL
and percentage_laid_off IS NULL;

Select * 
From layoffs.sample_layoffs2;

Alter table layoffs.sample_layoffs2
Drop COLUMN row_num;

Select * 
From layoffs.sample_layoffs2;