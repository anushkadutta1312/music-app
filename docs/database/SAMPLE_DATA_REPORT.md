# Sample Data Population & Database Verification Report

This report documents the synthetic sample data populated into the **Music App** SQLite database (`db.sqlite3`).

---

## 1. Actual Database Record Counts

All counts reported below are derived from direct SQL queries against `db.sqlite3`:

| Table | Application Model | Target Range | Actual Count in `db.sqlite3` | Status |
| :--- | :--- | :---: | :---: | :--- |
| `auth_user` | User (Django Auth) | ~12 | **12** | **VERIFIED** |
| `accounts_userprofile` | UserProfile | ~12 | **12** | **VERIFIED** |
| `catalog_genre` | Genre | ~10 | **10** | **VERIFIED** |
| `catalog_artist` | Artist | ~20 | **20** | **VERIFIED** |
| `catalog_song` | Song | ~50 | **55** | **VERIFIED** |
| `catalog_songartist` | SongArtist (M:N) | 55–65 | **59** | **VERIFIED** |
| `catalog_songgenre` | SongGenre (M:N) | 60–80 | **94** | **VERIFIED** |
| `profiles_favourite` | Favourite (M:N) | 35–50 | **54** | **VERIFIED** |
| `playlists_playlist` | Playlist | ~15 | **15** | **VERIFIED** |
| `playlists_playlistsong` | PlaylistSong (M:N) | 50–70 | **70** | **VERIFIED** |

---

## 2. Development Demo Accounts

The local seed command creates 12 synthetic accounts for testing and evaluation. Their fixed development passwords are intentionally omitted from this report. Do not use seeded demo accounts in a public deployment.

> **Note**: `kevin_newbie` and `julia_ambient` intentionally have zero playlists to enable demonstration of outer joins (`LEFT JOIN auth_user ... WHERE playlists_playlist.id IS NULL`).

---

## 3. The `seed_data` Management Command

### Command Location
`catalog/management/commands/seed_data.py`

### How to Run
```powershell
python manage.py seed_data
```

### Idempotency & Repeatability
The command is strictly idempotent:
- Uses `get_or_create` across all models with natural unique identifiers.
- Encapsulated within `transaction.atomic()` to guarantee all-or-nothing database consistency.
- Running the command a second time results in **0 duplicate rows** (`New: 0` across all models).

---

## 4. SQLite Integrity & Verification

Executing `database/verify_sample_data.py` directly confirms:
1. **`PRAGMA integrity_check`**: `ok` (no corrupted pages or index errors).
2. **`PRAGMA foreign_key_check`**: `0 violations found` (every foreign key references a real record).
3. **Check Constraints**:
   - Every song has `duration_seconds > 0` (min: 161s, max: 589s).
   - Every song with a release year satisfies `release_year >= 1900` (range: 1959–2022).
   - Every playlist song has `position >= 1` (sequential 1, 2, 3...).

---

## 5. SQL Practical Query Readiness Mapping

The sample dataset is structured to support all required academic SQL demonstrations:

1. **`SELECT * FROM catalog_song;`**: Returns all 55 songs with metadata.
2. **`WHERE` Filtering**: Retrieve songs where `release_year >= 2010` or `duration_seconds < 240`.
3. **`ORDER BY`**: Order songs alphabetically by title or by duration.
4. **`DISTINCT` Genres**: Fetch all 10 distinct music classifications.
5. **`COUNT` Aggregation**: Count total tracks, artists, and playlists.
6. **`GROUP BY` & `HAVING`**:
   - `SELECT g.name, COUNT(sg.song_id) FROM catalog_genre g JOIN catalog_songgenre sg ... GROUP BY g.name HAVING COUNT(sg.song_id) > 5;`
   - Pop (17), Rock (15), Indie (12), Alternative (9), Electronic (9), R&B (8), Acoustic (7), Hip-Hop (6), Jazz (6).
7. **`INNER JOIN` (Songs + Artists)**: Join `catalog_song` with `catalog_songartist` and `catalog_artist` to display track performer and feature credits.
8. **Three-Table `JOIN` (Playlists + Tracks)**: Join `playlists_playlist`, `playlists_playlistsong`, and `catalog_song` to display ordered playlist tracks.
9. **`LEFT JOIN` (Users Without Playlists)**:
   ```sql
   SELECT u.username 
   FROM auth_user u 
   LEFT JOIN playlists_playlist p ON u.id = p.owner_id 
   WHERE p.id IS NULL;
   ```
   *Returns*: `kevin_newbie` and `julia_ambient`.
10. **Subqueries**: Find songs with durations greater than the average song duration:
    ```sql
    SELECT title, duration_seconds 
    FROM catalog_song 
    WHERE duration_seconds > (SELECT AVG(duration_seconds) FROM catalog_song);
    ```

---

## 6. How to Inspect in DB Browser for SQLite

1. Open **DB Browser for SQLite**.
2. Click **Open Database** and select `db.sqlite3` located in the root of the project directory.
3. In the **Database Structure** tab:
   - Expand table nodes to inspect columns, data types, PKs, FKs, and Check constraints.
4. In the **Browse Data** tab:
   - Select `catalog_song` to inspect the 55 songs.
   - Select `catalog_artist` to inspect the 20 artists.
   - Select `playlists_playlistsong` to observe sequential `position` ordering.
5. In the **Execute SQL** tab:
   - Run verification queries (e.g., `SELECT COUNT(*) FROM catalog_song;`).
