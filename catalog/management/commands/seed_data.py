"""
Django Management Command: seed_data
Populates the Music App SQLite database with realistic, consistent, and idempotent synthetic sample data.

Usage:
    python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import UserProfile
from catalog.models import Genre, Artist, Song, SongArtist, SongGenre
from playlists.models import Playlist, PlaylistSong
from profiles.models import Favourite


class Command(BaseCommand):
    help = "Populate the database with realistic synthetic sample data (idempotent)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting Music App sample data population..."))

        stats = {
            'users': 0, 'profiles': 0,
            'genres': 0, 'artists': 0, 'songs': 0,
            'song_artists': 0, 'song_genres': 0,
            'favourites': 0, 'playlists': 0, 'playlist_songs': 0
        }

        with transaction.atomic():
            # 1. POPULATE USERS & USER PROFILES (12 Accounts)
            user_data = [
                # Admin (1)
                ('admin_demo', 'admin@musicapp.local', 'AdminDemo2026!', 'System Administrator',
                 'Platform administrator and catalogue curator.', 'ADMIN', True),
                # Members (11)
                ('alex_rhythm', 'alex@musicapp.local', 'MemberDemo2026!', 'Alex Rivera',
                 'Indie rock and alternative music enthusiast.', 'MEMBER', False),
                ('beat_master', 'maya@musicapp.local', 'MemberDemo2026!', 'Maya Chen',
                 'Electronic producer and synthesizer collector.', 'MEMBER', False),
                ('clara_acoustic', 'clara@musicapp.local', 'MemberDemo2026!', 'Clara Oswald',
                 'Acoustic folk and fingerstyle guitarist.', 'MEMBER', False),
                ('david_groove', 'david@musicapp.local', 'MemberDemo2026!', 'David Miller',
                 'Funk, soul, and contemporary R&B lover.', 'MEMBER', False),
                ('elena_classic', 'elena@musicapp.local', 'MemberDemo2026!', 'Elena Rostova',
                 'Classical pianist and orchestral composer.', 'MEMBER', False),
                ('felix_rock', 'felix@musicapp.local', 'MemberDemo2026!', 'Felix Vance',
                 'Classic rock, hard rock, and heavy metal fanatic.', 'MEMBER', False),
                ('grace_jazz', 'grace@musicapp.local', 'MemberDemo2026!', 'Grace Kelly',
                 'Bebop, jazz noir, and brass lover.', 'MEMBER', False),
                ('harper_pop', 'harper@musicapp.local', 'MemberDemo2026!', 'Harper Lee',
                 'Mainstream pop and global chart hit follower.', 'MEMBER', False),
                ('ian_hiphop', 'ian@musicapp.local', 'MemberDemo2026!', 'Ian Wright',
                 'Golden age hip hop and boom-bap connoisseur.', 'MEMBER', False),
                ('julia_ambient', 'julia@musicapp.local', 'MemberDemo2026!', 'Julia Santos',
                 'Deep focus, ambient soundscapes, and lofi explorer.', 'MEMBER', False),
                ('kevin_newbie', 'kevin@musicapp.local', 'MemberDemo2026!', 'Kevin Davis',
                 'Casual listener exploring new musical genres.', 'MEMBER', False),
            ]

            users = {}
            for username, email, password, display_name, bio, role, is_staff in user_data:
                user, u_created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email, 'is_staff': is_staff}
                )
                if u_created:
                    user.set_password(password)
                    user.save()
                    stats['users'] += 1

                users[username] = user

                profile, p_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'display_name': display_name,
                        'bio': bio,
                        'role': role,
                        'profile_image': f'https://images.unsplash.com/photo-user-{username}?w=150'
                    }
                )
                if p_created:
                    stats['profiles'] += 1

            # 2. POPULATE GENRES (10 Genres)
            genre_data = [
                ('Pop', 'Upbeat melodies and mainstream popular music.'),
                ('Rock', 'Guitar-driven rhythms with energetic live instrumentation.'),
                ('Hip-Hop', 'Rhythmic beats, lyricism, and urban culture.'),
                ('Jazz', 'Complex harmonies, swing rhythms, and improvisation.'),
                ('Classical', 'Orchestral, symphonic, and chamber art music.'),
                ('Electronic', 'Synthesizers, drum machines, and electronic dance music.'),
                ('Indie', 'Independent, authentic, and DIY-spirited songcraft.'),
                ('R&B', 'Rhythm and blues blending soul, funk, and modern pop.'),
                ('Alternative', 'Non-conformist rock, post-punk, and experimental sound.'),
                ('Acoustic', 'Unplugged, organic acoustic guitar and vocal performances.')
            ]

            genres = {}
            for name, description in genre_data:
                genre, g_created = Genre.objects.get_or_create(
                    name=name,
                    defaults={'description': description}
                )
                if g_created:
                    stats['genres'] += 1
                genres[name] = genre

            # 3. POPULATE ARTISTS (20 Artists)
            artist_data = [
                ('Daft Punk', 'Legendary French electronic music duo pioneers of French house.', 'https://images.unsplash.com/artist-daft-punk'),
                ('Queen', 'Iconic British rock band fronted by Freddie Mercury.', 'https://images.unsplash.com/artist-queen'),
                ('Miles Davis', 'Visionary American jazz trumpeter, bandleader, and innovator.', 'https://images.unsplash.com/artist-miles-davis'),
                ('Ludwig van Beethoven', 'German composer and pianist who bridged Classical and Romantic eras.', 'https://images.unsplash.com/artist-beethoven'),
                ('Kendrick Lamar', 'Pulitzer Prize-winning Compton hip hop artist and lyricist.', 'https://images.unsplash.com/artist-kendrick'),
                ('Taylor Swift', 'Prolific singer-songwriter spanning country, pop, and indie folk.', 'https://images.unsplash.com/artist-taylor-swift'),
                ('Arctic Monkeys', 'Sheffield indie rock band known for witty lyrics and gritty guitar riffs.', 'https://images.unsplash.com/artist-arctic-monkeys'),
                ('The Weeknd', 'Canadian singer and producer known for moody cinematic R&B.', 'https://images.unsplash.com/artist-the-weeknd'),
                ('Nirvana', 'Grunge band that defined 90s alternative rock music.', 'https://images.unsplash.com/artist-nirvana'),
                ('Ed Sheeran', 'English acoustic pop singer-songwriter and record-breaking artist.', 'https://images.unsplash.com/artist-ed-sheeran'),
                ('Billie Eilish', 'Genre-bending pop artist known for whisper vocals and dark production.', 'https://images.unsplash.com/artist-billie-eilish'),
                ('Radiohead', 'Experimental English rock band pushing musical boundaries.', 'https://images.unsplash.com/artist-radiohead'),
                ('John Coltrane', 'Legendary jazz saxophonist known for modal jazz and free jazz.', 'https://images.unsplash.com/artist-coltrane'),
                ('Johann Sebastian Bach', 'Baroque master of counterpoint, harmony, and organ compositions.', 'https://images.unsplash.com/artist-bach'),
                ('Eminem', 'Detroit rapper celebrated for rapid flow and technical complexity.', 'https://images.unsplash.com/artist-eminem'),
                ('Dua Lipa', 'British-Albanian pop powerhouse known for modern disco-pop.', 'https://images.unsplash.com/artist-dua-lipa'),
                ('Florence + The Machine', 'Indie rock band known for dramatic vocals and art-pop arrangements.', 'https://images.unsplash.com/artist-florence'),
                ('Bruno Mars', 'Multi-talented singer, dancer, and funk/soul revivalist.', 'https://images.unsplash.com/artist-bruno-mars'),
                ('Coldplay', 'Global arena rock and stadium pop band with anthemic melodies.', 'https://images.unsplash.com/artist-coldplay'),
                ('Bon Iver', 'Indie folk band spearheaded by Justin Vernon known for falsetto vocals.', 'https://images.unsplash.com/artist-bon-iver')
            ]

            artists = {}
            for name, bio, img in artist_data:
                artist, a_created = Artist.objects.get_or_create(
                    name=name,
                    defaults={
                        'biography': bio,
                        'image_url': img,
                        'external_provider': 'DemoPlayer',
                        'external_artist_id': f'DEMO_ART_{name.lower().replace(" ", "_").replace("+", "")[:12]}'
                    }
                )
                if a_created:
                    stats['artists'] += 1
                artists[name] = artist

            # 4. POPULATE SONGS (50 Songs)
            # Tuple structure: (title, album, duration, year, primary_artist, [featured_artists], [genres])
            song_catalog = [
                # Daft Punk
                ("One More Time", "Discovery", 320, 2001, "Daft Punk", [], ["Electronic", "Pop"]),
                ("Harder, Better, Faster, Stronger", "Discovery", 224, 2001, "Daft Punk", [], ["Electronic"]),
                ("Get Lucky", "Random Access Memories", 248, 2013, "Daft Punk", [], ["Electronic", "Pop"]),
                ("Around the World", "Homework", 429, 1997, "Daft Punk", [], ["Electronic"]),
                # Queen
                ("Bohemian Rhapsody", "A Night at the Opera", 354, 1975, "Queen", [], ["Rock", "Classical"]),
                ("Don't Stop Me Now", "Jazz", 209, 1978, "Queen", [], ["Rock", "Pop"]),
                ("Under Pressure", "Hot Space", 248, 1981, "Queen", [], ["Rock"]),
                ("Another One Bites the Dust", "The Game", 215, 1980, "Queen", [], ["Rock", "R&B"]),
                # Miles Davis
                ("So What", "Kind of Blue", 562, 1959, "Miles Davis", ["John Coltrane"], ["Jazz"]),
                ("Blue in Green", "Kind of Blue", 337, 1959, "Miles Davis", ["John Coltrane"], ["Jazz"]),
                ("Freddie Freeloader", "Kind of Blue", 589, 1959, "Miles Davis", [], ["Jazz"]),
                # Beethoven
                ("Symphony No. 5 in C Minor", "Symphonies", 432, 1965, "Ludwig van Beethoven", [], ["Classical"]),
                ("Moonlight Sonata", "Piano Sonatas", 360, 1970, "Ludwig van Beethoven", [], ["Classical", "Acoustic"]),
                ("Ode to Joy", "Symphony No. 9", 480, 1968, "Ludwig van Beethoven", [], ["Classical"]),
                # Kendrick Lamar
                ("HUMBLE.", "DAMN.", 177, 2017, "Kendrick Lamar", [], ["Hip-Hop"]),
                ("Alright", "To Pimp a Butterfly", 219, 2015, "Kendrick Lamar", [], ["Hip-Hop", "Jazz"]),
                ("Money Trees", "good kid, m.A.A.d city", 386, 2012, "Kendrick Lamar", [], ["Hip-Hop"]),
                ("King Kunta", "To Pimp a Butterfly", 234, 2015, "Kendrick Lamar", [], ["Hip-Hop", "R&B"]),
                # Taylor Swift
                ("Blank Space", "1989", 231, 2014, "Taylor Swift", [], ["Pop"]),
                ("Anti-Hero", "Midnights", 200, 2022, "Taylor Swift", [], ["Pop", "Indie"]),
                ("Cardigan", "Folklore", 239, 2020, "Taylor Swift", ["Bon Iver"], ["Indie", "Acoustic"]),
                ("Cruel Summer", "Lover", 178, 2019, "Taylor Swift", [], ["Pop"]),
                # Arctic Monkeys
                ("Do I Wanna Know?", "AM", 272, 2013, "Arctic Monkeys", [], ["Indie", "Rock"]),
                ("R U Mine?", "AM", 201, 2013, "Arctic Monkeys", [], ["Indie", "Rock"]),
                ("505", "Favourite Worst Nightmare", 253, 2007, "Arctic Monkeys", [], ["Indie", "Alternative"]),
                ("Why'd You Only Call Me When You're High?", "AM", 161, 2013, "Arctic Monkeys", [], ["Indie", "R&B"]),
                # The Weeknd
                ("Blinding Lights", "After Hours", 200, 2020, "The Weeknd", [], ["R&B", "Pop", "Electronic"]),
                ("Starboy", "Starboy", 230, 2016, "The Weeknd", ["Daft Punk"], ["R&B", "Electronic"]),
                ("Save Your Tears", "After Hours", 215, 2020, "The Weeknd", [], ["R&B", "Pop"]),
                ("The Hills", "Beauty Behind the Madness", 242, 2015, "The Weeknd", [], ["R&B", "Alternative"]),
                # Nirvana
                ("Smells Like Teen Spirit", "Nevermind", 301, 1991, "Nirvana", [], ["Alternative", "Rock"]),
                ("Come As You Are", "Nevermind", 219, 1991, "Nirvana", [], ["Alternative", "Rock"]),
                ("Heart-Shaped Box", "In Utero", 281, 1993, "Nirvana", [], ["Alternative", "Rock"]),
                # Ed Sheeran
                ("Shape of You", "Divide", 233, 2017, "Ed Sheeran", [], ["Pop", "Acoustic"]),
                ("Perfect", "Divide", 263, 2017, "Ed Sheeran", [], ["Pop", "Acoustic"]),
                ("Thinking Out Loud", "Multiply", 281, 2014, "Ed Sheeran", [], ["Acoustic", "Pop"]),
                # Billie Eilish
                ("Bad Guy", "When We All Fall Asleep", 194, 2019, "Billie Eilish", [], ["Pop", "Electronic"]),
                ("Happier Than Ever", "Happier Than Ever", 298, 2021, "Billie Eilish", [], ["Alternative", "Rock"]),
                ("Ocean Eyes", "Don't Smile at Me", 200, 2016, "Billie Eilish", [], ["Indie", "Pop"]),
                # Radiohead
                ("Creep", "Pablo Honey", 238, 1993, "Radiohead", [], ["Alternative", "Rock"]),
                ("Karma Police", "OK Computer", 264, 1997, "Radiohead", [], ["Alternative", "Rock"]),
                ("No Surprises", "OK Computer", 228, 1997, "Radiohead", [], ["Alternative", "Indie"]),
                # John Coltrane
                ("A Love Supreme, Pt. 1", "A Love Supreme", 462, 1965, "John Coltrane", [], ["Jazz"]),
                ("Giant Steps", "Giant Steps", 283, 1960, "John Coltrane", [], ["Jazz"]),
                # Bach
                ("Toccata and Fugue in D Minor", "Organ Works", 540, 1960, "Johann Sebastian Bach", [], ["Classical"]),
                # Eminem
                ("Lose Yourself", "8 Mile Soundtrack", 326, 2002, "Eminem", [], ["Hip-Hop"]),
                ("Without Me", "The Eminem Show", 290, 2002, "Eminem", [], ["Hip-Hop"]),
                # Dua Lipa
                ("Levitating", "Future Nostalgia", 203, 2020, "Dua Lipa", [], ["Pop", "Electronic"]),
                ("Don't Start Now", "Future Nostalgia", 183, 2019, "Dua Lipa", [], ["Pop", "Electronic"]),
                # Florence + The Machine
                ("Dog Days Are Over", "Lungs", 252, 2009, "Florence + The Machine", [], ["Indie", "Rock"]),
                # Bruno Mars
                ("Uptown Funk", "Uptown Special", 269, 2014, "Bruno Mars", [], ["R&B", "Pop"]),
                # Coldplay
                ("Viva La Vida", "Viva la Vida", 242, 2008, "Coldplay", [], ["Rock", "Pop"]),
                ("Yellow", "Parachutes", 269, 2000, "Coldplay", [], ["Rock", "Indie"]),
                # Bon Iver
                ("Skinny Love", "For Emma, Forever Ago", 239, 2007, "Bon Iver", [], ["Indie", "Acoustic"]),
                ("Holocene", "Bon Iver", 336, 2011, "Bon Iver", [], ["Indie", "Acoustic"])
            ]

            songs = {}
            for idx, (title, album, duration, year, primary_art, featured_arts, song_genres) in enumerate(song_catalog, 1):
                song, s_created = Song.objects.get_or_create(
                    title=title,
                    defaults={
                        'album_name': album,
                        'duration_seconds': duration,
                        'release_year': year,
                        'cover_image_url': f'https://images.unsplash.com/album-cover-{idx}?w=300',
                        'external_provider': 'DemoPlayer',
                        'external_track_id': f'DEMO_TRK_{idx:02d}'
                    }
                )
                if s_created:
                    stats['songs'] += 1
                songs[title] = song

                # Link Primary Artist
                if primary_art in artists:
                    sa, sa_created = SongArtist.objects.get_or_create(
                        song=song,
                        artist=artists[primary_art],
                        defaults={'role': 'Primary'}
                    )
                    if sa_created:
                        stats['song_artists'] += 1

                # Link Featured Artists
                for feat in featured_arts:
                    if feat in artists:
                        sa_f, feat_created = SongArtist.objects.get_or_create(
                            song=song,
                            artist=artists[feat],
                            defaults={'role': 'Featured'}
                        )
                        if feat_created:
                            stats['song_artists'] += 1

                # Link Genres
                for g_name in song_genres:
                    if g_name in genres:
                        sg, sg_created = SongGenre.objects.get_or_create(
                            song=song,
                            genre=genres[g_name]
                        )
                        if sg_created:
                            stats['song_genres'] += 1

            # 5. POPULATE FAVOURITES (40+ Favourites)
            favourite_matrix = [
                ('alex_rhythm', ["Do I Wanna Know?", "505", "Smells Like Teen Spirit", "Skinny Love", "Dog Days Are Over"]),
                ('beat_master', ["One More Time", "Harder, Better, Faster, Stronger", "Get Lucky", "Starboy", "Levitating"]),
                ('clara_acoustic', ["Skinny Love", "Holocene", "Shape of You", "Perfect", "Moonlight Sonata"]),
                ('david_groove', ["Starboy", "Save Your Tears", "Uptown Funk", "Another One Bites the Dust", "HUMBLE."]),
                ('elena_classic', ["Symphony No. 5 in C Minor", "Moonlight Sonata", "Ode to Joy", "Toccata and Fugue in D Minor", "Bohemian Rhapsody"]),
                ('felix_rock', ["Bohemian Rhapsody", "Don't Stop Me Now", "Smells Like Teen Spirit", "Creep", "Viva La Vida"]),
                ('grace_jazz', ["So What", "Blue in Green", "Freddie Freeloader", "A Love Supreme, Pt. 1", "Giant Steps"]),
                ('harper_pop', ["Blank Space", "Anti-Hero", "Levitating", "Save Your Tears", "Shape of You", "Bad Guy"]),
                ('ian_hiphop', ["HUMBLE.", "Alright", "Money Trees", "Lose Yourself", "Without Me"]),
                ('julia_ambient', ["Holocene", "Moonlight Sonata", "Blue in Green", "Skinny Love"]),
                ('admin_demo', ["Bohemian Rhapsody", "One More Time", "So What", "Lose Yourself"])
                # Note: 'kevin_newbie' left with 0 favourites to allow testing IS NULL in SQL practicals!
            ]

            for username, fav_titles in favourite_matrix:
                user = users.get(username)
                if not user:
                    continue
                for title in fav_titles:
                    song = songs.get(title)
                    if song:
                        fav, fav_created = Favourite.objects.get_or_create(
                            user=user,
                            song=song
                        )
                        if fav_created:
                            stats['favourites'] += 1

            # 6. POPULATE PLAYLISTS (15 Playlists)
            # Assigned across users, leaving 'kevin_newbie' with 0 playlists for SQL LEFT JOIN demonstration!
            playlists_data = [
                ('alex_rhythm', "Indie Discoveries", "Deep dive into indie rock gems and intimate vocals.", True),
                ('alex_rhythm', "Late Night Vibes", "Mellow acoustic and alternative tracks for midnight hours.", False),
                ('beat_master', "Workout Energy", "High-BPM electronic and dance anthems for maximum gym pump.", True),
                ('beat_master', "Synthwave & Future Funk", "Modern electronic funk, retro synth and disco grooves.", True),
                ('clara_acoustic', "Acoustic Sessions", "Stripped-back singer-songwriter acoustic recordings.", True),
                ('clara_acoustic', "Sunday Morning Coffee", "Warm, comforting folk melodies to ease into the day.", False),
                ('david_groove', "R&B Late Night Lounge", "Smooth contemporary R&B, neo-soul, and sensual melodies.", True),
                ('david_groove', "Funk & Disco Revival", "High-energy grooves guaranteed to move the crowd.", True),
                ('elena_classic', "Classical Masterworks", "Timeless orchestral symphonies and delicate piano sonatas.", True),
                ('felix_rock', "Rock Classics & Anthems", "Stomp-your-feet stadium rock anthems of all time.", True),
                ('felix_rock', "90s Alternative Waves", "Grunge and alternative rock classics from the 1990s.", True),
                ('grace_jazz', "Midnight Jazz Club", "Smoky saxophone solos and improvisational modal jazz.", True),
                ('harper_pop', "Pop Hits 2024", "Chart-topping viral pop sensations and party radio hits.", True),
                ('ian_hiphop', "Golden Age Hip-Hop", "Lyrical masterpieces, boom-bap drums, and storytelling.", True),
                ('admin_demo', "Curator's Showcase", "Staff-selected masterpieces spanning all major genres.", True),
            ]

            playlists = {}
            for owner_name, title, desc, is_public in playlists_data:
                owner = users.get(owner_name)
                if not owner:
                    continue
                playlist, pl_created = Playlist.objects.get_or_create(
                    owner=owner,
                    title=title,
                    defaults={
                        'description': desc,
                        'is_public': is_public,
                        'cover_image_url': f'https://images.unsplash.com/playlist-{title.lower().replace(" ", "-")}'
                    }
                )
                if pl_created:
                    stats['playlists'] += 1
                playlists[title] = playlist

            # 7. POPULATE PLAYLIST SONGS (55+ Playlist-Song associations)
            playlist_tracks = {
                "Indie Discoveries": ["Do I Wanna Know?", "505", "Cardigan", "Dog Days Are Over", "Holocene"],
                "Late Night Vibes": ["No Surprises", "Skinny Love", "Ocean Eyes", "Save Your Tears"],
                "Workout Energy": ["Harder, Better, Faster, Stronger", "Lose Yourself", "HUMBLE.", "Levitating", "Don't Start Now"],
                "Synthwave & Future Funk": ["One More Time", "Get Lucky", "Starboy", "Blinding Lights"],
                "Acoustic Sessions": ["Shape of You", "Perfect", "Thinking Out Loud", "Skinny Love", "Moonlight Sonata"],
                "Sunday Morning Coffee": ["Yellow", "Holocene", "Cardigan", "Blue in Green"],
                "R&B Late Night Lounge": ["Starboy", "Save Your Tears", "The Hills", "Blinding Lights"],
                "Funk & Disco Revival": ["Uptown Funk", "Another One Bites the Dust", "Get Lucky", "Don't Start Now"],
                "Classical Masterworks": ["Symphony No. 5 in C Minor", "Moonlight Sonata", "Ode to Joy", "Toccata and Fugue in D Minor"],
                "Rock Classics & Anthems": ["Bohemian Rhapsody", "Don't Stop Me Now", "Under Pressure", "Another One Bites the Dust", "Viva La Vida"],
                "90s Alternative Waves": ["Smells Like Teen Spirit", "Come As You Are", "Heart-Shaped Box", "Creep", "Karma Police"],
                "Midnight Jazz Club": ["So What", "Blue in Green", "Freddie Freeloader", "A Love Supreme, Pt. 1", "Giant Steps"],
                "Pop Hits 2024": ["Blank Space", "Anti-Hero", "Cruel Summer", "Bad Guy", "Levitating"],
                "Golden Age Hip-Hop": ["Lose Yourself", "Without Me", "HUMBLE.", "Alright", "Money Trees"],
                "Curator's Showcase": ["Bohemian Rhapsody", "So What", "One More Time", "Lose Yourself", "Symphony No. 5 in C Minor", "Blinding Lights"]
            }

            for pl_title, song_titles in playlist_tracks.items():
                playlist = playlists.get(pl_title)
                if not playlist:
                    continue
                for pos, song_title in enumerate(song_titles, 1):
                    song = songs.get(song_title)
                    if song:
                        ps, ps_created = PlaylistSong.objects.get_or_create(
                            playlist=playlist,
                            song=song,
                            defaults={'position': pos}
                        )
                        if ps_created:
                            stats['playlist_songs'] += 1

        # Summary output
        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Sample Data Population Completed!"))
        self.stdout.write("--------------------------------------------------")
        self.stdout.write(f"  • Users Created / Existing:          {User.objects.count()} (New: {stats['users']})")
        self.stdout.write(f"  • User Profiles Created / Existing:  {UserProfile.objects.count()} (New: {stats['profiles']})")
        self.stdout.write(f"  • Genres Created / Existing:         {Genre.objects.count()} (New: {stats['genres']})")
        self.stdout.write(f"  • Artists Created / Existing:        {Artist.objects.count()} (New: {stats['artists']})")
        self.stdout.write(f"  • Songs Created / Existing:          {Song.objects.count()} (New: {stats['songs']})")
        self.stdout.write(f"  • Song-Artist Links:                 {SongArtist.objects.count()} (New: {stats['song_artists']})")
        self.stdout.write(f"  • Song-Genre Links:                  {SongGenre.objects.count()} (New: {stats['song_genres']})")
        self.stdout.write(f"  • Favourite Bookmarks:               {Favourite.objects.count()} (New: {stats['favourites']})")
        self.stdout.write(f"  • Playlists Created / Existing:      {Playlist.objects.count()} (New: {stats['playlists']})")
        self.stdout.write(f"  • Playlist-Song Links:               {PlaylistSong.objects.count()} (New: {stats['playlist_songs']})")
        self.stdout.write("--------------------------------------------------")
