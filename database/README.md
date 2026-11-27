# Database Documentation & Inspection

This directory contains resources, notes, and guidelines relating to the relational database of the **Music App**.

---

## Database Specifications

- **Engine**: SQLite 3
- **Database File**: `db.sqlite3` (located at project root)
- **Management Tool**: Django Object-Relational Mapping (ORM)
- **Inspection Utility**: **DB Browser for SQLite** (free, open-source visual inspector)

---

## Purpose & Academic Role

The SQLite database serves a dual purpose in this project:
1. **Live Application Backend**: Houses all persistent data for the Django web application (users, profiles, songs, artists, genres, song associations, favourites, playlists, and playlist tracks).
2. **Academic SQL Practical Showcase**: Acts as the exact relational target against which all required SQL scripts (DDL, DML, complex SELECT queries) are demonstrated and evaluated.

---

## Inspection with DB Browser for SQLite

To inspect the application database during development:
1. Open DB Browser for SQLite.
2. Select **Open Database** and browse to `db.sqlite3` in the project root directory.
3. Navigate through:
   - **Database Structure**: View tables, columns, indexes, and constraints.
   - **Browse Data**: Inspect live records inserted via the web application.
   - **Execute SQL**: Run queries from the `sql/` directory to demonstrate SQL functionality.

## Verified live database

The current file contains nine application tables and the expected Django support tables. Its live schema and exact project-table counts were checked against the models and migrations; see [`ACTUAL_SCHEMA_AUDIT.md`](ACTUAL_SCHEMA_AUDIT.md). The 15-query SQL practical and safe execution instructions are in [`docs/DBMS_SQL_PRACTICAL.md`](../docs/DBMS_SQL_PRACTICAL.md), with runnable scripts in `../sql/`. `run_sql_practical.py` runs read-only demonstrations plus a rolled-back DML demonstration, then checks that the original row counts and database integrity remain intact.
