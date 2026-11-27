-- Query 7 — Genres with at least three associated songs (GROUP BY and HAVING).
SELECT g.name AS genre,
       COUNT(DISTINCT sg.song_id) AS song_count
FROM catalog_genre AS g
JOIN catalog_songgenre AS sg ON sg.genre_id = g.id
GROUP BY g.id, g.name
HAVING COUNT(DISTINCT sg.song_id) >= 3
ORDER BY song_count DESC, g.name;
