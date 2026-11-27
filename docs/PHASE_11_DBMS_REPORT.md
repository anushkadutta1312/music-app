# Phase 11 — DBMS Practical and Database Documentation Report

**Completed:** 27 November 2026  
**Database:** Existing project `db.sqlite3` (258,048 bytes at final inspection)

## Scope and preservation

This phase audited and documented the existing SQLite database and supplied an SQL practical. The database was not reset, reseeded, migrated, or replaced. No application models, views, forms, schema, or migrations were changed. SQL INSERT, UPDATE, and DELETE examples used a uniquely named temporary artist inside a SAVEPOINT and rolled the transaction back. The final safety verification confirmed that all nine application-table counts remained at their audited baseline, the temporary artist was absent, SQLite integrity was `ok`, and the foreign-key check returned no violations.

The full Django suite created its test database in memory (`file:memorydb_default?mode=memory&cache=shared`), ran 112 tests, and destroyed that temporary test database. The separate project database remained the verification target.

## Live schema audit

The existing database has the expected nine application tables, plus Django support tables. Their counts were:

| Application table | Rows |
| --- | ---: |
| `accounts_userprofile` | 12 |
| `catalog_genre` | 10 |
| `catalog_artist` | 20 |
| `catalog_song` | 55 |
| `catalog_songartist` | 59 |
| `catalog_songgenre` | 94 |
| `profiles_favourite` | 54 |
| `playlists_playlist` | 15 |
| `playlists_playlistsong` | 70 |

The physical tables, columns, indexes, constraints, and foreign keys were compared with the Django models and existing initial migrations. SQLite reports integer storage for `BigAutoField` primary keys and does not encode model-level choices as database constraints. There are no SQL `DEFAULT` clauses for model defaults such as `MEMBER`, playlist privacy, relationship roles, or playlist-song position; Django applies those defaults. Check [`../database/ACTUAL_SCHEMA_AUDIT.md`](../database/ACTUAL_SCHEMA_AUDIT.md) for the findings and [`../database/ER_DIAGRAM.md`](../database/ER_DIAGRAM.md), [`../docs/database/relational_schema.md`](database/relational_schema.md), [`../docs/database/database_dictionary.md`](database/database_dictionary.md), and [`../docs/database/normalization.md`](database/normalization.md) for the updated design documentation.

## SQL demonstrations

Fifteen queries are organized into nine runnable scripts under [`../sql/`](../sql/). They cover filtered and sorted SELECTs, DISTINCT, aggregate functions, GROUP BY, HAVING, INNER and LEFT JOINs, many-to-many junction traversal, subqueries, and INSERT/UPDATE/DELETE. The practical was executed in DB Browser for SQLite against the exact project database file and independently checked by [`../database/run_sql_practical.py`](../database/run_sql_practical.py).

Observed results included 55 catalogue songs (average duration 282.5 seconds; minimum 161; maximum 589), 10 genre groups, 25 displayed song-artist rows, 30 displayed song-artist-genre combinations, 12 user IDs in the LEFT JOIN, 14 subquery-matched songs, and 9 playlists above the average size. The final temporary-row query returned zero after DELETE; the subsequent rollback preserved the original data. The three-way join can return multiple combinations per song, as explained in the SQL source and practical guide.

DB Browser evidence is in [`../screenshots/dbms/database_structure.jpg`](../screenshots/dbms/database_structure.jpg) and [`../screenshots/dbms/09_dml_rollback.jpg`](../screenshots/dbms/09_dml_rollback.jpg). The former shows the expected project and Django tables. The latter shows the DML script's successful completion and its zero-row result after DELETE, before the final transaction rollback. The SQL guide is [`DBMS_SQL_PRACTICAL.md`](DBMS_SQL_PRACTICAL.md).

## Verification results

| Verification | Result |
| --- | --- |
| `.venv\Scripts\python.exe manage.py check` | Passed: no issues (0 silenced). |
| `.venv\Scripts\python.exe manage.py test --verbosity=2` | Passed: 112 tests in 259.681 seconds; `OK`. |
| DB Browser SQL demonstrations | All nine scripts executed; no SQL errors. DML demo was rolled back. |
| `database/run_sql_practical.py` | Passed after closing DB Browser; all 15 demonstrations completed and final database checks passed. |
| App-table baseline vs. after DML | All nine counts matched. |
| Temporary demonstration artist after rollback | 0 rows. |
| `PRAGMA integrity_check` | `ok`. |
| `PRAGMA foreign_key_check` | No rows. |

One initial command-line DML verification attempt, while DB Browser still held the file open, stopped at SQLite `database is locked`. The DB Browser transaction had already shown its rollback result; after closing the viewer, the full command-line practical was rerun and passed. No application or database change was made to work around the lock.

## Files created or modified

- Created [`../database/ACTUAL_SCHEMA_AUDIT.md`](../database/ACTUAL_SCHEMA_AUDIT.md), [`../database/ER_DIAGRAM.md`](../database/ER_DIAGRAM.md), [`../database/ER_DIAGRAM.mmd`](../database/ER_DIAGRAM.mmd), and [`../database/run_sql_practical.py`](../database/run_sql_practical.py).
- Updated [`../docs/database/relational_schema.md`](database/relational_schema.md), [`../docs/database/database_dictionary.md`](database/database_dictionary.md), and [`../docs/database/normalization.md`](database/normalization.md) to reflect actual SQLite metadata and distinguish database constraints from Django defaults.
- Created [`DBMS_SQL_PRACTICAL.md`](DBMS_SQL_PRACTICAL.md) and this report; updated [`../sql/README.md`](../sql/README.md), [`../database/README.md`](../database/README.md), [`../README.md`](../README.md), and [`../DEVELOPMENT_PROGRESS.md`](../DEVELOPMENT_PROGRESS.md).
- Created `../sql/01_select_and_filter.sql` through `../sql/09_insert_update_delete.sql` and two DB Browser evidence images under `../screenshots/dbms/`.
- No models, application views/forms, migration files, or database schema were modified. Git staging and commit state were left untouched; no commit or push was made.

## Roadmap note and risks

The inherited roadmap labeled Phase 11 as Music Playback Integration and Phase 12 as SQL practical demonstrations. The approved task handover assigns this work as Phase 11 DBMS practicals; the README and progress tracker now clarify the chosen sequence, with playback next. No playback integration is included.

The database file is currently ignored by the broad `*.sqlite3` rule in `.gitignore`, although the existing Git index already contains it. This phase did not stage, unstage, commit, or push anything. Continue to preserve the existing index and the populated `db.sqlite3`; avoid replacing it with a new empty database. The separate `.gitignore` behavior should be reviewed before any future checkpoint or transfer.

## Stop point

Phase 11 DBMS practical and documentation work is complete. No Phase 12 work has begun. Await approval before implementing the next phase.
