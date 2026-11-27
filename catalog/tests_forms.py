"""Focused validation and persistence tests for the catalogue ModelForms."""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.forms import ArtistForm, GenreForm, SongForm
from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


class SongFormValidationTests(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="Form Test Artist")
        self.genre = Genre.objects.create(name="Form Test Genre")

    def song_data(self, **overrides):
        data = {
            "title": "Form Test Song",
            "album_name": "Form Test Album",
            "duration_seconds": "210",
            "release_year": "2024",
            "cover_image_url": "",
            "external_provider": "",
            "external_track_id": "",
            "artists": [str(self.artist.pk)],
            "genres": [str(self.genre.pk)],
        }
        data.update(overrides)
        return data

    def test_valid_song_data_and_relationship_selections_are_accepted(self):
        form = SongForm(self.song_data())

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(list(form.cleaned_data["artists"]), [self.artist])
        self.assertEqual(list(form.cleaned_data["genres"]), [self.genre])

    def test_missing_song_title_is_rejected(self):
        form = SongForm(self.song_data(title=""))

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_zero_duration_is_rejected(self):
        form = SongForm(self.song_data(duration_seconds="0"))

        self.assertFalse(form.is_valid())
        self.assertIn("duration_seconds", form.errors)

    def test_release_year_before_1900_is_rejected(self):
        form = SongForm(self.song_data(release_year="1899"))

        self.assertFalse(form.is_valid())
        self.assertIn("release_year", form.errors)

    def test_invalid_artist_selection_is_rejected(self):
        form = SongForm(self.song_data(artists=["999999"]))

        self.assertFalse(form.is_valid())
        self.assertIn("artists", form.errors)

    def test_invalid_genre_selection_is_rejected(self):
        form = SongForm(self.song_data(genres=["999999"]))

        self.assertFalse(form.is_valid())
        self.assertIn("genres", form.errors)

    def test_duplicate_artist_and_genre_selections_do_not_duplicate_links(self):
        form = SongForm(
            self.song_data(
                artists=[str(self.artist.pk), str(self.artist.pk)],
                genres=[str(self.genre.pk), str(self.genre.pk)],
            )
        )

        self.assertTrue(form.is_valid(), form.errors)
        song = form.save()

        self.assertEqual(SongArtist.objects.filter(song=song, artist=self.artist).count(), 1)
        self.assertEqual(SongGenre.objects.filter(song=song, genre=self.genre).count(), 1)


