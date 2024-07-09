select genre_id from track limit 100;
describe track;
select genre_id from track;
select genre_id from genre;
-- checking if i have genre ID is available in the track table
SELECT DISTINCT genre_id
FROM genre
WHERE genre_id NOT IN (SELECT genre_id FROM track);
-- it appears that i have null values in the genre id column in my track table 
-- in order to fix this i will use the JSON in genre_ handle in the track table to get a genre_id usable 
SELECT track_id, track_genres
FROM track
LIMIT 10;
-- observed JSON data has quoation marks in the JSON 
SET SQL_SAFE_UPDATES = 0;
SELECT track_id, track_genres
FROM track
LIMIT 10;

UPDATE track
SET genre_id = JSON_UNQUOTE(JSON_EXTRACT(track_genres, '$[0].genre_id'));

SELECT track_id, track_genres, genre_id
FROM track
LIMIT 100;
-- checking if the foreign key paremeter was fullfiled 
describe track;
-- checking that the genre_id key is working random number to just test if it exists
select 
track.track_id,
track.track_title,
genre.genre_handle, 
track.genre_id,
genre.genre_id
from track
join genre on track.genre_id=genre.genre_id
where track.genre_id= 15;

select distinct genre_id,genre_handle from genre;
select distinct genre_id from track;
-- checking for nulls and missing tracks genre classification
SELECT DISTINCT genre_id
FROM track
WHERE genre_id NOT IN (SELECT genre_id FROM genre);

-- working on SQL queries for the distinct information to expose on the API that i will create 
-- generic song query to be used to get standard song information 
SELECT
t.track_id,
t.track_title,
a.artist_name,
g.genre_handle,
g.genre_id,
a.album_handle
FROM track t
inner join genre g on t.genre_id= g.genre_id
inner join album a on t.album_id = a.album_id;

alter table track drop column track_genres;

select * from track limit 100;
select * from echonest limit 10;

-- distinct count of generes and the number of songs in it and the average features in the genres 
-- creating a view of genre features usings genre and echonest average features

drop view genre_feature;
CREATE VIEW genre_feature as 
SELECT
	g.genre_id,
    g.genre_handle,
    COUNT(DISTINCT a.album_id) AS num_albums,
    COUNT(DISTINCT t.track_id) AS num_songs,
    AVG(e.acousticness) AS avg_acousticness,
    AVG(e.danceability) AS avg_danceability,
    AVG(e.energy) AS avg_energy,
    AVG(e.instrumentalness) AS avg_instrumentalness,
    AVG(e.liveness) AS avg_liveness,
    AVG(e.speechiness) AS avg_speechiness,
    AVG(e.tempo) AS avg_tempo,
    AVG(e.valence) AS avg_valence
FROM
    genre g
JOIN
    track t ON g.genre_id = t.genre_id
JOIN
    echonest e ON t.track_id = e.track_id
JOIN
    album a ON t.album_id = a.album_id
GROUP BY
    g.genre_handle, g.genre_id
ORDER BY
    g.genre_id;

-- using the view
select * from genre_feature;
-- dtopping track colulmns that have alot of NA 

select 
track_explicit,
track_explicit_notes,
track_publisher,
track_copyright_c,
track_copyright_p,
track_composer,
artist.artist_name
from 
track
join artist on track.artist_id = artist.artist_id
where track.track_composer is not NULL;

SET SESSION group_concat_max_len = 1000000;

-- Step 1: Create a variable to store the dynamic SQL statement
SET @sql = '';

-- Step 2: Generate the ALTER TABLE statement for each column
SELECT GROUP_CONCAT(CONCAT('DROP COLUMN `', COLUMN_NAME, '`') SEPARATOR ', ')
INTO @sql
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'echonest'
AND COLUMN_NAME REGEXP '^[0-9]+$'
AND CAST(COLUMN_NAME AS UNSIGNED) BETWEEN 0 AND 223;

-- Step 3: Prepare the final ALTER TABLE statement
SET @sql = CONCAT('ALTER TABLE echonest ', @sql);

-- Step 4: Execute the dynamic SQL statement
SET @alter_stmt = CONCAT('ALTER TABLE echonest ', @sql);
PREPARE stmt FROM @alter_stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
describe track;

-- number of tracks per genre
SELECT g.genre_title, COUNT(t.track_id) AS track_count
FROM track t
JOIN genre g ON t.genre_id = g.genre_id
GROUP BY g.genre_title
ORDER BY track_count DESC;
-- average tempo by album
SELECT a.album_title, AVG(e.tempo) AS average_tempo
FROM track t
JOIN album a ON t.album_id = a.album_id
JOIN echonest e ON t.track_id = e.track_id
GROUP BY a.album_title
ORDER BY average_tempo Asc;
-- top ten albums with the most tracks in the data set
SELECT a.album_title, COUNT(t.track_id) AS track_count
FROM track t
JOIN album a ON t.album_id = a.album_id
GROUP BY a.album_title
ORDER BY track_count DESC
LIMIT 10;
-- art with. the most albums 
SELECT ar.artist_name, COUNT(DISTINCT al.album_id) AS album_count
FROM album al
JOIN track t ON al.album_id = t.track_id
join artist ar on t.artist_id = ar.artist_id
GROUP BY ar.artist_name
ORDER BY album_count DESC
LIMIT 1;

