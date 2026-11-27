-- Query 10 — Every user ID and number of owned playlists, including zero (LEFT JOIN).
-- Aggregate playlist rows before joining so each user appears exactly once.
SELECT u.id AS user_id,
       COALESCE(p.playlist_count, 0) AS playlist_count
FROM auth_user AS u
LEFT JOIN (
    SELECT owner_id, COUNT(*) AS playlist_count
    FROM playlists_playlist
    GROUP BY owner_id
) AS p ON p.owner_id = u.id
ORDER BY u.id;
