from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.users.services import register_user


class TestRegisterView(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('users:register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_valid_registration_creates_user(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'email': 'newuser@example.com',
                'password': 'StrongPass1!',
                'confirm_password': 'StrongPass1!',
            },
        )

        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_valid_registration_logs_user_in_and_redirects(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'email': 'newuser@example.com',
                'password': 'StrongPass1!',
                'confirm_password': 'StrongPass1!',
            },
        )

        self.assertRedirects(response, reverse('products:list'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_duplicate_email_shows_error(self):
        register_user('existing@example.com', 'pass123')

        response = self.client.post(
            reverse('users:register'),
            {
                'email': 'existing@example.com',
                'password': 'StrongPass1!',
                'confirm_password': 'StrongPass1!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'], 'email', 'An account with this email already exists.'
        )

    def test_password_mismatch_shows_error(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'email': 'user@example.com',
                'password': 'StrongPass1!',
                'confirm_password': 'DifferentPass1!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, 'Passwords do not match.')

    def test_authenticated_user_redirected_away(self):
        register_user('auth@example.com', 'pass123')
        self.client.login(username='auth@example.com', password='pass123')

        response = self.client.get(reverse('users:register'))

        self.assertRedirects(response, reverse('products:list'))


class TestLoginView(TestCase):
    def setUp(self):
        self.user = register_user('login@example.com', 'pass123')

    def test_get_returns_200(self):
        response = self.client.get(reverse('users:login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_valid_credentials_log_user_in_and_redirect(self):
        response = self.client.post(
            reverse('users:login'),
            {'email': 'login@example.com', 'password': 'pass123'},
        )

        self.assertRedirects(response, reverse('products:list'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_valid_credentials_with_next_redirect_to_next(self):
        next_url = reverse('users:profile')
        response = self.client.post(
            reverse('users:login') + f'?next={next_url}',
            {'email': 'login@example.com', 'password': 'pass123', 'next': next_url},
        )

        self.assertRedirects(response, next_url)

    def test_invalid_password_shows_error(self):
        response = self.client.post(
            reverse('users:login'),
            {'email': 'login@example.com', 'password': 'wrongpass'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'], None, 'Invalid email or password.'
        )

    def test_nonexistent_email_shows_error(self):
        response = self.client.post(
            reverse('users:login'),
            {'email': 'nobody@example.com', 'password': 'pass123'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'], None, 'Invalid email or password.'
        )

    def test_authenticated_user_redirected_away(self):
        self.client.login(username='login@example.com', password='pass123')

        response = self.client.get(reverse('users:login'))

        self.assertRedirects(response, reverse('products:list'))


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = register_user('logout@example.com', 'pass123')

    def test_post_logs_out_and_redirects(self):
        self.client.login(username='logout@example.com', password='pass123')

        response = self.client.post(reverse('users:logout'))

        self.assertRedirects(response, reverse('products:list'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_get_not_allowed(self):
        self.client.login(username='logout@example.com', password='pass123')

        response = self.client.get(reverse('users:logout'))

        self.assertEqual(response.status_code, 405)


class TestProfileView(TestCase):
    def setUp(self):
        self.user = register_user('profile@example.com', 'pass123')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('users:profile'))

        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('users:profile'),
        )

    def test_authenticated_returns_200(self):
        self.client.login(username='profile@example.com', password='pass123')

        response = self.client.get(reverse('users:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_shows_email(self):
        self.client.login(username='profile@example.com', password='pass123')

        response = self.client.get(reverse('users:profile'))

        self.assertContains(response, 'profile@example.com')

    def test_post_updates_name_and_redirects(self):
        self.client.login(username='profile@example.com', password='pass123')

        response = self.client.post(
            reverse('users:profile'),
            {'first_name': 'Jane', 'last_name': 'Doe'},
        )

        self.assertRedirects(response, reverse('users:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, 'Doe')
