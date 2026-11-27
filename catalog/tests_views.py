"""Permission and destructive-action tests for catalogue management views."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


class CatalogueAdminPermissionTests(TestCase):
    """Every catalogue administration route is restricted to ADMIN users."""

    def setUp(self):
        # force_login() is used below, so fixture passwords are deliberately not
        # hashed and no test depends on a credential-authentication flow.
        self.admin = User.objects.create(username="catalogue_admin", is_staff=False)
        UserProfile.objects.create(
            user=self.admin,
            display_name="Catalogue Admin",
            role="ADMIN",
        )
        self.member = User.objects.create(username="catalogue_member")
        UserProfile.objects.create(
            user=self.member,
            display_name="Catalogue Member",
            role="MEMBER",
        )

        self.song = Song.objects.create(
            title="Permission Test Song",
            duration_seconds=180,
        )
        self.artist = Artist.objects.create(name="Permission Test Artist")
        self.genre = Genre.objects.create(name="Permission Test Genre")
        SongArtist.objects.create(song=self.song, artist=self.artist)
        SongGenre.objects.create(song=self.song, genre=self.genre)

        self.management_urls = {
            "catalogue dashboard": reverse("catalogue_manage"),
            "song listing": reverse("song_manage_list"),
            "song creation": reverse("song_create"),
            "song editing": reverse("song_update", args=[self.song.pk]),
            "song deletion": reverse("song_delete", args=[self.song.pk]),
            "artist listing": reverse("artist_manage_list"),
            "artist creation": reverse("artist_create"),
            "artist editing": reverse("artist_update", args=[self.artist.pk]),
            "artist deletion": reverse("artist_delete", args=[self.artist.pk]),
            "genre listing": reverse("genre_manage_list"),
            "genre creation": reverse("genre_create"),
            "genre editing": reverse("genre_update", args=[self.genre.pk]),
            "genre deletion": reverse("genre_delete", args=[self.genre.pk]),
        }
        self.mutation_urls = {
            name: url
            for name, url in self.management_urls.items()
            if name.endswith(("creation", "editing", "deletion"))
        }
        self.delete_urls = {
            "artist": self.management_urls["artist deletion"],
            "genre": self.management_urls["genre deletion"],
            "song": self.management_urls["song deletion"],
        }

    def test_anonymous_visitors_are_redirected_from_all_management_routes(self):
        client = Client()

        for label, url in self.management_urls.items():
            with self.subTest(endpoint=label):
                response = client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)

    def test_members_receive_403_from_all_management_routes(self):
        client = Client()
        client.force_login(self.member)

        for label, url in self.management_urls.items():
            with self.subTest(endpoint=label):
                response = client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_admins_can_open_all_management_pages(self):
        client = Client()
        client.force_login(self.admin)

        for label, url in self.management_urls.items():
            with self.subTest(endpoint=label):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_anonymous_and_member_posts_cannot_mutate_admin_endpoints(self):
        clients = {
            "anonymous": (Client(), 302),
            "member": (Client(), 403),
        }
        clients["member"][0].force_login(self.member)

        for state, (client, expected_status) in clients.items():
            for label, url in self.mutation_urls.items():
                with self.subTest(user_state=state, endpoint=label):
                    response = client.post(url, {"name": "Unauthorized Change"})
                    self.assertEqual(response.status_code, expected_status)

        self.assertEqual(Song.objects.count(), 1)
        self.assertEqual(Artist.objects.count(), 1)
        self.assertEqual(Genre.objects.count(), 1)
        self.song.refresh_from_db()
        self.artist.refresh_from_db()
        self.genre.refresh_from_db()
        self.assertEqual(self.song.title, "Permission Test Song")
        self.assertEqual(self.artist.name, "Permission Test Artist")
        self.assertEqual(self.genre.name, "Permission Test Genre")

    def test_get_and_non_post_requests_never_delete_records(self):
        client = Client()
        client.force_login(self.admin)

        for label, url in self.delete_urls.items():
            with self.subTest(method="GET", item=label):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(self._item_exists(label))

            with self.subTest(method="PUT", item=label):
                client.put(url, data="", content_type="application/octet-stream")
                self.assertTrue(self._item_exists(label))

    def test_invalid_csrf_posts_do_not_delete_records(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)

        for label, url in self.delete_urls.items():
            with self.subTest(item=label):
                confirmation = client.get(url)
                self.assertEqual(confirmation.status_code, 200)
                response = client.post(url, HTTP_X_CSRFTOKEN="invalid-token")
                self.assertEqual(response.status_code, 403)
                self.assertTrue(self._item_exists(label))

    def test_valid_csrf_protected_posts_perform_deletions(self):
        for label, url in self.delete_urls.items():
            with self.subTest(item=label):
                client = Client(enforce_csrf_checks=True)
                client.force_login(self.admin)

                confirmation = client.get(url)
                self.assertEqual(confirmation.status_code, 200)
                csrf_cookie = client.cookies.get("csrftoken")
                self.assertIsNotNone(csrf_cookie)

                response = client.post(
                    url,
                    HTTP_X_CSRFTOKEN=csrf_cookie.value,
                )
                self.assertEqual(response.status_code, 302)
                self.assertFalse(self._item_exists(label))
                if label in {"artist", "genre"}:
                    self.assertTrue(Song.objects.filter(pk=self.song.pk).exists())

        # Deleting an artist or genre leaves the song intact; deleting the song
        # then clears its remaining junction rows.
        self.assertFalse(Song.objects.filter(pk=self.song.pk).exists())
        self.assertEqual(SongArtist.objects.count(), 0)
        self.assertEqual(SongGenre.objects.count(), 0)

    def _item_exists(self, item_type):
        model_and_pk = {
            "song": (Song, self.song.pk),
            "artist": (Artist, self.artist.pk),
            "genre": (Genre, self.genre.pk),
        }
        model, pk = model_and_pk[item_type]
        return model.objects.filter(pk=pk).exists()
