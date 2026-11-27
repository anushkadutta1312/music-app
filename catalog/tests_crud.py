"""End-to-end admin catalogue CRUD and relationship behavior tests."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


class CatalogueCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(username="crud_admin")
        UserProfile.objects.create(user=self.admin, display_name="CRUD Admin", role="ADMIN")
        self.client = Client()
        self.client.force_login(self.admin)

        self.artist = Artist.objects.create(name="Original CRUD Artist")
        self.other_artist = Artist.objects.create(name="Unrelated CRUD Artist")
        self.genre = Genre.objects.create(name="Original CRUD Genre")
        self.other_genre = Genre.objects.create(name="Unrelated CRUD Genre")
        self.song = Song.objects.create(
            title="Original CRUD Song",
            album_name="Original Album",
            duration_seconds=190,
        )
        SongArtist.objects.create(song=self.song, artist=self.artist)
        SongGenre.objects.create(song=self.song, genre=self.genre)

    def song_data(self, title, artist_ids=None, genre_ids=None):
        return {
            "title": title,
            "album_name": "CRUD Album",
            "duration_seconds": "210",
            "release_year": "2020",
            "cover_image_url": "",
            "external_provider": "",
            "external_track_id": "",
            "artists": [str(pk) for pk in (artist_ids or [self.artist.pk])],
            "genres": [str(pk) for pk in (genre_ids or [self.genre.pk])],
        }

    def test_song_delete_requires_confirmation_then_removes_only_song_relations(self):
        delete_url = reverse("song_delete", args=[self.song.pk])

        confirmation = self.client.get(delete_url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(Song.objects.filter(pk=self.song.pk).exists())
        self.assertContains(confirmation, "Delete")

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Song.objects.filter(pk=self.song.pk).exists())
        self.assertFalse(SongArtist.objects.filter(song_id=self.song.pk).exists())
        self.assertFalse(SongGenre.objects.filter(song_id=self.song.pk).exists())
        self.assertTrue(Artist.objects.filter(pk=self.artist.pk).exists())
        self.assertTrue(Genre.objects.filter(pk=self.genre.pk).exists())

    def test_artist_create_edit_and_delete_preserves_related_songs(self):
        create_response = self.client.post(
            reverse("artist_create"),
            {"name": "Temporary CRUD Artist", "biography": "Created in test."},
        )
        self.assertEqual(create_response.status_code, 302)
        artist = Artist.objects.get(name="Temporary CRUD Artist")

        edit_response = self.client.post(
            reverse("artist_update", args=[artist.pk]),
            {"name": "Edited CRUD Artist", "biography": "Edited in test."},
        )
        self.assertEqual(edit_response.status_code, 302)
        artist.refresh_from_db()
        self.assertEqual(artist.name, "Edited CRUD Artist")

        # Link this artist to a song, then verify deleting it removes only the
        # junction row and leaves both songs and other artist links in place.
        SongArtist.objects.create(song=self.song, artist=artist)
        confirmation = self.client.get(reverse("artist_delete", args=[artist.pk]))
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(Artist.objects.filter(pk=artist.pk).exists())

        delete_response = self.client.post(reverse("artist_delete", args=[artist.pk]))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Artist.objects.filter(pk=artist.pk).exists())
        self.assertTrue(Song.objects.filter(pk=self.song.pk).exists())
        self.assertTrue(
            SongArtist.objects.filter(song=self.song, artist=self.artist).exists()
        )
        self.assertFalse(SongArtist.objects.filter(song=self.song, artist_id=artist.pk).exists())

    def test_genre_create_edit_and_delete_preserves_related_songs(self):
        create_response = self.client.post(
            reverse("genre_create"),
            {"name": "Temporary CRUD Genre", "description": "Created in test."},
        )
        self.assertEqual(create_response.status_code, 302)
        genre = Genre.objects.get(name="Temporary CRUD Genre")

        edit_response = self.client.post(
            reverse("genre_update", args=[genre.pk]),
            {"name": "Edited CRUD Genre", "description": "Edited in test."},
        )
        self.assertEqual(edit_response.status_code, 302)
        genre.refresh_from_db()
        self.assertEqual(genre.name, "Edited CRUD Genre")

        SongGenre.objects.create(song=self.song, genre=genre)
        confirmation = self.client.get(reverse("genre_delete", args=[genre.pk]))
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(Genre.objects.filter(pk=genre.pk).exists())

        delete_response = self.client.post(reverse("genre_delete", args=[genre.pk]))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Genre.objects.filter(pk=genre.pk).exists())
        self.assertTrue(Song.objects.filter(pk=self.song.pk).exists())
        self.assertTrue(SongGenre.objects.filter(song=self.song, genre=self.genre).exists())
        self.assertFalse(SongGenre.objects.filter(song=self.song, genre_id=genre.pk).exists())

    def test_invalid_song_create_and_edit_do_not_partially_change_records(self):
        original_artist_ids = set(
            SongArtist.objects.filter(song=self.song).values_list("artist_id", flat=True)
        )
        original_genre_ids = set(
            SongGenre.objects.filter(song=self.song).values_list("genre_id", flat=True)
        )

        create_response = self.client.post(
            reverse("song_create"),
            self.song_data("", [self.other_artist.pk], [self.other_genre.pk]),
        )
        self.assertEqual(create_response.status_code, 200)
        self.assertFalse(Song.objects.filter(title="").exists())

        edit_response = self.client.post(
            reverse("song_update", args=[self.song.pk]),
            self.song_data("", [self.other_artist.pk], [self.other_genre.pk]),
        )
        self.assertEqual(edit_response.status_code, 200)
        self.song.refresh_from_db()
        self.assertEqual(self.song.title, "Original CRUD Song")
        self.assertEqual(
            set(SongArtist.objects.filter(song=self.song).values_list("artist_id", flat=True)),
            original_artist_ids,
        )
        self.assertEqual(
            set(SongGenre.objects.filter(song=self.song).values_list("genre_id", flat=True)),
            original_genre_ids,
        )
