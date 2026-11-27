from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre
from .models import Favourite


class FavouriteViewsTests(TestCase):
    def setUp(self):
        self.member = self.make_user('member_favourites', 'MEMBER')
        self.admin = self.make_user('admin_favourites', 'ADMIN')
        self.other = self.make_user('other_favourites', 'MEMBER')
        self.artist = Artist.objects.create(name='Favourite Test Artist')
        self.genre = Genre.objects.create(name='Favourite Test Genre')
        self.song = Song.objects.create(
            title='Favourite Test Song', album_name='Test Album',
            duration_seconds=211, release_year=2024,
        )
        SongArtist.objects.create(song=self.song, artist=self.artist)
        SongGenre.objects.create(song=self.song, genre=self.genre)
        self.second_song = Song.objects.create(title='Second Favourite', duration_seconds=180)

    def make_user(self, username, role):
        user = User.objects.create_user(username=username, password='test-password-123')
        UserProfile.objects.create(user=user, display_name=username, role=role)
        return user

    def logged_in_client(self, user, enforce_csrf_checks=False):
        client = Client(enforce_csrf_checks=enforce_csrf_checks)
        client.force_login(user)
        return client

    def json_post(self, client, url, data):
        return client.post(url, data, HTTP_ACCEPT='application/json')

    def test_member_and_admin_can_add_favourites_and_feedback_is_returned(self):
        for user in (self.member, self.admin):
            with self.subTest(role=user.profile.role):
                client = self.logged_in_client(user)
                response = self.json_post(
                    client, reverse('favourite_action', args=[self.song.pk]), {'action': 'add'}
                )
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertTrue(payload['success'])
                self.assertTrue(payload['is_favourited'])
                self.assertTrue(Favourite.objects.filter(user=user, song=self.song).exists())

    def test_duplicate_add_is_idempotent_and_keeps_one_record(self):
        client = self.logged_in_client(self.member)
        url = reverse('favourite_action', args=[self.song.pk])
        first = self.json_post(client, url, {'action': 'add'})
        second = self.json_post(client, url, {'action': 'add'})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertIn('already', second.json()['message'])
        self.assertEqual(Favourite.objects.filter(user=self.member, song=self.song).count(), 1)

    def test_remove_deletes_only_own_favourite_and_preserves_song(self):
        own = Favourite.objects.create(user=self.member, song=self.song)
        other = Favourite.objects.create(user=self.other, song=self.song)

        response = self.json_post(
            self.logged_in_client(self.member),
            reverse('favourite_action', args=[self.song.pk]),
            {'action': 'remove'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_favourited'])
        self.assertFalse(Favourite.objects.filter(pk=own.pk).exists())
        self.assertTrue(Favourite.objects.filter(pk=other.pk).exists())
        self.assertTrue(Song.objects.filter(pk=self.song.pk).exists())

    def test_favourites_page_shows_only_users_songs_and_metadata(self):
        Favourite.objects.create(user=self.member, song=self.song)
        Favourite.objects.create(user=self.other, song=self.second_song)
        response = self.logged_in_client(self.member).get(reverse('my_favourites'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.song.title)
        self.assertContains(response, self.artist.name)
        self.assertContains(response, self.genre.name)
        self.assertContains(response, '3:31')
        self.assertContains(response, reverse('song_detail', args=[self.song.pk]))
        self.assertNotContains(response, self.second_song.title)
        self.assertEqual([fav.song_id for fav in response.context['favourites']], [self.song.pk])

    def test_empty_favourites_page_has_a_helpful_empty_state(self):
        response = self.logged_in_client(self.member).get(reverse('my_favourites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your favourites are empty')
        self.assertContains(response, reverse('catalogue_browse'))

    def test_anonymous_users_are_redirected_from_list_and_mutation(self):
        list_response = self.client.get(reverse('my_favourites'))
        post_response = self.client.post(
            reverse('favourite_action', args=[self.song.pk]), {'action': 'add'}
        )
        for response in (list_response, post_response):
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)
        self.assertFalse(Favourite.objects.exists())

    def test_member_cannot_edit_another_users_favourites_by_forging_owner_parameter(self):
        other_favourite = Favourite.objects.create(user=self.other, song=self.song)
        response = self.json_post(
            self.logged_in_client(self.member),
            reverse('favourite_action', args=[self.song.pk]),
            {'action': 'remove', 'user_id': self.other.pk, 'owner': self.other.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_favourited'])
        self.assertTrue(Favourite.objects.filter(pk=other_favourite.pk).exists())

    def test_admin_cannot_edit_another_users_favourites(self):
        other_favourite = Favourite.objects.create(user=self.other, song=self.song)
        response = self.json_post(
            self.logged_in_client(self.admin),
            reverse('favourite_action', args=[self.song.pk]),
            {'action': 'remove', 'user_id': self.other.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Favourite.objects.filter(user=self.admin, song=self.song).exists())
        self.assertTrue(Favourite.objects.filter(pk=other_favourite.pk).exists())

    def test_invalid_song_id_returns_json_404_without_changes(self):
        response = self.json_post(
            self.logged_in_client(self.member),
            reverse('favourite_action', args=[999999]),
            {'action': 'add'},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])
        self.assertFalse(Favourite.objects.exists())

    def test_invalid_action_returns_json_400(self):
        response = self.json_post(
            self.logged_in_client(self.member),
            reverse('favourite_action', args=[self.song.pk]),
            {'action': 'delete-everything'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertFalse(Favourite.objects.exists())

    def test_get_requests_cannot_change_favourites(self):
        client = self.logged_in_client(self.member)
        response = client.get(reverse('favourite_action', args=[self.song.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertFalse(Favourite.objects.filter(user=self.member, song=self.song).exists())

    def test_normal_post_fallback_redirects_and_updates_favourite(self):
        client = self.logged_in_client(self.member)
        response = client.post(
            reverse('favourite_action', args=[self.song.pk]),
            {'action': 'add'},
            HTTP_REFERER=reverse('catalogue_browse'),
        )
        self.assertRedirects(response, reverse('catalogue_browse'))
        self.assertTrue(Favourite.objects.filter(user=self.member, song=self.song).exists())

    def test_csrf_is_required_for_favourite_posts(self):
        url = reverse('favourite_action', args=[self.song.pk])
        client = self.logged_in_client(self.member, enforce_csrf_checks=True)
        client.get(reverse('catalogue_browse'))
        self.assertIn('csrftoken', client.cookies)

        rejected = client.post(url, {'action': 'add'})
        self.assertEqual(rejected.status_code, 403)
        self.assertFalse(Favourite.objects.filter(user=self.member).exists())

        token = client.cookies['csrftoken'].value
        accepted = client.post(url, {'action': 'add'}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted.status_code, 302)
        self.assertTrue(Favourite.objects.filter(user=self.member, song=self.song).exists())

    def test_catalogue_and_detail_show_current_users_favourite_state(self):
        for user in (self.member, self.admin):
            with self.subTest(role=user.profile.role):
                client = self.logged_in_client(user)
                browse = client.get(reverse('catalogue_browse'))
                detail = client.get(reverse('song_detail', args=[self.song.pk]))
                self.assertContains(browse, '♡ Add to favourites')
                self.assertContains(detail, '♡ Add to favourites')

                Favourite.objects.create(user=user, song=self.song)
                browse = client.get(reverse('catalogue_browse'))
                detail = client.get(reverse('song_detail', args=[self.song.pk]))
                self.assertContains(browse, '♥ Remove from favourites')
                self.assertContains(detail, '♥ Remove from favourites')
