# DBMS SQL Practical Demonstrations

## Purpose and execution target

These examples demonstrate SQL against the project's existing populated `db.sqlite3`, rather than a separately-created sample database. Nine app tables and their rows were audited from the live file; exact table counts and constraints are documented in [`ACTUAL_SCHEMA_AUDIT.md`](../database/ACTUAL_SCHEMA_AUDIT.md). The scripts were opened and executed in DB Browser for SQLite against the file in the project root. The command-line verifier [`run_sql_practical.py`](../database/run_sql_practical.py) independently ran the same scripts and checked that the database remained intact.

## Query guide and observed output

| No. | File | SQL concept | Observed result |
| ---: | --- | --- | --- |
| 1 | `sql/01_select_and_filter.sql` | SELECT, ORDER BY, LIMIT | 10 song rows |
| 2 | `sql/01_select_and_filter.sql` | WHERE comparison | 17 songs released in/after 2015 |
| 3 | `sql/02_sort_and_distinct.sql` | DISTINCT, ORDER BY | 10 unique genres |
| 4 | `sql/02_sort_and_distinct.sql` | descending sort | 10 longest-song rows |
| 5 | `sql/03_aggregates_group_by.sql` | COUNT, AVG, MIN, MAX | 55 songs; average 282.5 sec; range 161–589 sec |
| 6 | `sql/03_aggregates_group_by.sql` | LEFT JOIN, GROUP BY | 10 genre groups; Pop 17, Rock 15, Indie 12 at the top |
| 7 | `sql/04_having.sql` | GROUP BY, HAVING | 10 genres meet the minimum of three associated songs |
| 8 | `sql/05_inner_join.sql` | INNER JOIN through SongArtist | 25 displayed credited-song rows |
| 9 | `sql/06_three_table_join.sql` | artist and genre junction joins | 30 displayed combinations; a song with multiple credits can fan out into several combinations |
| 10 | `sql/07_left_join.sql` | LEFT JOIN and pre-aggregation | 12 user IDs, including users with zero playlists |
| 11 | `sql/08_subquery.sql` | IN subquery, grouped condition | 14 songs matched |
| 12 | `sql/08_subquery.sql` | correlated and nested subqueries | 9 playlists above the average playlist size |
| 13 | `sql/09_insert_update_delete.sql` | INSERT inside SAVEPOINT | One uniquely named temporary artist was visible inside the transaction |
| 14 | `sql/09_insert_update_delete.sql` | UPDATE targeted temporary row | The temporary biography changed as expected |
| 15 | `sql/09_insert_update_delete.sql` | DELETE and rollback | Delete left zero matching rows; the entire SAVEPOINT was then rolled back |

The SELECT examples avoid returning email addresses, password hashes, or other account credentials. The LEFT JOIN example uses user IDs only. The many-to-many query explicitly notes join fan-out so its combination count is not mistaken for a distinct-song count.

## Running safely

Open the existing project database in DB Browser and use **Execute SQL** to open scripts from `sql/`. Queries 1–12 are read-only. Run all of `09_insert_update_delete.sql` as one unit: its final `ROLLBACK TO` and `RELEASE` undo every temporary DML change. Do not save intermediate changes with **Write Changes**. The provided verifier additionally compares all nine app-table counts before/after and runs `PRAGMA integrity_check` and `PRAGMA foreign_key_check`.

## Integrity result

The DML demonstration finished without errors, reported zero temporary artist rows after deletion, and rolled back the insert/update/delete transaction. All nine app-table counts matched their baseline (profiles 12; genres 10; artists 20; songs 55; song-artist rows 59; song-genre rows 94; favourites 54; playlists 15; playlist-song rows 70). SQLite reported `integrity_check = ok` and no foreign-key violations. `db.sqlite3` was not reset, migrated, seeded, or intentionally modified by this practical.
