-- Query 1 — List a small sample of songs and release years (basic SELECT).
SELECT id, title, album_name, release_year
FROM catalog_song
ORDER BY id
LIMIT 10;

-- Query 2 — Filter for songs released in or after 2015 (WHERE).
SELECT title, release_year
FROM catalog_song
WHERE release_year >= 2015
ORDER BY release_year, title;
