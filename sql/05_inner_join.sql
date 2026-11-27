-- Query 8 — Songs and their credited artists (INNER JOIN).
SELECT s.title AS song,
       a.name AS artist,
       sa.role
FROM catalog_song AS s
INNER JOIN catalog_songartist AS sa ON sa.song_id = s.id
INNER JOIN catalog_artist AS a ON a.id = sa.artist_id
ORDER BY s.title, a.name
LIMIT 25;
