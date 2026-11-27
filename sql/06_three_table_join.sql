-- Query 9 — Song, artist, and genre combinations (three-table relationship joins).
-- A song with multiple artists and genres produces one row per combination;
-- use COUNT(DISTINCT song_id) for song totals across this fan-out.
SELECT DISTINCT s.title AS song,
       a.name AS artist,
       g.name AS genre
FROM catalog_song AS s
JOIN catalog_songartist AS sa ON sa.song_id = s.id
JOIN catalog_artist AS a ON a.id = sa.artist_id
JOIN catalog_songgenre AS sg ON sg.song_id = s.id
JOIN catalog_genre AS g ON g.id = sg.genre_id
ORDER BY s.title, a.name, g.name
LIMIT 30;
