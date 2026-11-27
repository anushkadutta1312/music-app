"""
Script to generate a clean, high-resolution Entity-Relationship (ER) Diagram PNG.
Uses standard Python PIL to draw all 10 entities, attributes, PK/FK markers, and relationships.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = BASE_DIR / 'docs' / 'database' / 'er_diagram.png'

def create_er_diagram():
    # Canvas dimensions
    width = 1600
    height = 1100
    img = Image.new('RGB', (width, height), color='#1e212b')
    draw = ImageDraw.Draw(img)

    # Colors
    header_color = '#2d3748'
    entity_bg = '#282c37'
    border_color = '#4a5568'
    text_color = '#e2e8f0'
    pk_color = '#ecc94b'
    fk_color = '#63b3ed'
    line_color = '#718096'
    accent_color = '#48bb78'

    # Font setup (use default bitmap font)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Title
    draw.text((40, 25), "MUSIC APP — ENTITY RELATIONSHIP (ER) DIAGRAM", fill='#ffffff', font=font)
    draw.text((40, 45), "Academic DBMS Full Stack Relational Schema • 9 Application Tables + auth_user • 3NF Normalized", fill='#a0aec0', font=font)

    # Entities definition: (x, y, w, h, name, fields[(name, tag)])
    entities = {
        'auth_user': {
            'rect': (50, 100, 240, 180),
            'header': 'auth_user (Django Auth)',
            'fields': [
                ('id', 'PK'),
                ('username', 'UK, NOT NULL'),
                ('email', 'NOT NULL'),
                ('password', 'NOT NULL'),
                ('is_staff', 'DEFAULT False'),
                ('date_joined', 'DATETIME')
            ]
        },
        'accounts_userprofile': {
            'rect': (350, 100, 260, 200),
            'header': 'accounts_userprofile',
            'fields': [
                ('id', 'PK'),
                ('user_id', 'FK, UK (1:1)'),
                ('display_name', 'VARCHAR(100)'),
                ('bio', 'TEXT'),
                ('profile_image', 'VARCHAR(500)'),
                ('role', 'ADMIN | MEMBER'),
                ('created_at', 'DATETIME')
            ]
        },
        'profiles_favourite': {
            'rect': (50, 360, 240, 150),
            'header': 'profiles_favourite',
            'fields': [
                ('id', 'PK'),
                ('user_id', 'FK'),
                ('song_id', 'FK'),
                ('created_at', 'DATETIME'),
                ('[user, song]', 'UNIQUE')
            ]
        },
        'playlists_playlist': {
            'rect': (50, 580, 250, 200),
            'header': 'playlists_playlist',
            'fields': [
                ('id', 'PK'),
                ('owner_id', 'FK -> auth_user'),
                ('title', 'VARCHAR(150)'),
                ('description', 'TEXT'),
                ('is_public', 'DEFAULT False'),
                ('created_at', 'DATETIME'),
                ('updated_at', 'DATETIME')
            ]
        },
        'playlists_playlistsong': {
            'rect': (380, 580, 260, 180),
            'header': 'playlists_playlistsong',
            'fields': [
                ('id', 'PK'),
                ('playlist_id', 'FK'),
                ('song_id', 'FK'),
                ('position', 'CHECK >= 1'),
                ('added_at', 'DATETIME'),
                ('[playlist, song]', 'UNIQUE')
            ]
        },
        'catalog_song': {
            'rect': (720, 350, 280, 250),
            'header': 'catalog_song',
            'fields': [
                ('id', 'PK'),
                ('title', 'VARCHAR(200)'),
                ('album_name', 'VARCHAR(150)'),
                ('duration_seconds', 'CHECK > 0'),
                ('release_year', 'CHECK >= 1900'),
                ('external_provider', 'VARCHAR(50)'),
                ('external_track_id', 'VARCHAR(100)'),
                ('cover_image_url', 'VARCHAR(500)'),
                ('created_at', 'DATETIME')
            ]
        },
        'catalog_songartist': {
            'rect': (1080, 250, 240, 160),
            'header': 'catalog_songartist',
            'fields': [
                ('id', 'PK'),
                ('song_id', 'FK'),
                ('artist_id', 'FK'),
                ('role', 'DEFAULT Primary'),
                ('[song, artist]', 'UNIQUE')
            ]
        },
        'catalog_artist': {
            'rect': (1360, 250, 210, 200),
            'header': 'catalog_artist',
            'fields': [
                ('id', 'PK'),
                ('name', 'UK, NOT NULL'),
                ('biography', 'TEXT'),
                ('image_url', 'VARCHAR(500)'),
                ('external_provider', 'VARCHAR(50)'),
                ('created_at', 'DATETIME')
            ]
        },
        'catalog_songgenre': {
            'rect': (1080, 500, 240, 150),
            'header': 'catalog_songgenre',
            'fields': [
                ('id', 'PK'),
                ('song_id', 'FK'),
                ('genre_id', 'FK'),
                ('[song, genre]', 'UNIQUE')
            ]
        },
        'catalog_genre': {
            'rect': (1360, 500, 210, 150),
            'header': 'catalog_genre',
            'fields': [
                ('id', 'PK'),
                ('name', 'UK, NOT NULL'),
                ('description', 'TEXT'),
                ('created_at', 'DATETIME')
            ]
        }
    }

    # Draw entity boxes
    for key, ent in entities.items():
        x, y, w, h = ent['rect']
        # Background
        draw.rectangle([x, y, x + w, y + h], fill=entity_bg, outline=border_color, width=2)
        # Header banner
        draw.rectangle([x, y, x + w, y + 28], fill=header_color)
        draw.text((x + 8, y + 8), ent['header'], fill='#68d391', font=font)

        # Fields
        cur_y = y + 36
        for name, tag in ent['fields']:
            draw.text((x + 10, cur_y), name, fill=text_color, font=font)
            # Tag color
            if 'PK' in tag:
                t_color = pk_color
            elif 'FK' in tag:
                t_color = fk_color
            elif 'UNIQUE' in tag or 'UK' in tag:
                t_color = '#f6ad55'
            elif 'CHECK' in tag:
                t_color = '#fc8181'
            else:
                t_color = '#a0aec0'
            draw.text((x + 130, cur_y), tag, fill=t_color, font=font)
            cur_y += 18

    # Helper function to draw relationship connector lines
    def draw_rel(pt1, pt2, label=""):
        draw.line([pt1, pt2], fill=line_color, width=2)
        mid_x = (pt1[0] + pt2[0]) // 2
        mid_y = (pt1[1] + pt2[1]) // 2
        if label:
            draw.text((mid_x - 15, mid_y - 12), label, fill='#cbd5e0', font=font)

    # Relationships:
    # 1. auth_user -> accounts_userprofile (1:1)
    draw_rel((290, 160), (350, 160), "1 : 1")
    # 2. auth_user -> profiles_favourite (1:M)
    draw_rel((150, 280), (150, 360), "1 : M")
    # 3. auth_user -> playlists_playlist (1:M)
    draw_rel((150, 510), (150, 580), "1 : M")
    # 4. playlists_playlist -> playlists_playlistsong (1:M)
    draw_rel((300, 650), (380, 650), "1 : M")
    # 5. catalog_song -> playlists_playlistsong (1:M)
    draw_rel((720, 550), (640, 650), "M : 1")
    # 6. catalog_song -> profiles_favourite (1:M)
    draw_rel((720, 430), (290, 430), "M : 1")
    # 7. catalog_song -> catalog_songartist (1:M)
    draw_rel((1000, 400), (1080, 330), "1 : M")
    # 8. catalog_artist -> catalog_songartist (1:M)
    draw_rel((1360, 330), (1320, 330), "1 : M")
    # 9. catalog_song -> catalog_songgenre (1:M)
    draw_rel((1000, 480), (1080, 550), "1 : M")
    # 10. catalog_genre -> catalog_songgenre (1:M)
    draw_rel((1360, 550), (1320, 550), "1 : M")

    # Legend / Legend Box at bottom
    draw.rectangle([50, 850, 1550, 1030], fill='#232731', outline=border_color, width=1)
    draw.text((70, 865), "DATABASE ARCHITECTURE & CONSTRAINTS LEGEND", fill='#ffffff', font=font)
    
    draw.text((70, 900), "• [PK] Primary Key: Clustered auto-incrementing integer key on every table.", fill=pk_color, font=font)
    draw.text((70, 925), "• [FK] Foreign Key: Enforces referential integrity with ON DELETE CASCADE.", fill=fk_color, font=font)
    draw.text((70, 950), "• [UK / UNIQUE]: Prevents duplicate entries (user-profile 1:1, unique favourites, unique playlist songs, unique genre/artist names).", fill='#f6ad55', font=font)
    draw.text((70, 975), "• [CHECK]: Enforces domain boundaries (song duration > 0, release year >= 1900, playlist position >= 1).", fill='#fc8181', font=font)
    draw.text((70, 1000), "• Normalization: Satisfies 1NF (atomic values), 2NF (no partial dependencies), and 3NF (no transitive dependencies).", fill='#68d391', font=font)

    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    img.save(OUTPUT_PATH, 'PNG')
    print(f"ER Diagram PNG generated successfully at {OUTPUT_PATH}")

if __name__ == '__main__':
    create_er_diagram()
