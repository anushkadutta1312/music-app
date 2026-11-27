# Live SQLite Schema Audit

**Inspected:** 27 November 2026  
**Database:** `C:\Users\Hp\Desktop\MY PROJECT\db.sqlite3` opened in SQLite read-only mode for this audit.

## Result

The file contains all nine expected application tables: `accounts_userprofile`, `catalog_genre`, `catalog_artist`, `catalog_song`, `catalog_songartist`, `catalog_songgenre`, `profiles_favourite`, `playlists_playlist`, and `playlists_playlistsong`. No application table was missing or unexpected. Django support tables are also present, including `auth_user`, `auth_group`, `auth_permission`, `django_admin_log`, `django_content_type`, `django_migrations`, and `django_session` and their auth join tables. These are not counted among the nine project tables.

The nine app tables, their columns, indexes, unique constraints, and foreign keys match the project models and initial migrations. Relevant details confirmed from `sqlite_master`, `PRAGMA table_info`, `PRAGMA foreign_key_list`, and `PRAGMA index_list`:

- Every app table uses an auto-incrementing `id` primary key. Despite Django declaring `BigAutoField`, SQLite reports its primary-key storage type as `INTEGER` (SQLite's rowid alias representation).
- SQLite reports foreign key columns according to the generated physical declaration (for example `bigint` on many-to-many FK columns); affinity is integer. ORM `PositiveIntegerField` declarations may also appear as `integer unsigned` plus generated checks.
- Unique database indexes/constraints: profile `user_id`; genre `name`; artist `name`; `(song_id, artist_id)`; `(song_id, genre_id)`; `(user_id, song_id)`; `(playlist_id, song_id)`.
- Explicit checks: song duration `> 0`; song release year `>= 1900 OR NULL`; playlist-song position `>= 1`. SQLite also contains generated nonnegative checks for Django positive integer fields, so `duration_seconds` and `position` have an additional `>= 0` check. The stricter explicit checks govern valid values.
- Django creates ordinary indexes for foreign key columns. Composite unique indexes support the unique relationship constraints. Unique `name` and profile `user_id` are backed by unique indexes.
- `PRAGMA integrity_check` returned `ok`; `PRAGMA foreign_key_check` returned no rows.

## Database defaults versus Django defaults

The table DDL has no SQL `DEFAULT` clauses for the app columns. Defaults such as profile role `MEMBER`, `SongArtist.role` `Primary`, playlist `is_public=False`, playlist-song `position=1`, and blank string fields are Django/model/form defaults applied by the application. Auto timestamps are populated by Django. They should not be described as SQLite-enforced defaults. The database itself enforces `NOT NULL`, primary/foreign keys, named unique constraints, and checks listed above. `blank=True` affects form validation; it does not make the SQLite column nullable. `release_year` is the nullable project field.

## Model/schema observations

- The nine-table expected list is correct; `auth_user` is a referenced Django table, not one of those nine.
- The old editable ER source included `auth_user` among its ten depicted entities. It has been replaced with a nine-app-table diagram that shows `auth_user` only as the external parent reference.
- Earlier relational documentation labeled model defaults as database defaults and described model field widths as the physical SQLite declarations without qualifying SQLite storage. Updated documentation separates actual DDL from Python-level defaults.
- The live schema has no SQL-only unexpected application columns or tables. The `db.sqlite3` file was not migrated or altered for this audit.
