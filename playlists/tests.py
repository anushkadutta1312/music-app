from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from catalog.models import Song
from playlists.models import Playlist, PlaylistSong


class PlaylistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='playlistowner', password='password123')
        self.song1 = Song.objects.create(title='Track 1', duration_seconds=180)
        self.song2 = Song.objects.create(title='Track 2', duration_seconds=210)
        self.playlist = Playlist.objects.create(
            owner=self.user,
            title='Chill Vibes',
            description='Relaxing music for coding',
            is_public=False
        )

    def test_14_create_playlist(self):
        """Verify playlist creation with owner and default privacy."""
        self.assertEqual(self.playlist.owner.username, 'playlistowner')
        self.assertEqual(self.playlist.title, 'Chill Vibes')
        self.assertFalse(self.playlist.is_public)
        self.assertIn('Chill Vibes (by playlistowner)', str(self.playlist))

    def test_15_add_songs_to_playlist(self):
        """Verify adding songs to a playlist with custom ordering."""
        ps1 = PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, position=1)
        ps2 = PlaylistSong.objects.create(playlist=self.playlist, song=self.song2, position=2)
        self.assertEqual(self.playlist.songs.count(), 2)
        self.assertEqual(ps1.position, 1)
        self.assertEqual(ps2.position, 2)

    def test_16_prevent_duplicate_songs_in_same_playlist(self):
        """Verify UNIQUE constraint prevents adding same song twice to same playlist."""
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, position=1)
        with self.assertRaises(IntegrityError):
            PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, position=2)

    def test_17_playlist_song_position_check_constraint(self):
        """Verify CHECK constraint rejects position < 1."""
        with self.assertRaises(IntegrityError):
            PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, position=0)

    def test_18_cascade_deletion_on_playlist_delete(self):
        """Verify junction records are removed when playlist is deleted."""
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, position=1)
        self.assertEqual(PlaylistSong.objects.count(), 1)
        self.playlist.delete()
        self.assertEqual(PlaylistSong.objects.count(), 0)
        # Song itself remains intact in catalog
        self.assertTrue(Song.objects.filter(id=self.song1.id).exists())
