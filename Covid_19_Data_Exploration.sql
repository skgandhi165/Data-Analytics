Select *
From CovidDeaths 
order by 3,4;

-- Select Data that we are going to be starting with

Select location, date, total_cases, new_cases, total_deaths, population
From CovidDeaths
Where continent is not null 
order by 1,2;

-- Total Cases vs Total Deaths
-- Shows likelihood of dying if you contract covid in your country

Select Location, date, total_cases,total_deaths, CAST((total_deaths/total_cases)*100.00 AS decimal(10,3)) as Death_Percentage
From CovidDeaths
--Where location like '%states%'
order by 1,2;

-- Total Cases vs Population
-- Shows what percentage of population infected with Covid

Select location, date, population, total_cases,  CAST((total_cases/population)*100.00 AS decimal(10,3)) as Percent_Population_Infected
From CovidDeaths
--Where location like '%states%'
order by 1,2;


-- Countries with Highest Infection Rate compared to Population

Select location, population, MAX(total_cases) as HighestInfectionCount,  CAST(Max((total_cases/population))*100.00 AS decimal(10,3)) as Percent_Population_Infected
From CovidDeaths
--Where location like '%states%'
Group by Location, Population
order by Percent_Population_Infected desc;

-- Countries with Highest Death Count per Population

Select location, MAX(Total_deaths) as Total_Death_Count
From CovidDeaths
Where continent is not null 
Group by location
order by Total_Death_Count desc;

-- BREAKING THINGS DOWN BY CONTINENT

-- Showing contintents with the highest death count per population

Select continent, MAX(Total_deaths) as TotalDeathCount
From CovidDeaths
Where continent is not null 
Group by continent
order by TotalDeathCount desc;

-- GLOBAL NUMBERS

Select SUM(new_cases) as total_cases, SUM(new_deaths) as total_deaths, cast(SUM(new_deaths)/SUM(New_Cases)*100.00 as decimal(10,3)) as DeathPercentage
From CovidDeaths
where continent is not null 
--Group By date
order by 1,2;

-- Total Population vs Vaccinations
-- Shows Percentage of Population that has recieved at least one Covid Vaccine

Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(cast(vac.new_vaccinations as int)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
From CovidDeaths dea
Join CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
order by 2,3;

-- Using CTE to perform Calculation on Partition By in previous query

With PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingPeopleVaccinated)
as
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
From CovidDeaths dea
Join CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
--order by 2,3
)
Select *, cast((RollingPeopleVaccinated/Population)*100.00 as decimal(10,3)) as Percent_Population_Vaccinated
From PopvsVac;

--OR

-- Using Temp Table to perform Calculation on Partition By in previous query

DROP Table if exists PercentPopulationVaccinated
Create Table PercentPopulationVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingPeopleVaccinated numeric
)

Insert into PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
From CovidDeaths dea
Join CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
--where dea.continent is not null 
--order by 2,3

Select *,  cast((RollingPeopleVaccinated/Population)*100.00 as decimal(10,3)) as Percent_Population_Vaccinated
From PercentPopulationVaccinated;