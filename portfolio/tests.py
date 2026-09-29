import os
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=TEST_STORAGES)
class PublicPageTests(TestCase):
    def test_public_pages_render(self):
        for name in ("home", "mikrotik_generator", "algorithm_studio", "owner_login"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_pages_have_one_main_landmark(self):
        for name in ("home", "mikrotik_generator", "algorithm_studio"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertEqual(html.count("<main"), 1, name)
            self.assertIn('id="mainContent"', html)

    def test_private_navigation_is_hidden_from_visitors(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertNotIn("Search OLT by location", html)
        self.assertIn("Admin View", html)


@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=TEST_STORAGES)
class OwnerAccessTests(TestCase):
    @patch.dict(os.environ, {"OWNER_ACCESS_KEY": "correct-secret"})
    def test_correct_key_unlocks_private_navigation(self):
        response = self.client.post(reverse("owner_login"), {"access_key": "correct-secret"})
        self.assertRedirects(response, reverse("home"))
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("Search OLT by location", html)
        self.assertIn("MANOR-IT", html)

    @patch.dict(os.environ, {"OWNER_ACCESS_KEY": "correct-secret"})
    def test_invalid_key_is_rejected(self):
        response = self.client.post(reverse("owner_login"), {"access_key": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid owner access key")

    @patch.dict(os.environ, {"OWNER_ACCESS_KEY": "correct-secret"})
    def test_login_is_rate_limited(self):
        for _ in range(5):
            self.client.post(reverse("owner_login"), {"access_key": "wrong"})
        response = self.client.post(reverse("owner_login"), {"access_key": "wrong"})
        self.assertEqual(response.status_code, 429)

    @patch.dict(os.environ, {"OWNER_ACCESS_KEY": "correct-secret"})
    def test_logout_requires_post(self):
        self.client.post(reverse("owner_login"), {"access_key": "correct-secret"})
        self.assertEqual(self.client.get(reverse("owner_logout")).status_code, 405)
        response = self.client.post(reverse("owner_logout"))
        self.assertRedirects(response, reverse("home"))

# Create your tests here.
