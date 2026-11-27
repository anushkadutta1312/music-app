from django.test import TestCase
from django.db import IntegrityError
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


class CatalogModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(
            name='Daft Punk',
            biography='French electronic music duo formed in 1993.',
            external_provider='YouTube',
            external_artist_id='artist_daft_punk'
        )
        self.genre = Genre.objects.create(
            name='Electronic',
            description='Music that employs electronic musical instruments.'
        )
        self.song = Song.objects.create(
            title='One More Time',
            album_name='Discovery',
            duration_seconds=320,
            release_year=2001,
            external_provider='YouTube',
            external_track_id='FGBhQbmPwH8'
        )

    def test_04_artist_creation(self):
        """Verify artist record creation and string representation."""
        self.assertEqual(str(self.artist), 'Daft Punk')
        self.assertEqual(self.artist.name, 'Daft Punk')

    def test_05_prevent_duplicate_artist_name(self):
        """Verify UNIQUE constraint on artist name."""
        with self.assertRaises(IntegrityError):
            Artist.objects.create(name='Daft Punk')

    def test_06_genre_creation(self):
        """Verify genre record creation and uniqueness."""
        self.assertEqual(str(self.genre), 'Electronic')
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name='Electronic')

    def test_07_song_creation(self):
        """Verify song metadata creation."""
        self.assertEqual(str(self.song), 'One More Time')
        self.assertEqual(self.song.duration_seconds, 320)
        self.assertEqual(self.song.release_year, 2001)

    def test_08_song_duration_check_constraint(self):
        """Verify database rejects songs with duration <= 0."""
        with self.assertRaises(IntegrityError):
            Song.objects.create(
                title='Invalid Duration Song',
                duration_seconds=0
            )

    def test_09_song_artist_relationship(self):
        """Verify M:N junction table SongArtist."""
        sa = SongArtist.objects.create(
            song=self.song,
            artist=self.artist,
            role='Primary'
        )
        self.assertEqual(self.song.artists.count(), 1)
        self.assertEqual(self.artist.songs.count(), 1)
        self.assertIn('One More Time - Daft Punk (Primary)', str(sa))

    def test_10_prevent_duplicate_song_artist(self):
        """Verify unique constraint on song + artist junction."""
        SongArtist.objects.create(song=self.song, artist=self.artist, role='Primary')
        with self.assertRaises(IntegrityError):
            SongArtist.objects.create(song=self.song, artist=self.artist, role='Featured')

    def test_11_song_genre_relationship(self):
        """Verify M:N junction table SongGenre."""
        sg = SongGenre.objects.create(song=self.song, genre=self.genre)
        self.assertEqual(self.song.genres.count(), 1)
        self.assertEqual(self.genre.songs.count(), 1)
        self.assertEqual(str(sg), 'One More Time - Electronic')

    def test_12_prevent_duplicate_song_genre(self):
        """Verify unique constraint on song + genre junction."""
        SongGenre.objects.create(song=self.song, genre=self.genre)
        with self.assertRaises(IntegrityError):
            SongGenre.objects.create(song=self.song, genre=self.genre)

    def test_13_cascade_deletion_on_song_delete(self):
        """Verify junction records are deleted when a song is deleted."""
        SongArtist.objects.create(song=self.song, artist=self.artist)
        SongGenre.objects.create(song=self.song, genre=self.genre)
        self.assertEqual(SongArtist.objects.count(), 1)
        self.assertEqual(SongGenre.objects.count(), 1)
        self.song.delete()
        self.assertEqual(SongArtist.objects.count(), 0)
        self.assertEqual(SongGenre.objects.count(), 0)
        # Artist and Genre remain intact
        self.assertTrue(Artist.objects.filter(name='Daft Punk').exists())
        self.assertTrue(Genre.objects.filter(name='Electronic').exists())
