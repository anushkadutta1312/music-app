"""Focused model, form, catalogue and song-detail tests for local audio playback."""
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import UserProfile
from catalog.forms import SongForm
from catalog.models import Artist, Genre, Song


class CataloguePlaybackTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)
        self.addCleanup(self.media_directory.cleanup)

        self.user = User.objects.create_user(username='playback_member', password='test-password')
        UserProfile.objects.create(user=self.user, display_name='Playback Member', role='MEMBER')
        self.client = Client()
        self.client.force_login(self.user)
        self.artist = Artist.objects.create(name='Sample Composer')
        self.genre = Genre.objects.create(name='Sample Soundtrack')
        self.playable = Song.objects.create(
            title='Playable Sample', album_name='Sample Collection', duration_seconds=90,
        )
        self.playable.artists.add(self.artist)
        self.playable.genres.add(self.genre)
        self.playable.audio_file.save(
            'sample.mp3',
            SimpleUploadedFile('sample.mp3', b'ID3\x04\x00sample-audio', content_type='audio/mpeg'),
            save=True,
        )
        self.missing = Song.objects.create(
            title='Missing Sample', album_name='Sample Collection', duration_seconds=90,
            audio_file='audio/samples/not-present.mp3',
        )

    def song_form_data(self, **overrides):
        data = {
            'title': 'Form Sample',
            'album_name': '',
            'duration_seconds': '80',
            'release_year': '',
            'cover_image_url': '',
            'external_provider': '',
            'external_track_id': '',
            'artists': [str(self.artist.pk)],
            'genres': [str(self.genre.pk)],
        }
        data.update(overrides)
        return data

    def test_audio_file_is_optional_and_a_missing_physical_file_is_unplayable(self):
        ordinary_song = Song.objects.create(title='Existing Metadata Only', duration_seconds=60)
        self.assertFalse(ordinary_song.audio_file.name)
        self.assertEqual(ordinary_song.audio_url, '')
        self.assertEqual(self.missing.audio_url, '')

    def test_existing_mp3_file_returns_a_media_url(self):
        self.assertTrue(Path(self.playable.audio_file.path).is_file())
        self.assertTrue(self.playable.audio_url.endswith('/media/audio/tracks/sample.mp3'))

    def test_song_form_accepts_no_audio_and_rejects_non_mp3_uploads(self):
        optional_audio_form = SongForm(self.song_form_data())
        self.assertTrue(optional_audio_form.is_valid(), optional_audio_form.errors)

        invalid_file_form = SongForm(
            self.song_form_data(),
            {'audio_file': SimpleUploadedFile('notes.txt', b'not audio', content_type='text/plain')},
        )
        self.assertFalse(invalid_file_form.is_valid())
        self.assertIn('audio_file', invalid_file_form.errors)

    def test_catalogue_marks_only_existing_audio_files_as_playable(self):
        response = self.client.get(reverse('catalogue_browse'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-track-title="Playable Sample"')
        self.assertContains(response, 'Audio sample not available')
        self.assertNotContains(response, 'data-track-title="Missing Sample"')

    def test_song_detail_shows_play_action_or_unavailable_message(self):
        playable_response = self.client.get(reverse('song_detail', args=[self.playable.pk]))
        missing_response = self.client.get(reverse('song_detail', args=[self.missing.pk]))

        self.assertContains(playable_response, 'data-track-title="Playable Sample"')
        self.assertContains(missing_response, 'Audio sample not available')
        self.assertNotContains(missing_response, 'data-track-title="Missing Sample"')
