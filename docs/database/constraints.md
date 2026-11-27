# Database Integrity Constraints Specification

This document details the relational constraints implemented in the **Music App** database and their enforcement at the SQLite storage layer.

---

## 1. Primary Key (PK) Constraints

Every table in the database possesses a single surrogate integer Primary Key that auto-increments with each inserted row (`id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT`).

### Purpose:
- Uniquely and unambiguously identifies each record.
- Provides fast, clustered B-tree index lookups.
- Avoids mutable natural keys.

---

## 2. Foreign Key (FK) Constraints & Deletion Rules

Foreign keys enforce referential integrity between parent and child tables.

| Child Table | Foreign Key Column | Target Parent Table | Deletion Rule (`ON DELETE`) | Engineering Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `accounts_userprofile` | `user_id` | `auth_user(id)` | `CASCADE` | If a user deletes their account, their profile is completely removed. |
| `playlists_playlist` | `owner_id` | `auth_user(id)` | `CASCADE` | If a user account is deleted, their personal playlists are removed. |
| `profiles_favourite` | `user_id` | `auth_user(id)` | `CASCADE` | If a user account is deleted, their favourite bookmarks are purged. |
| `profiles_favourite` | `song_id` | `catalog_song(id)` | `CASCADE` | If a song is removed from the catalogue, it is purged from user favourites. |
| `catalog_songartist` | `song_id` | `catalog_song(id)` | `CASCADE` | If a song is deleted, its artist relationship link is deleted. |
| `catalog_songartist` | `artist_id` | `catalog_artist(id)` | `CASCADE` | If an artist is deleted, their song association record is removed. |
| `catalog_songgenre` | `song_id` | `catalog_song(id)` | `CASCADE` | If a song is deleted, its genre classification link is removed. |
| `catalog_songgenre` | `genre_id` | `catalog_genre(id)` | `CASCADE` | If a genre is deleted, its link to the song is removed. |
| `playlists_playlistsong` | `playlist_id` | `playlists_playlist(id)` | `CASCADE` | If a playlist is deleted, its track entries are purged (underlying songs remain intact). |
| `playlists_playlistsong` | `song_id` | `catalog_song(id)` | `CASCADE` | If a song is deleted from the catalogue, it is automatically removed from any playlist containing it. |

---

## 3. UNIQUE Constraints

UNIQUE constraints guarantee that duplicate entries cannot exist, preventing data anomalies and redundant records.

1. **`catalog_genre.name`**: Genre names must be unique (e.g., only one "Rock" or "Jazz" record).
2. **`catalog_artist.name`**: Artist names must be unique to avoid duplicate artist entries.
3. **`accounts_userprofile.user_id`**: Guaranteed unique via `OneToOneField` (a user can have at most one profile).
4. **`catalog_songartist(song_id, artist_id)`**: Prevents associating the same artist with the same song more than once.
5. **`catalog_songgenre(song_id, genre_id)`**: Prevents associating the same genre with the same song more than once.
6. **`profiles_favourite(user_id, song_id)`**: Prevents a user from bookmarking the exact same song multiple times.
7. **`playlists_playlistsong(playlist_id, song_id)`**: Prevents adding the exact same song multiple times to the same playlist.

---

## 4. NOT NULL Constraints

All mandatory columns carry explicit `NOT NULL` constraints in SQLite:
- `title` in `catalog_song`
- `name` in `catalog_artist` and `catalog_genre`
- `duration_seconds` in `catalog_song`
- `role` in `accounts_userprofile`
- `title` in `playlists_playlist`
- All foreign key columns (`user_id`, `song_id`, `artist_id`, `genre_id`, `playlist_id`, `owner_id`)

Optional columns like `release_year` in `Song` explicitly permit `NULL`.

---

## 5. DEFAULT Values

Meaningful defaults streamline operations and guarantee consistent states:
- `accounts_userprofile.role`: Defaults to `'MEMBER'`.
- `playlists_playlist.is_public`: Defaults to `False` (private by default).
- `catalog_songartist.role`: Defaults to `'Primary'`.
- `playlists_playlistsong.position`: Defaults to `1`.
- `created_at` and `added_at`: Default to current database timestamp via Django's `auto_now_add=True`.

---

## 6. CHECK Constraints (Database-Level)

CHECK constraints enforce domain validity rules directly inside the SQLite storage engine:

### 1. `check_song_duration_positive`
```sql
CONSTRAINT "check_song_duration_positive" CHECK ("duration_seconds" > 0)
```
- **Rule**: Audio tracks must have a strictly positive duration. Songs with zero or negative durations are rejected by the SQLite database.

### 2. `check_song_release_year_valid`
```sql
CONSTRAINT "check_song_release_year_valid" CHECK ("release_year" >= 1900 OR "release_year" IS NULL)
```
- **Rule**: If a release year is supplied, it must be $\ge 1900$, preventing bogus or invalid historical years.

### 3. `check_playlist_song_position_positive`
```sql
CONSTRAINT "check_playlist_song_position_positive" CHECK ("position" >= 1)
```
- **Rule**: Sequential track ordering within a playlist starts at 1. Positions $\le 0$ are rejected by SQLite.

---

## 7. Direct SQLite Schema Verification

Direct query executed against SQLite `sqlite_master` confirms that every constraint is physically present in `db.sqlite3`:

```sql
CREATE TABLE "catalog_song" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "title" varchar(200) NOT NULL, 
    "album_name" varchar(150) NOT NULL, 
    "duration_seconds" integer unsigned NOT NULL CHECK ("duration_seconds" >= 0), 
    "release_year" integer unsigned NULL CHECK ("release_year" >= 0), 
    "cover_image_url" varchar(500) NOT NULL, 
    "external_provider" varchar(50) NOT NULL, 
    "external_track_id" varchar(100) NOT NULL, 
    "created_at" datetime NOT NULL, 
    "updated_at" datetime NOT NULL, 
    CONSTRAINT "check_song_duration_positive" CHECK ("duration_seconds" > 0), 
    CONSTRAINT "check_song_release_year_valid" CHECK (("release_year" >= 1900 OR "release_year" IS NULL))
);
```