class ArtistFormValidationTests(TestCase):
    def test_valid_artist_data_is_accepted(self):
        form = ArtistForm({"name": "Valid Artist", "biography": "A short biography."})

        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_artist_name_is_rejected(self):
        form = ArtistForm({"name": "", "biography": "A short biography."})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_duplicate_artist_name_is_rejected(self):
        Artist.objects.create(name="Existing Artist")
        form = ArtistForm({"name": "Existing Artist", "biography": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class GenreFormValidationTests(TestCase):
    def test_valid_genre_data_is_accepted(self):
        form = GenreForm({"name": "Valid Genre", "description": "A short description."})

        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_genre_name_is_rejected(self):
        form = GenreForm({"name": "", "description": "A short description."})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_duplicate_genre_name_is_rejected(self):
        Genre.objects.create(name="Existing Genre")
        form = GenreForm({"name": "Existing Genre", "description": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class SongRelationshipViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(username="form_admin")
        UserProfile.objects.create(
            user=self.admin,
            display_name="Form Test Admin",
            role="ADMIN",
        )
        self.client = Client()
        self.client.force_login(self.admin)

        self.artist_one = Artist.objects.create(name="Artist One")
        self.artist_two = Artist.objects.create(name="Artist Two")
        self.genre_one = Genre.objects.create(name="Genre One")
        self.genre_two = Genre.objects.create(name="Genre Two")

    def song_data(self, title, artists, genres):
        return {
            "title": title,
            "album_name": "Relationship Album",
            "duration_seconds": "200",
            "release_year": "2023",
            "cover_image_url": "",
            "external_provider": "",
            "external_track_id": "",
            "artists": [str(artist.pk) for artist in artists],
            "genres": [str(genre.pk) for genre in genres],
        }

    def test_song_creation_view_saves_all_selected_junction_rows(self):
        response = self.client.post(
            reverse("song_create"),
            self.song_data(
                "Created Through View",
                [self.artist_one, self.artist_two],
                [self.genre_one, self.genre_two],
            ),
        )

        self.assertEqual(response.status_code, 302)
        song = Song.objects.get(title="Created Through View")
        self.assertSetEqual(
            set(SongArtist.objects.filter(song=song).values_list("artist_id", flat=True)),
            {self.artist_one.pk, self.artist_two.pk},
        )
        self.assertSetEqual(
            set(SongGenre.objects.filter(song=song).values_list("genre_id", flat=True)),
            {self.genre_one.pk, self.genre_two.pk},
        )

    def test_song_edit_updates_both_junction_sets_without_duplicates(self):
        song = Song.objects.create(title="Before Edit", duration_seconds=200)
        SongArtist.objects.create(song=song, artist=self.artist_one)
        SongGenre.objects.create(song=song, genre=self.genre_one)

        response = self.client.post(
            reverse("song_update", args=[song.pk]),
            self.song_data(
                "After Edit",
                [self.artist_two, self.artist_two],
                [self.genre_two, self.genre_two],
            ),
        )

        self.assertEqual(response.status_code, 302)
        song.refresh_from_db()
        self.assertEqual(song.title, "After Edit")
        self.assertSetEqual(
            set(SongArtist.objects.filter(song=song).values_list("artist_id", flat=True)),
            {self.artist_two.pk},
        )
        self.assertSetEqual(
            set(SongGenre.objects.filter(song=song).values_list("genre_id", flat=True)),
            {self.genre_two.pk},
        )
        self.assertEqual(SongArtist.objects.filter(song=song).count(), 1)
        self.assertEqual(SongGenre.objects.filter(song=song).count(), 1)

    def test_relationship_database_error_rolls_back_song_and_old_relationships(self):
        song = Song.objects.create(title="Stable Before Failure", duration_seconds=200)
        SongArtist.objects.create(song=song, artist=self.artist_one)
        SongGenre.objects.create(song=song, genre=self.genre_one)
        form = SongForm(
            self.song_data("Should Roll Back", [self.artist_two], [self.genre_two]),
            instance=song,
        )
        self.assertTrue(form.is_valid(), form.errors)

        with patch(
            "catalog.forms.SongGenre.objects.create",
            side_effect=IntegrityError("simulated junction insert failure"),
        ):
            with self.assertRaises(IntegrityError):
                form.save()

        song.refresh_from_db()
        self.assertEqual(song.title, "Stable Before Failure")
        self.assertSetEqual(
            set(SongArtist.objects.filter(song=song).values_list("artist_id", flat=True)),
            {self.artist_one.pk},
        )
        self.assertSetEqual(
            set(SongGenre.objects.filter(song=song).values_list("genre_id", flat=True)),
            {self.genre_one.pk},
        )

    def test_relationship_database_error_does_not_leave_a_new_song(self):
        form = SongForm(
            self.song_data("Must Not Persist", [self.artist_one], [self.genre_one])
        )
        self.assertTrue(form.is_valid(), form.errors)

        with patch(
            "catalog.forms.SongArtist.objects.create",
            side_effect=IntegrityError("simulated junction insert failure"),
        ):
            with self.assertRaises(IntegrityError):
                form.save()

        self.assertFalse(Song.objects.filter(title="Must Not Persist").exists())
        self.assertEqual(SongArtist.objects.count(), 0)
        self.assertEqual(SongGenre.objects.count(), 0)
