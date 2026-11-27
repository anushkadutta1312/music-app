from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from accounts.models import UserProfile
from catalog.models import Genre, Artist, Song, SongArtist, SongGenre
from playlists.models import Playlist, PlaylistSong
from profiles.models import Favourite


class SeedDataCommandTest(TestCase):
    def test_seed_data_execution_and_idempotency(self):
        """
        Verify that running seed_data populates records as expected,
        and running it a second time does not duplicate any records.
        """
        # --- First Execution ---
        call_command('seed_data')

        # Verify target counts
        self.assertEqual(User.objects.count(), 12)
        self.assertEqual(UserProfile.objects.count(), 12)
        self.assertEqual(Genre.objects.count(), 10)
        self.assertEqual(Artist.objects.count(), 20)
        self.assertEqual(Song.objects.count(), 55)  # 55 curated tracks in catalog
        self.assertGreaterEqual(SongArtist.objects.count(), 55)
        self.assertGreaterEqual(SongGenre.objects.count(), 60)
        self.assertGreaterEqual(Favourite.objects.count(), 40)
        self.assertEqual(Playlist.objects.count(), 15)
        self.assertGreaterEqual(PlaylistSong.objects.count(), 60)

        # Snapshot counts after 1st execution
        user_cnt_1 = User.objects.count()
        genre_cnt_1 = Genre.objects.count()
        artist_cnt_1 = Artist.objects.count()
        song_cnt_1 = Song.objects.count()
        sa_cnt_1 = SongArtist.objects.count()
        sg_cnt_1 = SongGenre.objects.count()
        fav_cnt_1 = Favourite.objects.count()
        pl_cnt_1 = Playlist.objects.count()
        pls_cnt_1 = PlaylistSong.objects.count()

        # --- Second Execution (Idempotency Check) ---
        call_command('seed_data')

        # Verify no duplicate records were created
        self.assertEqual(User.objects.count(), user_cnt_1)
        self.assertEqual(Genre.objects.count(), genre_cnt_1)
        self.assertEqual(Artist.objects.count(), artist_cnt_1)
        self.assertEqual(Song.objects.count(), song_cnt_1)
        self.assertEqual(SongArtist.objects.count(), sa_cnt_1)
        self.assertEqual(SongGenre.objects.count(), sg_cnt_1)
        self.assertEqual(Favourite.objects.count(), fav_cnt_1)
        self.assertEqual(Playlist.objects.count(), pl_cnt_1)
        self.assertEqual(PlaylistSong.objects.count(), pls_cnt_1)

    def test_demo_accounts_authentication(self):
        """Verify that admin and member demo accounts authenticate cleanly."""
        call_command('seed_data')

        # Test Admin credentials
        admin_user = authenticate(username='admin_demo', password='AdminDemo2026!')
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.profile.role, 'ADMIN')

        # Test Member credentials
        member_user = authenticate(username='alex_rhythm', password='MemberDemo2026!')
        self.assertIsNotNone(member_user)
        self.assertFalse(member_user.is_staff)
        self.assertEqual(member_user.profile.role, 'MEMBER')

    def test_unpopulated_user_for_left_join(self):
        """Verify kevin_newbie has 0 playlists so LEFT JOIN queries find unassociated rows."""
        call_command('seed_data')
        kevin = User.objects.get(username='kevin_newbie')
        self.assertEqual(kevin.playlists.count(), 0)
