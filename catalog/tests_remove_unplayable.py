"""
Tests for the remove_unplayable_songs management command.

Covers:
- Dry-run mode (no database changes).
- --apply mode (actual deletion).
- Songs with valid audio files are preserved.
- Songs with missing audio files are removed.
- Songs with empty audio_file fields are removed.
- Related SongArtist, SongGenre, Favourite and PlaylistSong records cascade.
- Database integrity holds after deletion.
- Post-deletion: every remaining song has a valid audio file.
"""

import tempfile
from io import StringIO
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre
from playlists.models import Playlist, PlaylistSong
from profiles.models import Favourite


class RemoveUnplayableSongsTests(TestCase):
    """Management command: remove_unplayable_songs"""

    def setUp(self):
        # Temporary media directory so tests don't touch real media files.
        self.media_dir = tempfile.TemporaryDirectory()
        self.media_patch = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_patch.enable()
        self.addCleanup(self.media_patch.disable)
        self.addCleanup(self.media_dir.cleanup)

        # Shared artist and genre
        self.artist = Artist.objects.create(name="Test Artist")
        self.genre = Genre.objects.create(name="Test Genre")

        # User for favourites / playlists
        self.user = User.objects.create_user(username="testuser", password="pass")
        UserProfile.objects.create(user=self.user, role="MEMBER")

        # Song WITH a valid audio file
        self.playable = Song.objects.create(
            title="Playable Song", duration_seconds=120
        )
        self.playable.audio_file.save(
            "test.mp3",
            SimpleUploadedFile("test.mp3", b"ID3\x04\x00audio-data", content_type="audio/mpeg"),
            save=True,
        )
        SongArtist.objects.create(song=self.playable, artist=self.artist)
        SongGenre.objects.create(song=self.playable, genre=self.genre)

        # Song with an EMPTY audio_file field
        self.empty_audio = Song.objects.create(
            title="No Audio Song", duration_seconds=90
        )
        SongArtist.objects.create(song=self.empty_audio, artist=self.artist)
        SongGenre.objects.create(song=self.empty_audio, genre=self.genre)

        # Song whose audio_file field points to a non-existent file
        self.missing_file = Song.objects.create(
            title="Missing File Song",
            duration_seconds=200,
            audio_file="audio/tracks/does_not_exist.mp3",
        )
        SongArtist.objects.create(song=self.missing_file, artist=self.artist)
        SongGenre.objects.create(song=self.missing_file, genre=self.genre)

        # Favourite and playlist entry pointing at the unplayable songs
        self.playlist = Playlist.objects.create(
            owner=self.user, title="Test Playlist", is_public=False
        )
        self.fav_empty = Favourite.objects.create(user=self.user, song=self.empty_audio)
        self.fav_missing = Favourite.objects.create(user=self.user, song=self.missing_file)
        self.ps_empty = PlaylistSong.objects.create(
            playlist=self.playlist, song=self.empty_audio, position=1
        )
        self.ps_missing = PlaylistSong.objects.create(
            playlist=self.playlist, song=self.missing_file, position=2
        )

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _run(self, *args, **kwargs):
        stdout, stderr = StringIO(), StringIO()
        call_command("remove_unplayable_songs", *args, stdout=stdout, stderr=stderr, **kwargs)
        return stdout.getvalue(), stderr.getvalue()

    # ------------------------------------------------------------------
    # Dry-run tests
    # ------------------------------------------------------------------

    def test_dry_run_does_not_delete_any_songs(self):
        """Default execution must not modify the database."""
        before = Song.objects.count()
        self._run()  # no --apply
        self.assertEqual(Song.objects.count(), before)

    def test_dry_run_does_not_delete_related_records(self):
        """Dry run must not remove favourites or playlist songs."""
        self.assertEqual(Favourite.objects.count(), 2)
        self.assertEqual(PlaylistSong.objects.count(), 2)
        self._run()
        self.assertEqual(Favourite.objects.count(), 2)
        self.assertEqual(PlaylistSong.objects.count(), 2)

    def test_dry_run_output_lists_songs_to_remove(self):
        """Dry run output must name the songs that would be deleted."""
        stdout, _ = self._run()
        self.assertIn("No Audio Song", stdout)
        self.assertIn("Missing File Song", stdout)
        self.assertIn("DRY RUN", stdout)

    def test_dry_run_output_lists_songs_to_keep(self):
        """Dry run output must name songs with valid audio as KEEP."""
        stdout, _ = self._run()
        self.assertIn("Playable Song", stdout)
        self.assertIn("KEEP", stdout)

    def test_dry_run_reports_cascade_counts(self):
        """Dry run must report related record counts."""
        stdout, _ = self._run()
        self.assertIn("Favourite", stdout)
        self.assertIn("PlaylistSong", stdout)

    # ------------------------------------------------------------------
    # Apply tests
    # ------------------------------------------------------------------

    def test_apply_removes_songs_without_audio(self):
        """--apply must delete songs that have no valid audio file."""
        self._run(apply=True)
        self.assertFalse(Song.objects.filter(pk=self.empty_audio.pk).exists())
        self.assertFalse(Song.objects.filter(pk=self.missing_file.pk).exists())

    def test_apply_preserves_songs_with_valid_audio(self):
        """--apply must NOT delete songs whose audio file exists."""
        self._run(apply=True)
        self.assertTrue(Song.objects.filter(pk=self.playable.pk).exists())

    def test_apply_cascades_favourites(self):
        """Favourites pointing at deleted songs must be removed."""
        self._run(apply=True)
        self.assertFalse(Favourite.objects.filter(pk=self.fav_empty.pk).exists())
        self.assertFalse(Favourite.objects.filter(pk=self.fav_missing.pk).exists())

    def test_apply_cascades_playlist_songs(self):
        """PlaylistSong rows pointing at deleted songs must be removed."""
        self._run(apply=True)
        self.assertFalse(PlaylistSong.objects.filter(pk=self.ps_empty.pk).exists())
        self.assertFalse(PlaylistSong.objects.filter(pk=self.ps_missing.pk).exists())

    def test_apply_keeps_playlist_itself(self):
        """The Playlist record must survive even if it becomes empty."""
        self._run(apply=True)
        self.assertTrue(Playlist.objects.filter(pk=self.playlist.pk).exists())
        self.assertEqual(
            PlaylistSong.objects.filter(playlist=self.playlist).count(), 0
        )

    def test_apply_cascades_song_artist_junction(self):
        """SongArtist rows for deleted songs must be removed."""
        before = SongArtist.objects.filter(
            song__in=[self.empty_audio, self.missing_file]
        ).count()
        self.assertEqual(before, 2)
        self._run(apply=True)
        self.assertEqual(
            SongArtist.objects.filter(
                song__in=[self.empty_audio, self.missing_file]
            ).count(),
            0,
        )

    def test_apply_cascades_song_genre_junction(self):
        """SongGenre rows for deleted songs must be removed."""
        self._run(apply=True)
        self.assertEqual(
            SongGenre.objects.filter(
                song__in=[self.empty_audio, self.missing_file]
            ).count(),
            0,
        )

    def test_apply_does_not_delete_artists_or_genres(self):
        """Artists and genres must not be touched."""
        self._run(apply=True)
        self.assertTrue(Artist.objects.filter(pk=self.artist.pk).exists())
        self.assertTrue(Genre.objects.filter(pk=self.genre.pk).exists())

    def test_apply_does_not_delete_unrelated_users(self):
        """User accounts must not be touched."""
        self._run(apply=True)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_apply_verification_passes(self):
        """Post-deletion: every remaining song must have a valid audio file."""
        stdout, stderr = self._run(apply=True)
        self.assertIn("Verification passed", stdout)
        self.assertNotIn("WARNING", stderr)

    def test_apply_output_reports_deleted_count(self):
        """Output must report the total rows deleted."""
        stdout, _ = self._run(apply=True)
        self.assertIn("Deleted", stdout)

    def test_apply_idempotent_second_run(self):
        """Running --apply a second time finds nothing to remove."""
        self._run(apply=True)
        stdout, _ = self._run(apply=True)
        self.assertIn("Nothing to remove", stdout)

    # ------------------------------------------------------------------
    # Audio validity edge cases
    # ------------------------------------------------------------------

    def test_zero_byte_file_is_treated_as_invalid(self):
        """A song whose audio file is zero bytes must be removed."""
        zero_song = Song.objects.create(title="Zero Byte", duration_seconds=10)
        zero_path = Path(self.media_dir.name) / "audio" / "tracks"
        zero_path.mkdir(parents=True, exist_ok=True)
        zero_file = zero_path / "zero.mp3"
        zero_file.write_bytes(b"")  # zero bytes
        zero_song.audio_file = "audio/tracks/zero.mp3"
        zero_song.save()

        self._run(apply=True)

        self.assertFalse(Song.objects.filter(pk=zero_song.pk).exists())

    def test_song_with_valid_audio_survives_second_song_deletion(self):
        """Deleting unplayable songs must not affect the playable one."""
        self._run(apply=True)
        surviving = Song.objects.get(pk=self.playable.pk)
        self.assertTrue(Path(surviving.audio_file.path).is_file())
