"""Playback queue rendering tests for owner-scoped playlist detail pages."""
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Song
from playlists.models import Playlist, PlaylistSong


class PlaylistPlaybackTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)
        self.addCleanup(self.media_directory.cleanup)

        self.owner = User.objects.create_user(username='playlist_player', password='test-password')
        UserProfile.objects.create(user=self.owner, display_name='Playlist Player', role='MEMBER')
        self.other = User.objects.create_user(username='playlist_other', password='test-password')
        UserProfile.objects.create(user=self.other, display_name='Other Playlist Owner', role='MEMBER')
        artist = Artist.objects.create(name='Playlist Sample Artist')
        self.first = self.make_song('First playable', artist, 'first.mp3')
        self.missing = self.make_song('No audio middle track', artist)
        self.last = self.make_song('Last playable', artist, 'last.mp3')
        self.playlist = Playlist.objects.create(owner=self.owner, title='Mixed Audio Queue')
        for position, song in enumerate((self.first, self.missing, self.last), start=1):
            PlaylistSong.objects.create(playlist=self.playlist, song=song, position=position)
        self.client = Client()
        self.client.force_login(self.owner)

    def make_song(self, title, artist, filename=None):
        song = Song.objects.create(title=title, duration_seconds=100)
        song.artists.add(artist)
        if filename:
            song.audio_file.save(
                filename,
                SimpleUploadedFile(filename, b'ID3\x04\x00sample', content_type='audio/mpeg'),
                save=True,
            )
        return song

    def test_playlist_play_all_keeps_order_and_excludes_unplayable_tracks(self):
        response = self.client.get(reverse('playlist_detail', args=[self.playlist.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Play All (2 playable)')
        self.assertContains(response, 'Audio sample not available')
        self.assertEqual(response.context['playable_count'], 2)
        first_position = response.content.index(b'data-track-title="First playable"')
        last_position = response.content.index(b'data-track-title="Last playable"')
        self.assertLess(first_position, last_position)
        self.assertNotIn(b'data-track-title="No audio middle track"', response.content)

    def test_empty_playlist_and_playlist_without_audio_have_clear_states(self):
        empty_playlist = Playlist.objects.create(owner=self.owner, title='Empty Audio Queue')
        empty_response = self.client.get(reverse('playlist_detail', args=[empty_playlist.pk]))
        self.assertContains(empty_response, 'This playlist is empty')
        self.assertNotContains(empty_response, 'data-player-play-all')

        unavailable_playlist = Playlist.objects.create(owner=self.owner, title='No Audio Queue')
        PlaylistSong.objects.create(playlist=unavailable_playlist, song=self.missing, position=1)
        unavailable_response = self.client.get(reverse('playlist_detail', args=[unavailable_playlist.pk]))
        self.assertContains(unavailable_response, 'This playlist has no available audio samples to play.')
        self.assertNotContains(unavailable_response, 'data-player-play-all')

    def test_other_users_cannot_open_playlist_playback_queue(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('playlist_detail', args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 404)
