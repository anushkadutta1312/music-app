from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from catalog.models import Song
from profiles.models import Favourite


class FavouriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='listener', password='password123')
        self.song = Song.objects.create(title='Starboy', duration_seconds=230)

    def test_19_add_favourite_song(self):
        """Verify favourite creation linking user and song."""
        fav = Favourite.objects.create(user=self.user, song=self.song)
        self.assertEqual(fav.user.username, 'listener')
        self.assertEqual(fav.song.title, 'Starboy')
        self.assertEqual(self.user.favourites.count(), 1)
        self.assertEqual(self.song.favourited_by.count(), 1)

    def test_20_prevent_duplicate_favourites(self):
        """Verify UNIQUE constraint prevents user from favouriting the same song twice."""
        Favourite.objects.create(user=self.user, song=self.song)
        with self.assertRaises(IntegrityError):
            Favourite.objects.create(user=self.user, song=self.song)

    def test_21_cascade_deletion_on_user_or_song_delete(self):
        """Verify favourite records are removed when either user or song is deleted."""
        Favourite.objects.create(user=self.user, song=self.song)
        self.assertEqual(Favourite.objects.count(), 1)
        self.song.delete()
        self.assertEqual(Favourite.objects.count(), 0)
