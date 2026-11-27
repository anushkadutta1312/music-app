"""Integration tests for authenticated catalogue discovery and search."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


class CatalogueBrowseTests(TestCase):
    def setUp(self):
        self.member = User.objects.create(username="browse_member")
        UserProfile.objects.create(user=self.member, display_name="Browse Member", role="MEMBER")
        self.admin = User.objects.create(username="browse_admin")
        UserProfile.objects.create(user=self.admin, display_name="Browse Admin", role="ADMIN")

        self.aurora = Artist.objects.create(name="Aurora Waves")
        self.pulse = Artist.objects.create(name="Pulse Quartet")
        self.twin_one = Artist.objects.create(name="Twin Signal One")
        self.twin_two = Artist.objects.create(name="Twin Signal Two")
        self.dream_pop = Genre.objects.create(name="Dream Pop")
        self.jazz = Genre.objects.create(name="Late Night Jazz")

        self.moonlight = self.create_song(
            "Moonlight Signal", "Night Archive", [self.aurora], [self.dream_pop]
        )
        self.river = self.create_song(
            "Quiet River", "Night Archive Vol 2", [self.pulse], [self.jazz]
        )
        self.twin = self.create_song(
            "Twin Signal Anthem",
            "Twin Signal Sessions",
            [self.twin_one, self.twin_two],
            [self.dream_pop, self.jazz],
        )

    def create_song(self, title, album, artists, genres):
        song = Song.objects.create(title=title, album_name=album, duration_seconds=200)
        SongArtist.objects.bulk_create(
            [SongArtist(song=song, artist=artist) for artist in artists]
        )
        SongGenre.objects.bulk_create(
            [SongGenre(song=song, genre=genre) for genre in genres]
        )
        return song

    def login_as(self, user):
        client = Client()
        client.force_login(user)
        return client

    def result_ids(self, response):
        return [song.pk for song in response.context["songs"]]

    def test_member_and_admin_can_browse_but_anonymous_is_redirected(self):
        url = reverse("catalogue_browse")
        response = Client().get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

        for role_user in (self.member, self.admin):
            with self.subTest(role=role_user.profile.role):
                response = self.login_as(role_user).get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["total_results"], 3)

    def test_song_details_show_associated_artist_and_genre_names(self):
        response = self.login_as(self.member).get(
            reverse("song_detail", args=[self.moonlight.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Moonlight Signal")
        self.assertContains(response, self.aurora.name)
        self.assertContains(response, self.dream_pop.name)

    def test_search_matches_title_artist_and_album_case_insensitively(self):
        client = self.login_as(self.member)

        title_response = client.get(reverse("catalogue_browse"), {"q": "mOoNlIgHt"})
        self.assertSetEqual(set(self.result_ids(title_response)), {self.moonlight.pk})

        artist_response = client.get(reverse("catalogue_browse"), {"q": "AURORA WAVES"})
        self.assertSetEqual(set(self.result_ids(artist_response)), {self.moonlight.pk})

        album_response = client.get(reverse("catalogue_browse"), {"q": "ARCHIVE"})
        self.assertSetEqual(
            set(self.result_ids(album_response)),
            {self.moonlight.pk, self.river.pk},
        )

    def test_search_combines_with_genre_and_artist_filters(self):
        client = self.login_as(self.member)

        genre_response = client.get(
            reverse("catalogue_browse"),
            {"q": "Moonlight", "genre": self.dream_pop.pk},
        )
        self.assertSetEqual(set(self.result_ids(genre_response)), {self.moonlight.pk})

        no_genre_match = client.get(
            reverse("catalogue_browse"),
            {"q": "Moonlight", "genre": self.jazz.pk},
        )
        self.assertEqual(no_genre_match.context["total_results"], 0)

        artist_response = client.get(
            reverse("catalogue_browse"),
            {"q": "Moonlight", "artist": self.aurora.pk},
        )
        self.assertSetEqual(set(self.result_ids(artist_response)), {self.moonlight.pk})

        no_artist_match = client.get(
            reverse("catalogue_browse"),
            {"q": "Moonlight", "artist": self.pulse.pk},
        )
        self.assertEqual(no_artist_match.context["total_results"], 0)

    def test_invalid_filter_values_are_handled_without_a_server_error(self):
        response = self.login_as(self.member).get(
            reverse("catalogue_browse"),
            {"genre": "not-an-id", "artist": "also-not-an-id"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_results"], 3)
        self.assertTrue(response.context["filter_form"].errors)

    def test_empty_search_shows_catalogue_and_no_result_search_is_helpful(self):
        client = self.login_as(self.member)
        url = reverse("catalogue_browse")

        empty_search = client.get(url, {"q": ""})
        self.assertEqual(empty_search.status_code, 200)
        self.assertEqual(empty_search.context["total_results"], 3)
        self.assertNotContains(empty_search, "No songs found")

        no_results = client.get(url, {"q": "no such catalogue track"})
        self.assertEqual(no_results.status_code, 200)
        self.assertEqual(no_results.context["total_results"], 0)
        self.assertContains(no_results, "No songs found")

    def test_artist_search_does_not_duplicate_a_song_with_multiple_matches(self):
        response = self.login_as(self.member).get(
            reverse("catalogue_browse"), {"q": "Twin Signal"}
        )

        self.assertEqual(response.context["total_results"], 1)
        self.assertEqual(self.result_ids(response), [self.twin.pk])

    def test_pagination_and_filter_parameters_are_preserved(self):
        page_artist = Artist.objects.create(name="Page Set Artist")
        page_genre = Genre.objects.create(name="Page Set Genre")
        page_songs = [
            self.create_song(
                f"PageSet Track {index:02}", "Pagination Album", [page_artist], [page_genre]
            )
            for index in range(14)
        ]
        client = self.login_as(self.member)
        url = reverse("catalogue_browse")
        filters = {
            "q": "PageSet",
            "genre": str(page_genre.pk),
            "artist": str(page_artist.pk),
        }

        first_page = client.get(url, filters)
        self.assertEqual(first_page.context["page_obj"].number, 1)
        self.assertEqual(len(first_page.context["songs"]), 12)
        self.assertTrue(first_page.context["page_obj"].has_next())

        second_page = client.get(url, {**filters, "page": "2"})
        self.assertEqual(second_page.context["page_obj"].number, 2)
        self.assertEqual(len(second_page.context["songs"]), 2)
        self.assertEqual(second_page.context["total_results"], 14)
        self.assertEqual(
            set(self.result_ids(first_page)) | set(self.result_ids(second_page)),
            {song.pk for song in page_songs},
        )
        self.assertEqual(
            second_page.context["pagination_params"],
            f"&q=PageSet&genre={page_genre.pk}&artist={page_artist.pk}",
        )
        self.assertContains(
            second_page,
            f"?page=1&amp;q=PageSet&amp;genre={page_genre.pk}&amp;artist={page_artist.pk}",
        )

    def test_invalid_page_value_falls_back_safely(self):
        response = self.login_as(self.member).get(
            reverse("catalogue_browse"), {"page": "not-a-page"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)
