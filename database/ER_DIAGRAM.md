# Music App Entity–Relationship Diagram

This diagram covers the nine project application tables. `auth_user` is Django's built-in account table and is shown only as an external referenced table because profiles, favourites, and playlists point to it. The other Django support tables are outside the project ER model.

Editable source: [`ER_DIAGRAM.mmd`](ER_DIAGRAM.mmd). The schema was checked against `db.sqlite3`, Django model files, and the initial migrations on 27 November 2026. SQLite's live PRAGMA output is authoritative for stored types and constraints.

![Music App ER diagram](ER_DIAGRAM.png)

Cardinality: one auth user has zero or one profile (the profile's unique `user_id` enforces at most one); one user can have many favourites and playlists. Songs and artists, songs and genres, and playlists and songs are many-to-many relationships resolved by explicit junction tables. Each favourite joins one user to one song. Each junction pair is unique in the database.
