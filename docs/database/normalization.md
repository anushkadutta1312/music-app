# Normalization of the Music App Database

This explanation refers to the nine application tables in the live `db.sqlite3`, checked against Django models and migrations. Django's `auth_user` is a separate referenced parent table. Normalization describes the logical data structure; database constraints and application validation are distinguished where they differ.

## First Normal Form (1NF)

In 1NF, each stored field has a single value for that row and repeated values are represented in separate rows rather than packed into a string or repeated column group. For example, a song with several artists does not store a comma-separated `artist_names` field. `catalog_songartist` contains one `song_id`/`artist_id` association per row; `catalog_songgenre` similarly stores one song/category pair per row. The song title, duration, and release year each describe one song. The `id` primary key identifies each row.

This structure lets SQL filter by a particular artist or genre through keys and joins. A value such as `"Jazz, Pop"` would be a poor substitute because exact membership, updates, and foreign-key validation would be difficult.

## Second Normal Form (2NF)

2NF requires 1NF and no non-key attribute may depend on only part of a candidate key. It is not enough to point out that the tables have surrogate `id` keys: the alternate candidate keys and junction dependencies also need consideration.

- In entity tables, each declared candidate key is single-column: `id`, plus unique `name` on `catalog_artist` and `catalog_genre`, and unique `user_id` on `accounts_userprofile`. A single-column key has no proper subset on which a partial dependency could occur.
- In `catalog_songartist`, `(song_id, artist_id)` is an alternate candidate key enforced by `unique_song_artist`. Its `role` describes that artist's participation in that song and depends on the pair, not only the song or only the artist.
- In `catalog_songgenre`, `(song_id, genre_id)` is an alternate candidate key and there is no non-key descriptive attribute that could depend on just one side.
- In `profiles_favourite`, `(user_id, song_id)` is unique. `created_at` describes that user's particular favourite relationship.
- In `playlists_playlistsong`, `(playlist_id, song_id)` is unique. `position` and `added_at` describe that song's placement and addition in that playlist. Song title/duration are instead stored once in `catalog_song`; playlist title/owner are stored in `playlists_playlist`.

The explicit unique pairs are important: they define candidate relationship identities and prevent duplicate associations. `position` itself is not unique in SQLite, so the database does not enforce that two songs cannot have the same position; playlist application logic manages ordering.

## Third Normal Form (3NF)

3NF requires 2NF and no non-key attribute should depend transitively on another non-key attribute rather than directly on a key. For example, if artist names and biographies were copied to every song row, the song key would lead to an artist key and then to artist details. Instead, `catalog_artist` stores `name`, `biography`, and image/provider data once; `catalog_songartist` stores only the association and its artist role. Genre names/descriptions are likewise stored in `catalog_genre`, linked through `catalog_songgenre`.

User-owned data follows the same separation: profile fields and role are stored in `accounts_userprofile`, favourites in `profiles_favourite`, and playlist title/description/visibility/owner in `playlists_playlist`. Track metadata is not copied into favourites or playlist-song rows. The structure avoids update anomalies such as having to change a song title in every playlist where it appears.

This 3NF assessment assumes each table's non-key descriptive attributes describe its row's key. It does not assert that the schema models every possible real-world functional dependency (for example, external provider identifiers are not constrained unique). SQLite enforces the keys, unique associations and listed checks; it does not enforce field length, URL format, role choices, or playlist position uniqueness.

## Why the junction tables matter

Songs can have multiple artists and genres, and artists/genres can each be associated with multiple songs. `catalog_songartist` and `catalog_songgenre` turn those many-to-many relationships into two one-to-many relationships while retaining database foreign keys. `profiles_favourite` represents each user/song choice and enforces `UNIQUE(user_id, song_id)`. `playlists_playlistsong` represents each playlist/song membership, stores its order metadata, and enforces `UNIQUE(playlist_id, song_id)`. Together those constraints prevent duplicate favourite and playlist membership relationships.

## Summary

| Form | Evidence from this schema | Result |
|---|---|---|
| 1NF | Atomic scalar columns; repeating artists, genres, favourites, and playlist entries represented as rows | Meets 1NF |
| 2NF | Candidate keys are single-column or relationship pairs; pair-dependent attributes stay with the pair | Meets 2NF under the documented relationship semantics |
| 3NF | Artist, genre, user, song, and playlist details are stored in their own keyed tables and referenced by FKs | Meets 3NF for the modeled dependencies described above |
