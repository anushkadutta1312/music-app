# Relational Schema — Verified SQLite Structure

This specification covers the nine Music App tables in the root `db.sqlite3`. Types and declared constraints below reflect the actual SQLite `sqlite_master` DDL; integer affinity is used for integer-like columns. All nine tables have an `INTEGER PRIMARY KEY AUTOINCREMENT` `id`. Because SQLite rowid primary keys are implicitly not null, each `id` is required. Foreign-key columns are `NOT NULL` and reference the listed parent with `ON DELETE CASCADE`.

**Important:** Django model defaults are not SQLite DDL defaults in this database. The app inserts default values through Django. Unless listed as a CHECK, UNIQUE, PK, or FK below, a validation in a form/model is not necessarily database-enforced. `blank=True` does not imply nullable; nullable status below is physical SQLite `NOT NULL` status.

## `accounts_userprofile`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `display_name` | varchar(100) | No | — |
| `bio` | TEXT | No | — |
| `profile_image` | varchar(500) | No | — |
| `role` | varchar(10) | No | Model choices ADMIN/MEMBER; choices are not a database CHECK |
| `created_at` | datetime | No | — |
| `updated_at` | datetime | No | — |
| `user_id` | integer | No | UNIQUE, FK → `auth_user(id)`, cascade |

Index: unique index on `user_id` (enforces one profile per user). No SQLite column DEFAULT clause.

## `catalog_genre`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `name` | varchar(50) | No | UNIQUE |
| `description` | TEXT | No | — |
| `created_at` | datetime | No | — |

Index: unique index on `name`. No SQLite DEFAULT clause.

## `catalog_artist`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `name` | varchar(150) | No | UNIQUE |
| `biography` | TEXT | No | — |
| `image_url` | varchar(500) | No | — |
| `external_provider` | varchar(50) | No | — |
| `external_artist_id` | varchar(100) | No | — |
| `created_at` | datetime | No | — |
| `updated_at` | datetime | No | — |

Index: unique index on `name`. Provider fields are not unique. No SQLite DEFAULT clause.

## `catalog_song`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `title` | varchar(200) | No | — |
| `album_name` | varchar(150) | No | — |
| `duration_seconds` | integer unsigned | No | CHECK `>= 0` generated for positive field and named CHECK `> 0` |
| `release_year` | integer unsigned | Yes | CHECK `>= 0` generated for positive field and named CHECK `>= 1900 OR NULL` |
| `cover_image_url` | varchar(500) | No | — |
| `external_provider` | varchar(50) | No | — |
| `external_track_id` | varchar(100) | No | — |
| `created_at` | datetime | No | — |
| `updated_at` | datetime | No | — |

No SQLite DEFAULT clause. The 1900 minimum applies only when `release_year` is supplied.

## `catalog_songartist`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `role` | varchar(50) | No | Django model default `Primary`; no SQLite DEFAULT |
| `artist_id` | bigint | No | FK → `catalog_artist(id)`, cascade |
| `song_id` | bigint | No | FK → `catalog_song(id)`, cascade |

Unique constraint/index: `(song_id, artist_id)` named `unique_song_artist`. Separate indexes on `artist_id` and `song_id`.

## `catalog_songgenre`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `genre_id` | bigint | No | FK → `catalog_genre(id)`, cascade |
| `song_id` | bigint | No | FK → `catalog_song(id)`, cascade |

Unique constraint/index: `(song_id, genre_id)` named `unique_song_genre`. Separate indexes on `genre_id` and `song_id`.

## `profiles_favourite`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `created_at` | datetime | No | — |
| `song_id` | bigint | No | FK → `catalog_song(id)`, cascade |
| `user_id` | integer | No | FK → `auth_user(id)`, cascade |

Unique constraint/index: `(user_id, song_id)` named `unique_user_song_favourite`. Separate FK indexes.

## `playlists_playlist`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `title` | varchar(150) | No | — |
| `description` | TEXT | No | — |
| `cover_image_url` | varchar(500) | No | — |
| `is_public` | bool | No | Django model default `False`; no SQLite DEFAULT |
| `created_at` | datetime | No | — |
| `updated_at` | datetime | No | — |
| `owner_id` | integer | No | FK → `auth_user(id)`, cascade |

Index: ordinary index on `owner_id`. There is no unique constraint on playlist title or `(owner_id, title)`.

## `playlists_playlistsong`

| Column | SQLite type | Null? | Key / rule |
|---|---|---:|---|
| `id` | INTEGER | No | PK, autoincrement |
| `position` | integer unsigned | No | Generated CHECK `>= 0`, named CHECK `>= 1`; Django default 1, no SQLite DEFAULT |
| `added_at` | datetime | No | — |
| `playlist_id` | bigint | No | FK → `playlists_playlist(id)`, cascade |
| `song_id` | bigint | No | FK → `catalog_song(id)`, cascade |

Unique constraint/index: `(playlist_id, song_id)` named `unique_playlist_song`. Separate FK indexes. Position is not constrained unique within a playlist.

## Constraint/index summary

All FKs have indexes generated by Django. Unique constraints are backed by SQLite unique indexes. No explicit SQL defaults were found for the nine app tables. Checks and uniqueness are enforced by SQLite; role choices, URL formatting, text lengths, and other form/model validation are application-layer rules. See [`ACTUAL_SCHEMA_AUDIT.md`](ACTUAL_SCHEMA_AUDIT.md) for the audit method and SQLite-specific notes.
