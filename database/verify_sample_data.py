"""
Verification script for db.sqlite3 sample data integrity.
Checks record counts, foreign key integrity, and SQL practical readiness.
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'

def verify():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("1. SQLITE INTEGRITY & FOREIGN KEY CHECKS")
    print("=" * 60)
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchall()
    print(f"PRAGMA integrity_check: {integrity[0][0]}")

    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    print(f"PRAGMA foreign_key_check: {len(fk_violations)} violations found")

    print("\n" + "=" * 60)
    print("2. ACTUAL TABLE ROW COUNTS IN db.sqlite3")
    print("=" * 60)
    tables = [
        'auth_user',
        'accounts_userprofile',
        'catalog_genre',
        'catalog_artist',
        'catalog_song',
        'catalog_songartist',
        'catalog_songgenre',
        'profiles_favourite',
        'playlists_playlist',
        'playlists_playlistsong',
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        cnt = cursor.fetchone()[0]
        print(f"  • {table:<25}: {cnt:>4} rows")

    print("\n" + "=" * 60)
    print("3. SQL PRACTICAL COMPLIANCE CHECKS")
    print("=" * 60)
    # Check LEFT JOIN users without playlists
    cursor.execute("""
        SELECT u.username 
        FROM auth_user u 
        LEFT JOIN playlists_playlist p ON u.id = p.owner_id 
        WHERE p.id IS NULL;
    """)
    users_without_pl = [r[0] for r in cursor.fetchall()]
    print(f"  • Users without playlists (LEFT JOIN test): {users_without_pl}")

    # Check genres with > 5 songs (HAVING test)
    cursor.execute("""
        SELECT g.name, COUNT(sg.song_id) as song_count
        FROM catalog_genre g
        JOIN catalog_songgenre sg ON g.id = sg.genre_id
        GROUP BY g.name
        HAVING song_count > 5
        ORDER BY song_count DESC;
    """)
    genres_above_5 = cursor.fetchall()
    print(f"  • Genres with > 5 songs (GROUP BY + HAVING test): {len(genres_above_5)} genres found")
    for g, c in genres_above_5:
        print(f"      - {g:<15}: {c} songs")

    conn.close()

if __name__ == '__main__':
    verify()
