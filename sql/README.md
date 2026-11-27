# SQL Practical Demonstrations

The nine numbered scripts in this directory provide 15 demonstrations against the project's populated SQLite database. They are ordered by concept and were executed using DB Browser for SQLite:

1. `01_select_and_filter.sql` — SELECT, WHERE, LIKE, IN, BETWEEN.
2. `02_sort_and_distinct.sql` — DISTINCT and ORDER BY.
3. `03_aggregates_group_by.sql` — COUNT, AVG, MIN, MAX and GROUP BY.
4. `04_having.sql` — filtering aggregate groups with HAVING.
5. `05_inner_join.sql` — song and artist junction traversal.
6. `06_three_table_join.sql` — song, artist and genre joins.
7. `07_left_join.sql` — retain users with no playlist.
8. `08_subquery.sql` — nested and correlated queries.
9. `09_insert_update_delete.sql` — INSERT, UPDATE and DELETE inside a SAVEPOINT that is rolled back.

The last script is intentionally reversible. Run the entire file as one unit; it rolls the temporary demonstration row back and releases the savepoint. Never save intermediate DML changes to the project database. `database/run_sql_practical.py` provides a read-only/reversible command-line execution and checks baseline table counts, referential integrity and SQLite integrity afterward.

See [the practical guide](../docs/DBMS_SQL_PRACTICAL.md), [the actual schema audit](../database/ACTUAL_SCHEMA_AUDIT.md), and [the Phase 11 report](../docs/PHASE_11_DBMS_REPORT.md).
