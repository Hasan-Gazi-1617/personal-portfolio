import os
import re
from unittest.mock import patch
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings

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

    def test_accessible_responsive_navigation_contract(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn('class="navbar-toggler nav-menu-toggle"', html)
        self.assertIn('class="nav-menu-label">Menu</span>', html)
        self.assertIn('class="skip-link"', html)
        self.assertIn("responsive-navigation", html)

    def test_manual_cache_busting_query_strings_are_removed(self):
        for name in ("home", "mikrotik_generator", "algorithm_studio"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertNotRegex(html, r'/static/[^"\']+\?v=')


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


@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=TEST_STORAGES)
class FrontendContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        static_root = Path(settings.BASE_DIR) / "static"
        cls.generator = (static_root / "js" / "mikrotik-generator.js").read_text()
        cls.algorithm = (static_root / "js" / "algorithm-studio.js").read_text()
        cls.navigation = (static_root / "js" / "responsive-navigation.js").read_text()
        cls.foundation = (static_root / "css" / "responsive-foundation.css").read_text()

    def test_all_nine_failover_scenarios_are_declared(self):
        html = self.client.get(reverse("mikrotik_generator")).content.decode()
        expected = (
            "static_static", "static_dhcp", "static_pppoe",
            "dhcp_static", "dhcp_dhcp", "dhcp_pppoe",
            "pppoe_static", "pppoe_dhcp", "pppoe_pppoe",
        )
        for scenario in expected:
            self.assertIn(f'value="{scenario}"', html)
        self.assertEqual(html.count("Scenario "), 9)

    def test_generator_safety_and_routing_guards(self):
        for required in (
            "0.0.0.0/0", "All four failover probe IPs must be unique",
            "DHCP pool cannot include the router LAN gateway",
            "PRIMARY STATIC WAN NAT", "BACKUP STATIC WAN NAT",
            "check-gateway=ping", "ROLLBACK GUIDE", "hide-sensitive",
        ):
            self.assertIn(required, self.generator)
        self.assertNotIn("Syntax ready</span>", self.generator)

    def test_routeros_versions_and_optional_dns_are_available(self):
        html = self.client.get(reverse("mikrotik_generator")).content.decode()
        self.assertIn('value="6"', html)
        self.assertIn('value="7"', html)
        self.assertIn("Secondary DNS", html)
        self.assertIn("Optional", html)

    def test_algorithm_languages_controls_and_live_regions(self):
        html = self.client.get(reverse("algorithm_studio")).content.decode()
        for language in ("C++", "Python", "Java", "Ruby"):
            self.assertIn(language, html)
        for control in ("avsReset", "avsPrev", "avsPlay", "avsNext", "avsSpeed"):
            self.assertIn(f'id="{control}"', html)
        self.assertGreaterEqual(html.count('aria-live="polite"'), 2)
        for topic in ("stack", "queue", "bfs", "dfs", "sliding"):
            self.assertRegex(self.algorithm, rf"id:'{topic}'")

    def test_single_breakpoint_foundation_and_no_overflow_hiding(self):
        for width in (991.98, 767.98, 374.98):
            self.assertIn(f"max-width: {width}px", self.foundation)
        self.assertNotIn("overflow-x: hidden", self.foundation)
        self.assertIn("--touch-target: 44px", self.foundation)

    def test_navigation_keyboard_and_focus_contract(self):
        for behavior in ("Escape", "previousFocus", "IntersectionObserver", "nav-open", "closeSubmenus"):
            self.assertIn(behavior, self.navigation)

    def test_private_infrastructure_is_not_embedded_in_public_assets(self):
        roots = (Path(settings.BASE_DIR) / "templates", Path(settings.BASE_DIR) / "static")
        combined = "\n".join(
            path.read_text(errors="ignore")
            for root in roots
            for path in root.rglob("*")
            if path.is_file()
        )
        self.assertNotIn("drive.google.com/drive/folders", combined)

    @patch.dict(os.environ, {
        "PRIVATE_NAV_LINKS_JSON": '{"webmail":"https://portal.example.test"}',
        "OLT_LOCATIONS_JSON": '[{"location":"POP A","olt":"Test OLT","pop":"Core","port":"443","url":"https://olt.example.test"}]',
    })
    def test_private_navigation_data_requires_owner_session(self):
        public_html = self.client.get(reverse("home")).content.decode()
        self.assertNotIn("portal.example.test", public_html)
        session = self.client.session
        session["owner_access"] = True
        session.save()
        owner_html = self.client.get(reverse("home")).content.decode()
        self.assertIn("portal.example.test", owner_html)
        self.assertIn("olt.example.test", owner_html)
