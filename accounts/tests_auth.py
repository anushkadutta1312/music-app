from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from accounts.models import UserProfile
from catalog.models import Song, Artist, Genre
from playlists.models import Playlist


class AuthenticationAndPermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create sample admin
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin_test@musicapp.local',
            password='AdminTest2026!',
            is_staff=True
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            display_name='Admin Tester',
            role='ADMIN'
        )

        # Create sample member
        self.member_user = User.objects.create_user(
            username='member_test',
            email='member_test@musicapp.local',
            password='MemberTest2026!'
        )
        self.member_profile = UserProfile.objects.create(
            user=self.member_user,
            display_name='Member Tester',
            role='MEMBER'
        )

        # Create another member
        self.other_user = User.objects.create_user(
            username='other_member',
            email='other@musicapp.local',
            password='MemberTest2026!'
        )
        self.other_profile = UserProfile.objects.create(
            user=self.other_user,
            display_name='Other Member',
            role='MEMBER'
        )

    # 1. A new user can register successfully
    def test_01_user_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'new_fan',
            'email': 'newfan@example.com',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_fan').exists())

    # 2. A new user automatically receives the MEMBER role
    def test_02_new_user_gets_member_role(self):
        self.client.post(reverse('register'), {
            'username': 'auto_member',
            'email': 'automember@example.com',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!'
        })
        user = User.objects.get(username='auto_member')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'MEMBER')
        self.assertFalse(user.is_staff)

    # 3. Duplicate usernames are rejected
    def test_03_duplicate_username_rejected(self):
        response = self.client.post(reverse('register'), {
            'username': 'member_test',  # already exists
            'email': 'unique_email@example.com',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'A user with that username already exists.')

    # 4. Invalid passwords (short / mismatch) are rejected
    def test_04_invalid_password_rejected(self):
        # Mismatched passwords
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'PasswordOne123!',
            'confirm_password': 'PasswordTwo123!'
        })
        self.assertFormError(response.context['form'], 'confirm_password', 'Passwords do not match.')

        # Short password
        response2 = self.client.post(reverse('register'), {
            'username': 'short_pwd_user',
            'email': 'short@example.com',
            'password': '123',
            'confirm_password': '123'
        })
        self.assertIn('password', response2.context['form'].errors)

    # 5. A valid user can log in
    def test_05_valid_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'member_test',
            'password': 'MemberTest2026!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    # 6. Invalid login credentials are rejected
    def test_06_invalid_login_rejected(self):
        response = self.client.post(reverse('login'), {
            'username': 'member_test',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        # Verify user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # 7. A logged-in user can log out
    def test_07_logged_in_user_logout(self):
        self.client.login(username='member_test', password='MemberTest2026!')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout_rejects_get_without_ending_session(self):
        self.client.login(username='member_test', password='MemberTest2026!')

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)

    def test_logout_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.member_user)

        response = csrf_client.post(reverse('logout'))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(csrf_client.get(reverse('profile')).status_code, 200)

    def test_login_page_does_not_publish_demo_passwords(self):
        response = self.client.get(reverse('login'))

        self.assertNotContains(response, 'AdminDemo2026!')
        self.assertNotContains(response, 'MemberDemo2026!')

    # 8. An unauthenticated user cannot access protected pages
    def test_08_unauthenticated_user_redirected(self):
        protected_urls = [reverse('dashboard'), reverse('profile'), reverse('profile_edit'), reverse('admin_dashboard')]
        for url in protected_urls:
            response = self.client.get(url)
            # Should redirect to login with ?next=...
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)

    # 9. An administrator can access the admin dashboard
    def test_09_admin_can_access_admin_dashboard(self):
        self.client.login(username='admin_test', password='AdminTest2026!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System Administration Dashboard")

    # 10. An administrator can access catalogue-management pages
    def test_10_admin_can_access_catalogue_management(self):
        self.client.login(username='admin_test', password='AdminTest2026!')
        response = self.client.get(reverse('catalogue_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Music Catalogue Management")

    # 11. A normal member cannot access admin-only pages
    def test_11_member_cannot_access_admin_pages(self):
        self.client.login(username='member_test', password='MemberTest2026!')
        # Admin dashboard access attempt -> 403 Forbidden
        response1 = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response1.status_code, 403)

        # Catalogue management access attempt -> 403 Forbidden
        response2 = self.client.get(reverse('catalogue_manage'))
        self.assertEqual(response2.status_code, 403)

    # 12. A member cannot change their role through profile updates
    def test_12_member_cannot_escalate_role(self):
        self.client.login(username='member_test', password='MemberTest2026!')
        # Attempt to inject 'role': 'ADMIN' in profile edit POST
        response = self.client.post(reverse('profile_edit'), {
            'display_name': 'Hacker Member',
            'bio': 'Trying to become admin',
            'role': 'ADMIN'  # Form must ignore this!
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.role, 'MEMBER')  # Remained MEMBER
        self.assertEqual(self.member_profile.display_name, 'Hacker Member')

    # 13. A member cannot access or edit another member's profile
    def test_13_member_profile_isolation(self):
        self.client.login(username='member_test', password='MemberTest2026!')
        # User viewing their profile gets their own profile
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'].user, self.member_user)
        self.assertNotEqual(response.context['profile'].user, self.other_user)

    # 14. Authentication works for seeded users
    def test_14_authentication_for_users(self):
        user = authenticate(username='admin_test', password='AdminTest2026!')
        self.assertIsNotNone(user)
        self.assertEqual(user.profile.role, 'ADMIN')

    # 15. Database records and schema remain intact
    def test_15_schema_and_integrity_preserved(self):
        Song.objects.create(title='Test Song', duration_seconds=200)
        self.assertEqual(Song.objects.filter(title='Test Song').count(), 1)
