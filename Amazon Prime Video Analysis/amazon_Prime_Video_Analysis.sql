select * from amazon_prime_titles

-- 1. Number of total shows by each country

select count(show_id) as no_of_shows, country 
from amazon_prime_titles
where country not like '%,%'
and country is not null
group by country;

-- 2. Display the Name, Description, Cast, Genre, Type, Duration, Release Year of the movie/show selected

select title, description, cast, listed_in as genre, type, duration, release_year
from amazon_prime_titles
group by title, description, cast, listed_in, type, duration, release_year;

-- 3. Worst to Best movie/shows based on ratings

select count(show_id) as no_of_shows, rating
from amazon_prime_titles
where rating is not null
group by rating
order by no_of_shows desc;

-- 4. Dsiplay the top 10 genre of movies/shows

select top 10 count(show_id) as no_of_shows, listed_in as genre
from amazon_prime_titles
group by listed_in
order by No_of_shows desc;

-- 5. Total percentage of shows by type (tv shows/movies)

select type, cast (count(show_id)*100.0 / sum(count(show_id)) over()  as decimal(10,2)) as percentage
from amazon_prime_titles
group by type;

-- 6. No of shows released every year by show type

select release_year, type, count(show_id) as no_of_shows
from amazon_prime_titles
group by release_year, type
order by release_year;