from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounts.models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='musicfan',
            email='fan@example.com',
            password='secretpassword123'
        )

    def test_01_user_profile_creation(self):
        """Verify user profile creation with default role."""
        profile = UserProfile.objects.create(
            user=self.user,
            display_name='Music Fanatic',
            bio='Lover of all genres',
            role='MEMBER'
        )
        self.assertEqual(profile.user.username, 'musicfan')
        self.assertEqual(profile.role, 'MEMBER')
        self.assertEqual(str(profile), 'Music Fanatic (MEMBER)')

    def test_02_prevent_multiple_profiles_for_same_user(self):
        """Verify OneToOne constraint rejects second profile for same user."""
        UserProfile.objects.create(user=self.user, display_name='Profile 1')
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user, display_name='Profile 2')

    def test_03_cascade_deletion_on_user_delete(self):
        """Verify profile is deleted when parent user is deleted."""
        UserProfile.objects.create(user=self.user, display_name='To Delete')
        self.assertEqual(UserProfile.objects.count(), 1)
        self.user.delete()
        self.assertEqual(UserProfile.objects.count(), 0)
