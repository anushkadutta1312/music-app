"""
Utility script to inspect the SQLite database schema and constraints.
Demonstrates actual table structures, primary keys, foreign keys, and constraints.
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'

def inspect_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT name, sql 
    FROM sqlite_master 
    WHERE type='table' 
      AND (name LIKE 'accounts_%' OR name LIKE 'catalog_%' OR name LIKE 'playlists_%' OR name LIKE 'profiles_%')
    ORDER BY name;
    """
    cursor.execute(query)
    tables = cursor.fetchall()

    print(f"Total Application Tables Found: {len(tables)}\n")
    for name, sql in tables:
        print("=" * 70)
        print(f"TABLE: {name}")
        print("=" * 70)
        print(sql)
        print("\nINDEXES / CONSTRAINTS:")
        cursor.execute(f"PRAGMA index_list('{name}');")
        for idx in cursor.fetchall():
            print(f"  - Index: {idx[1]} (Unique: {bool(idx[2])})")
        print()

    conn.close()

if __name__ == '__main__':
    inspect_database()
