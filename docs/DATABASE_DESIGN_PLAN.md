# Database Design Plan & Architecture

## 1. Overview & Objectives

This document details the finalized relational database architecture for the **Music App**.

The database architecture directly satisfies all academic DBMS evaluation criteria:
1. Complete normalization adhering to **1NF, 2NF, and 3NF**.
2. **9 meaningful application tables** (exceeding the minimum 6 tables requirement).
3. Explicit relational constraints: **Primary Keys**, **Foreign Keys**, **UNIQUE**, **NOT NULL**, **DEFAULT**, and **CHECK** constraints.
4. Clean support for **One-to-One (1:1)**, **One-to-Many (1:M)**, and **Many-to-Many (M:N)** relationships with explicit junction models.
5. Single unified SQLite database (`db.sqlite3`) powering both application runtime and SQL practical query demonstrations.

---

## 2. Final Implemented Entities

### 2.1 Core Entities

1. **User (`auth_user`)**
   - Django standard authentication entity.
   - Fields: `id` (PK), `username` (UNIQUE), `email`, `password`, `is_staff`, `is_active`, `date_joined`.

2. **UserProfile (`accounts_userprofile`)**
   - Personal profile details linked 1:1 with `auth_user`.
   - Fields: `id` (PK), `user_id` (FK to User, UNIQUE, ON DELETE CASCADE), `display_name`, `bio`, `profile_image`, `role` (`'ADMIN'` or `'MEMBER'`), `created_at`, `updated_at`.

3. **Genre (`catalog_genre`)**
   - Music categorization entity.
   - Fields: `id` (PK), `name` (UNIQUE, NOT NULL), `description`, `created_at`.

4. **Artist (`catalog_artist`)**
   - Musicians, bands, and creators.
   - Fields: `id` (PK), `name` (UNIQUE, NOT NULL), `biography`, `image_url`, `external_provider`, `external_artist_id`, `created_at`, `updated_at`.

5. **Song (`catalog_song`)**
   - Individual musical tracks with metadata.
   - Fields: `id` (PK), `title` (NOT NULL), `album_name`, `duration_seconds` (INTEGER, CHECK `duration_seconds > 0`), `release_year` (INTEGER, CHECK `release_year >= 1900 OR release_year IS NULL`), `cover_image_url`, `external_provider`, `external_track_id`, `created_at`, `updated_at`.

6. **Playlist (`playlists_playlist`)**
   - User-created collections of songs.
   - Fields: `id` (PK), `owner_id` (FK to User, ON DELETE CASCADE), `title` (NOT NULL), `description`, `cover_image_url`, `is_public` (BOOLEAN, DEFAULT False), `created_at`, `updated_at`.

---

### 2.2 Junction & Relationship Entities (M:N Relationships)

7. **SongArtist (`catalog_songartist`)** *(Song <-> Artist Junction Table)*
   - Resolves Many-to-Many relationship between songs and artists (supporting collaborations, features, and multi-artist tracks).
   - Fields: `id` (PK), `song_id` (FK to Song, ON DELETE CASCADE), `artist_id` (FK to Artist, ON DELETE CASCADE), `role` (VARCHAR, DEFAULT 'Primary').
   - Constraints: UNIQUE(`song_id`, `artist_id`).

8. **SongGenre (`catalog_songgenre`)** *(Song <-> Genre Junction Table)*
   - Resolves Many-to-Many relationship between songs and genres (songs can belong to multiple genres).
   - Fields: `id` (PK), `song_id` (FK to Song, ON DELETE CASCADE), `genre_id` (FK to Genre, ON DELETE CASCADE).
   - Constraints: UNIQUE(`song_id`, `genre_id`).

9. **Favourite (`profiles_favourite`)** *(User <-> Song Favourites)*
   - Records a user's bookmarked favourite songs.
   - Fields: `id` (PK), `user_id` (FK to User, ON DELETE CASCADE), `song_id` (FK to Song, ON DELETE CASCADE), `created_at`.
   - Constraints: UNIQUE(`user_id`, `song_id`) preventing duplicate favourites.

10. **PlaylistSong (`playlists_playlistsong`)** *(Playlist <-> Song Junction Table)*
    - Resolves Many-to-Many relationship between playlists and tracks.
    - Fields: `id` (PK), `playlist_id` (FK to Playlist, ON DELETE CASCADE), `song_id` (FK to Song, ON DELETE CASCADE), `position` (INTEGER, CHECK `position >= 1`), `added_at`.
    - Constraints: UNIQUE(`playlist_id`, `song_id`) preventing duplicate songs within the same playlist.

---

## 3. Relational Relationships Summary

| Parent Entity | Child / Junction Entity | Relationship | Key Implementation |
| :--- | :--- | :--- | :--- |
| `User` | `UserProfile` | One-to-One (1:1) | `user_id` (OneToOneField / UNIQUE FK) |
| `User` | `Playlist` | One-to-Many (1:M) | `owner_id` (ForeignKey) |
| `User` | `Favourite` | One-to-Many (1:M) | `user_id` (ForeignKey) |
| `Song` | `Favourite` | One-to-Many (1:M) | `song_id` (ForeignKey) |
| `Song` | `SongArtist` | One-to-Many (1:M) | `song_id` (ForeignKey) |
| `Artist` | `SongArtist` | One-to-Many (1:M) | `artist_id` (ForeignKey) |
| `Song` | `SongGenre` | One-to-Many (1:M) | `song_id` (ForeignKey) |
| `Genre` | `SongGenre` | One-to-Many (1:M) | `genre_id` (ForeignKey) |
| `Playlist` | `PlaylistSong` | One-to-Many (1:M) | `playlist_id` (ForeignKey) |
| `Song` | `PlaylistSong` | One-to-Many (1:M) | `song_id` (ForeignKey) |

---

## 4. Documentation References

For exhaustive technical specifications, refer to:
- [docs/database/relational_schema.md](file:///c:/Users/Hp/Desktop/MY%20PROJECT/docs/database/relational_schema.md)
- [docs/database/constraints.md](file:///c:/Users/Hp/Desktop/MY%20PROJECT/docs/database/constraints.md)
- [docs/database/normalization.md](file:///c:/Users/Hp/Desktop/MY%20PROJECT/docs/database/normalization.md)
- [docs/database/database_dictionary.md](file:///c:/Users/Hp/Desktop/MY%20PROJECT/docs/database/database_dictionary.md)
- [docs/database/er_diagram_source.mmd](file:///c:/Users/Hp/Desktop/MY%20PROJECT/docs/database/er_diagram_source.mmd)
