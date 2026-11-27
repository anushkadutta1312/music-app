-- Query 11 — Songs favourited by more than one distinct user (subquery).
SELECT s.id, s.title
FROM catalog_song AS s
WHERE s.id IN (
    SELECT f.song_id
    FROM profiles_favourite AS f
    GROUP BY f.song_id
    HAVING COUNT(DISTINCT f.user_id) > 1
)
ORDER BY s.title;

-- Query 12 — Playlists whose number of songs is above the catalogue average.
SELECT p.id, p.title,
       (SELECT COUNT(*) FROM playlists_playlistsong AS ps
        WHERE ps.playlist_id = p.id) AS track_count
FROM playlists_playlist AS p
WHERE (SELECT COUNT(*) FROM playlists_playlistsong AS ps
       WHERE ps.playlist_id = p.id) > (
    SELECT AVG(track_count)
    FROM (
        SELECT COUNT(*) AS track_count
        FROM playlists_playlistsong
        GROUP BY playlist_id
    ) AS playlist_sizes
)
ORDER BY track_count DESC, p.title;
