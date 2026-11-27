"""Playback visibility tests for the current user's private favourites."""
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Song
from profiles.models import Favourite


class FavouritePlaybackTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)
        self.addCleanup(self.media_directory.cleanup)

        self.member = User.objects.create_user(username='favourite_player', password='test-password')
        UserProfile.objects.create(user=self.member, display_name='Favourite Player', role='MEMBER')
        self.other = User.objects.create_user(username='other_player', password='test-password')
        UserProfile.objects.create(user=self.other, display_name='Other Player', role='MEMBER')
        self.artist = Artist.objects.create(name='Favourite Sample Artist')
        self.playable = Song.objects.create(title='Favourite Audio', duration_seconds=100)
        self.playable.artists.add(self.artist)
        self.playable.audio_file.save(
            'favourite.mp3',
            SimpleUploadedFile('favourite.mp3', b'ID3\x04\x00sample', content_type='audio/mpeg'),
            save=True,
        )
        self.unplayable = Song.objects.create(title='Favourite Without Audio', duration_seconds=110)
        self.other_song = Song.objects.create(title='Other User Song', duration_seconds=120)
        Favourite.objects.create(user=self.member, song=self.playable)
        Favourite.objects.create(user=self.member, song=self.unplayable)
        Favourite.objects.create(user=self.other, song=self.other_song)
        self.client = Client()
        self.client.force_login(self.member)

    def test_favourites_render_play_and_unavailable_states_without_leaking_other_users(self):
        response = self.client.get(reverse('my_favourites'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-track-title="Favourite Audio"')
        self.assertContains(response, 'Audio sample not available')
        self.assertNotContains(response, 'Other User Song')
        self.assertEqual(
            {favourite.song_id for favourite in response.context['favourites']},
            {self.playable.pk, self.unplayable.pk},
        )

    def test_audio_association_does_not_change_favourite_ownership(self):
        self.client.post(reverse('favourite_action', args=[self.playable.pk]), {'action': 'remove'})
        self.assertFalse(Favourite.objects.filter(user=self.member, song=self.playable).exists())
        self.assertTrue(Favourite.objects.filter(user=self.other, song=self.other_song).exists())
