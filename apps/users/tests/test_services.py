from django.test import TestCase

from apps.users.models import User
from apps.users.services import register_user, update_profile


class TestRegisterUser(TestCase):
    def test_creates_user_with_email_and_password(self):
        user = register_user('alice@example.com', 'securepass123')

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.email, 'alice@example.com')
        self.assertTrue(user.check_password('securepass123'))

    def test_user_is_active_by_default(self):
        user = register_user('bob@example.com', 'securepass123')

        self.assertTrue(user.is_active)

    def test_username_set_to_email(self):
        user = register_user('carol@example.com', 'securepass123')

        self.assertEqual(user.username, 'carol@example.com')


class TestUpdateProfile(TestCase):
    def setUp(self):
        self.user = register_user('dave@example.com', 'securepass123')

    def test_updates_first_and_last_name(self):
        updated = update_profile(self.user, 'Dave', 'Smith')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Dave')
        self.assertEqual(self.user.last_name, 'Smith')
        self.assertEqual(updated.first_name, 'Dave')
        self.assertEqual(updated.last_name, 'Smith')

    def test_accepts_empty_strings(self):
        update_profile(self.user, '', '')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
