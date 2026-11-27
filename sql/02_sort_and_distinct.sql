-- Query 3 — Show distinct genre names in alphabetical order (DISTINCT, ORDER BY).
SELECT DISTINCT name AS genre_name
FROM catalog_genre
ORDER BY genre_name;

-- Query 4 — Sort the longest tracks first (ORDER BY).
SELECT title, duration_seconds
FROM catalog_song
ORDER BY duration_seconds DESC, title
LIMIT 10;
