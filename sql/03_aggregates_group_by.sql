-- Query 5 — Aggregate functions over the catalogue (COUNT, AVG, MIN, MAX).
SELECT COUNT(*) AS song_count,
       ROUND(AVG(duration_seconds), 1) AS average_seconds,
       MIN(duration_seconds) AS shortest_seconds,
       MAX(duration_seconds) AS longest_seconds
FROM catalog_song;

-- Query 6 — Count songs assigned to each genre (GROUP BY).
SELECT g.name AS genre,
       COUNT(DISTINCT sg.song_id) AS song_count
FROM catalog_genre AS g
LEFT JOIN catalog_songgenre AS sg ON sg.genre_id = g.id
GROUP BY g.id, g.name
ORDER BY song_count DESC, g.name;
