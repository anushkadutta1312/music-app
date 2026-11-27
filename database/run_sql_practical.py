"""Verify the SQL practical against this project's populated db.sqlite3.

Read demonstrations use SQLite read-only mode. The DML demonstration uses a
savepoint in the same existing database and rolls it back before exit.
"""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB_FILE = ROOT / "db.sqlite3"
SQL_DIR = ROOT / "sql"
APP_TABLES = {
    "accounts_userprofile": 12,
    "catalog_genre": 10,
    "catalog_artist": 20,
    "catalog_song": 55,
    "catalog_songartist": 59,
    "catalog_songgenre": 94,
    "profiles_favourite": 54,
    "playlists_playlist": 15,
    "playlists_playlistsong": 70,
}


def statements(path):
    """Yield complete SQL statements, keeping comment-only lines attached."""
    pending = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        pending += line + "\n"
        if sqlite3.complete_statement(pending):
            if pending.strip() and any(part.strip() and not part.lstrip().startswith("--")
                                       for part in pending.splitlines()):
                yield pending.strip()
            pending = ""
    if pending.strip():
        raise ValueError(f"Incomplete SQL statement in {path.name}: {pending}")


def counts(connection):
    return {table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in APP_TABLES}


def main():
    before_conn = sqlite3.connect(f"file:{DB_FILE.as_posix()}?mode=ro", uri=True)
    before = counts(before_conn)
    print(f"Database: {DB_FILE}")
    print(f"Baseline application counts: {before}")
    if before != APP_TABLES:
        raise SystemExit(f"Expected baseline counts differ: {APP_TABLES}")

    for file_name in sorted(path.name for path in SQL_DIR.glob("0[1-8]_*.sql")):
        path = SQL_DIR / file_name
        print(f"\n{file_name}")
        for statement in statements(path):
            cursor = before_conn.execute(statement)
            if cursor.description:
                rows = cursor.fetchall()
                print(f"  SELECT returned {len(rows)} row(s); sample={rows[:3]}")
            else:
                print(f"  Statement completed; affected rows={cursor.rowcount}")
    before_conn.close()

    # The DML exercise runs inside a savepoint on the same project database.
    # Roll back before closing even if a statement fails.
    write_conn = sqlite3.connect(DB_FILE)
    write_conn.execute("PRAGMA foreign_keys = ON")
    if write_conn.execute(
        "SELECT COUNT(*) FROM catalog_artist WHERE name='__PHASE11_SQL_DEMO__'"
    ).fetchone()[0]:
        raise SystemExit("Temporary demonstration artist already exists; refusing to run DML.")
    try:
        path = SQL_DIR / "09_insert_update_delete.sql"
        print(f"\n{path.name}")
        for statement in statements(path):
            cursor = write_conn.execute(statement)
            if cursor.description:
                rows = cursor.fetchall()
                print(f"  Result rows={rows}")
            else:
                print(f"  Statement completed; affected rows={cursor.rowcount}")
    except Exception:
        if write_conn.in_transaction:
            write_conn.rollback()
        raise
    after = counts(write_conn)
    integrity = write_conn.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_key_violations = write_conn.execute("PRAGMA foreign_key_check").fetchall()
    temp_count = write_conn.execute(
        "SELECT COUNT(*) FROM catalog_artist WHERE name='__PHASE11_SQL_DEMO__'"
    ).fetchone()[0]
    write_conn.close()
    print(f"\nAfter rollback application counts: {after}")
    print(f"Temporary demo artist rows remaining: {temp_count}")
    print(f"PRAGMA integrity_check: {integrity}")
    print(f"PRAGMA foreign_key_check: {foreign_key_violations}")
    if after != before or temp_count or integrity != "ok" or foreign_key_violations:
        raise SystemExit("Post-run safety verification failed.")
    print("All SQL examples executed; DML rolled back; database counts preserved.")


if __name__ == "__main__":
    main()
