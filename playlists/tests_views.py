from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre
from .forms import PlaylistForm
from .models import Playlist, PlaylistSong


class PlaylistFormTests(TestCase):
    def test_name_is_required_and_whitespace_is_trimmed(self):
        self.assertFalse(PlaylistForm({'title': '   ', 'description': ''}).is_valid())

        form = PlaylistForm({'title': '  Evening Drive  ', 'description': '  mellow songs  '})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['title'], 'Evening Drive')
        self.assertEqual(form.cleaned_data['description'], 'mellow songs')
        self.assertNotIn('owner', form.fields)

    def test_title_longer_than_model_limit_is_rejected(self):
        form = PlaylistForm({'title': 'x' * 151, 'description': ''})
        self.assertFalse(form.is_valid())


class PlaylistViewsTests(TestCase):
    def setUp(self):
        self.member = self.make_user('playlist_member_a', 'MEMBER')
        self.other_member = self.make_user('playlist_member_b', 'MEMBER')
        self.admin = self.make_user('playlist_admin', 'ADMIN')
        self.artist = Artist.objects.create(name='Playlist Test Artist')
        self.genre = Genre.objects.create(name='Playlist Test Genre')
        self.songs = [
            Song.objects.create(
                title=f'Playlist Track {index}',
                album_name='Test Album',
                duration_seconds=180 + index,
                release_year=2024,
            )
            for index in range(1, 5)
        ]
        SongArtist.objects.create(song=self.songs[0], artist=self.artist)
        SongGenre.objects.create(song=self.songs[0], genre=self.genre)
        self.playlist = Playlist.objects.create(
            owner=self.member, title='Member Private Playlist', description='Original description'
        )
        self.other_playlist = Playlist.objects.create(
            owner=self.other_member, title='Other Private Playlist'
        )
        self.admin_playlist = Playlist.objects.create(
            owner=self.admin, title='Admin Private Playlist'
        )

    def make_user(self, username, role):
        user = User.objects.create_user(username=username, password='playlist-test-password')
        UserProfile.objects.create(user=user, display_name=username, role=role)
        return user

    def login(self, user, enforce_csrf_checks=False):
        client = Client(enforce_csrf_checks=enforce_csrf_checks)
        client.force_login(user)
        return client

    def api_post(self, client, url, data):
        return client.post(url, data, HTTP_ACCEPT='application/json')

    def action_url(self, playlist=None, song=None):
        return reverse('playlist_song_action', args=[
            (playlist or self.playlist).pk,
            (song or self.songs[0]).pk,
        ])

    def test_members_and_admins_create_private_playlists_owned_by_the_session_user(self):
        for user in (self.member, self.admin):
            with self.subTest(role=user.profile.role):
                response = self.login(user).post(reverse('playlist_create'), {
                    'title': '  Weekend Mix  ',
                    'description': '  Road songs  ',
                    'owner': self.other_member.pk,
                    'owner_id': self.other_member.pk,
                    'is_public': 'on',
                })
                self.assertEqual(response.status_code, 302)
                created = Playlist.objects.get(owner=user, title='Weekend Mix')
                self.assertEqual(created.description, 'Road songs')
                self.assertFalse(created.is_public)
                self.assertFalse(Playlist.objects.filter(owner=self.other_member, title='Weekend Mix').exists())

    def test_blank_playlist_name_is_rejected_without_creating_a_record(self):
        response = self.login(self.member).post(reverse('playlist_create'), {
            'title': '   ', 'description': 'No title',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a playlist name.')
        self.assertFalse(Playlist.objects.filter(owner=self.member, description='No title').exists())

    def test_list_is_owner_scoped_and_includes_song_counts_and_empty_state(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[0], position=1)
        PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[1], position=2)
        response = self.login(self.member).get(reverse('playlist_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.playlist.title)
        self.assertContains(response, '2 songs')
        self.assertNotContains(response, self.other_playlist.title)
        self.assertNotContains(response, self.admin_playlist.title)

        empty_user = self.make_user('playlist_empty_user', 'MEMBER')
        empty_response = self.login(empty_user).get(reverse('playlist_list'))
        self.assertContains(empty_response, 'You have no playlists yet')

    def test_detail_shows_saved_order_song_metadata_and_empty_state(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[1], position=1)
        PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[0], position=2)
        response = self.login(self.member).get(
            reverse('playlist_detail', args=[self.playlist.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artist.name)
        self.assertContains(response, self.genre.name)
        self.assertContains(response, 'Test Album')
        self.assertContains(response, '3:01')
        self.assertLess(response.content.index(b'Playlist Track 2'), response.content.index(b'Playlist Track 1'))
        self.assertEqual(response.context['song_count'], 2)

        empty_response = self.login(self.other_member).get(
            reverse('playlist_detail', args=[self.other_playlist.pk])
        )
        self.assertContains(empty_response, 'This playlist is empty')

    def test_edit_changes_only_owner_editable_fields_and_ignores_submitted_owner(self):
        response = self.login(self.member).post(
            reverse('playlist_update', args=[self.playlist.pk]),
            {'title': '  Updated Mix  ', 'description': '  New description  ', 'owner': self.other_member.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.title, 'Updated Mix')
        self.assertEqual(self.playlist.description, 'New description')
        self.assertEqual(self.playlist.owner, self.member)

    def test_playlist_delete_requires_post_and_keeps_catalogue_songs(self):
        link = PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[0], position=1)
        client = self.login(self.member)
        confirm = client.get(reverse('playlist_delete', args=[self.playlist.pk]))
        self.assertEqual(confirm.status_code, 200)
        self.assertTrue(Playlist.objects.filter(pk=self.playlist.pk).exists())
        self.assertContains(confirm, 'Confirm Delete')

        response = client.post(reverse('playlist_delete', args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Playlist.objects.filter(pk=self.playlist.pk).exists())
        self.assertFalse(PlaylistSong.objects.filter(pk=link.pk).exists())
        self.assertTrue(Song.objects.filter(pk=self.songs[0].pk).exists())

    def test_anonymous_users_are_redirected_from_playlist_pages_and_mutations(self):
        urls = [
            reverse('playlist_list'),
            reverse('playlist_create'),
            reverse('playlist_detail', args=[self.playlist.pk]),
            reverse('playlist_update', args=[self.playlist.pk]),
            reverse('playlist_delete', args=[self.playlist.pk]),
            reverse('playlist_add_song', args=[self.songs[0].pk]),
            self.action_url(),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.post(url, {'action': 'remove', 'playlist_id': self.playlist.pk})
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)
        self.assertTrue(Playlist.objects.filter(pk=self.playlist.pk).exists())

    def test_get_requests_cannot_mutate_playlist_songs(self):
        add_get = self.login(self.member).get(
            reverse('playlist_add_song', args=[self.songs[0].pk]), {'playlist_id': self.playlist.pk}
        )
        action_get = self.login(self.member).get(self.action_url())
        self.assertEqual(add_get.status_code, 405)
        self.assertEqual(action_get.status_code, 405)
        self.assertFalse(PlaylistSong.objects.exists())

    def test_other_member_cannot_view_edit_delete_or_change_another_playlist(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[0], position=1)
        client = self.login(self.other_member)
        requests = [
            client.get(reverse('playlist_detail', args=[self.playlist.pk])),
            client.get(reverse('playlist_update', args=[self.playlist.pk])),
            client.post(reverse('playlist_update', args=[self.playlist.pk]), {'title': 'Hijacked'}),
            client.get(reverse('playlist_delete', args=[self.playlist.pk])),
            client.post(reverse('playlist_delete', args=[self.playlist.pk])),
            self.api_post(client, reverse('playlist_add_song', args=[self.songs[1].pk]), {
                'playlist_id': self.playlist.pk,
            }),
            self.api_post(client, self.action_url(), {'action': 'remove'}),
            self.api_post(client, reverse('playlist_song_action', args=[self.playlist.pk, self.songs[0].pk]), {
                'action': 'move_down',
            }),
        ]
        for response in requests:
            self.assertEqual(response.status_code, 404)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.title, 'Member Private Playlist')
        self.assertEqual(list(self.playlist.playlist_songs.values_list('song_id', 'position')), [(self.songs[0].pk, 1)])
        self.assertTrue(Playlist.objects.filter(pk=self.playlist.pk).exists())

    def test_admin_cannot_manage_another_users_private_playlist(self):
        PlaylistSong.objects.create(playlist=self.other_playlist, song=self.songs[0], position=1)
        client = self.login(self.admin)
        detail = client.get(reverse('playlist_detail', args=[self.other_playlist.pk]))
        edit = client.post(reverse('playlist_update', args=[self.other_playlist.pk]), {
            'title': 'Administrator overwrite', 'description': 'Must not persist',
        })
        delete = client.post(reverse('playlist_delete', args=[self.other_playlist.pk]))
        add = self.api_post(client, reverse('playlist_add_song', args=[self.songs[1].pk]), {
            'playlist_id': self.other_playlist.pk,
        })
        remove = self.api_post(client, reverse('playlist_song_action', args=[
            self.other_playlist.pk, self.songs[0].pk,
        ]), {'action': 'remove'})
        reorder = self.api_post(client, reverse('playlist_song_action', args=[
            self.other_playlist.pk, self.songs[0].pk,
        ]), {'action': 'move_down'})
        self.assertEqual(detail.status_code, 404)
        self.assertEqual(edit.status_code, 404)
        self.assertEqual(delete.status_code, 404)
        self.assertEqual(add.status_code, 404)
        self.assertEqual(remove.status_code, 404)
        self.assertEqual(reorder.status_code, 404)
        self.other_playlist.refresh_from_db()
        self.assertEqual(self.other_playlist.title, 'Other Private Playlist')
        self.assertTrue(PlaylistSong.objects.filter(playlist=self.other_playlist, song=self.songs[0]).exists())

    def test_admin_can_edit_and_delete_their_own_playlist(self):
        client = self.login(self.admin)
        edit = client.post(reverse('playlist_update', args=[self.admin_playlist.pk]), {
            'title': 'Admin Updated', 'description': 'Updated by its owner.',
        })
        self.assertEqual(edit.status_code, 302)
        self.admin_playlist.refresh_from_db()
        self.assertEqual(self.admin_playlist.title, 'Admin Updated')
        delete = client.post(reverse('playlist_delete', args=[self.admin_playlist.pk]))
        self.assertEqual(delete.status_code, 302)
        self.assertFalse(Playlist.objects.filter(pk=self.admin_playlist.pk).exists())

    def test_add_song_works_for_both_roles_and_appends_with_valid_positions(self):
        for user in (self.member, self.admin):
            with self.subTest(role=user.profile.role):
                playlist = Playlist.objects.create(owner=user, title=f'{user.username} list')
                client = self.login(user)
                response = self.api_post(client, reverse('playlist_add_song', args=[self.songs[0].pk]), {
                    'playlist_id': playlist.pk,
                })
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()['created'])
                row = PlaylistSong.objects.get(playlist=playlist, song=self.songs[0])
                self.assertEqual(row.position, 1)
                self.assertGreaterEqual(row.position, 1)

    def test_duplicate_add_is_prevented_without_changing_existing_position(self):
        existing = PlaylistSong.objects.create(playlist=self.playlist, song=self.songs[0], position=1)
        response = self.api_post(
            self.login(self.member),
            reverse('playlist_add_song', args=[self.songs[0].pk]),
            {'playlist_id': self.playlist.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['created'])
        self.assertEqual(PlaylistSong.objects.filter(playlist=self.playlist, song=self.songs[0]).count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.position, 1)

    def test_add_rejects_nonexistent_song_and_invalid_or_foreign_playlist_ids(self):
        client = self.login(self.member)
        bad_song = self.api_post(client, reverse('playlist_add_song', args=[999999]), {
            'playlist_id': self.playlist.pk,
        })
        bad_playlist = self.api_post(client, reverse('playlist_add_song', args=[self.songs[0].pk]), {
            'playlist_id': '999999',
        })
        foreign_playlist = self.api_post(client, reverse('playlist_add_song', args=[self.songs[0].pk]), {
            'playlist_id': self.other_playlist.pk,
        })
        invalid_playlist = self.api_post(client, reverse('playlist_add_song', args=[self.songs[0].pk]), {
            'playlist_id': 'not-an-id',
        })
        self.assertEqual(bad_song.status_code, 404)
        self.assertEqual(bad_playlist.status_code, 404)
        self.assertEqual(foreign_playlist.status_code, 404)
        self.assertEqual(invalid_playlist.status_code, 400)
        self.assertFalse(PlaylistSong.objects.exists())

    def test_remove_song_preserves_catalogue_record_and_normalizes_positions(self):
        rows = [
            PlaylistSong.objects.create(playlist=self.playlist, song=song, position=index)
            for index, song in enumerate(self.songs[:3], start=1)
        ]
        response = self.api_post(
            self.login(self.member), self.action_url(self.playlist, self.songs[1]), {'action': 'remove'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        remaining = list(PlaylistSong.objects.filter(playlist=self.playlist).order_by('position'))
        self.assertEqual([(row.song_id, row.position) for row in remaining], [
            (self.songs[0].pk, 1), (self.songs[2].pk, 2),
        ])
        self.assertTrue(Song.objects.filter(pk=self.songs[1].pk).exists())

    def test_move_up_and_down_persist_contiguous_positions(self):
        for index, song in enumerate(self.songs[:3], start=1):
            PlaylistSong.objects.create(playlist=self.playlist, song=song, position=index)
        client = self.login(self.member)

        up = self.api_post(client, self.action_url(self.playlist, self.songs[2]), {'action': 'move_up'})
        self.assertEqual(up.status_code, 200)
        self.assertEqual(up.json()['positions'], [
            {'song_id': self.songs[0].pk, 'position': 1},
            {'song_id': self.songs[2].pk, 'position': 2},
            {'song_id': self.songs[1].pk, 'position': 3},
        ])

        down = self.api_post(client, self.action_url(self.playlist, self.songs[0]), {'action': 'move_down'})
        self.assertEqual(down.status_code, 200)
        rows = list(PlaylistSong.objects.filter(playlist=self.playlist).order_by('position'))
        self.assertEqual([(row.song_id, row.position) for row in rows], [
            (self.songs[2].pk, 1), (self.songs[0].pk, 2), (self.songs[1].pk, 3),
        ])
        positions = [row.position for row in rows]
        self.assertEqual(positions, list(range(1, len(rows) + 1)))
        self.assertEqual(len(positions), len(set(positions)))

    def test_invalid_reorder_action_and_song_not_in_playlist_are_safe(self):
        wrong_action = self.api_post(
            self.login(self.member), self.action_url(), {'action': 'share'}
        )
        not_in_list = self.api_post(
            self.login(self.member), self.action_url(self.playlist, self.songs[1]), {'action': 'move_up'}
        )
        self.assertEqual(wrong_action.status_code, 400)
        self.assertEqual(not_in_list.status_code, 404)
        self.assertFalse(PlaylistSong.objects.exists())

    def test_move_at_playlist_edge_is_safe_and_preserves_positions(self):
        for index, song in enumerate(self.songs[:2], start=1):
            PlaylistSong.objects.create(playlist=self.playlist, song=song, position=index)
        response = self.api_post(
            self.login(self.member), self.action_url(self.playlist, self.songs[0]), {'action': 'move_up'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('already at the edge', response.json()['message'])
        self.assertEqual(list(self.playlist.playlist_songs.order_by('position').values_list('song_id', 'position')),
                         [(self.songs[0].pk, 1), (self.songs[1].pk, 2)])

    def test_regular_form_add_remove_fallback_redirects_and_mutates_correctly(self):
        client = self.login(self.member)
        add = client.post(reverse('playlist_add_song', args=[self.songs[0].pk]), {
            'playlist_id': self.playlist.pk,
        })
        self.assertRedirects(add, reverse('song_detail', args=[self.songs[0].pk]))
        remove = client.post(self.action_url(), {'action': 'remove'})
        self.assertRedirects(remove, reverse('playlist_detail', args=[self.playlist.pk]))
        self.assertFalse(PlaylistSong.objects.exists())
        self.assertTrue(Song.objects.filter(pk=self.songs[0].pk).exists())

    def test_csrf_is_enforced_on_add_and_song_actions(self):
        client = self.login(self.member, enforce_csrf_checks=True)
        client.get(reverse('song_detail', args=[self.songs[0].pk]))
        token = client.cookies['csrftoken'].value
        add_url = reverse('playlist_add_song', args=[self.songs[0].pk])
        rejected = client.post(add_url, {'playlist_id': self.playlist.pk})
        self.assertEqual(rejected.status_code, 403)
        accepted = client.post(add_url, {'playlist_id': self.playlist.pk}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted.status_code, 302)

        action_url = self.action_url()
        rejected_remove = client.post(action_url, {'action': 'remove'})
        self.assertEqual(rejected_remove.status_code, 403)
        accepted_remove = client.post(action_url, {'action': 'remove'}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(accepted_remove.status_code, 302)
        self.assertTrue(Song.objects.filter(pk=self.songs[0].pk).exists())
