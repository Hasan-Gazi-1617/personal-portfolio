import os
import re
from unittest.mock import patch
from pathlib import Path

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import ComplaintTicket

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
@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=TEST_STORAGES)
class TkiWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user("hasan-admin", password="StrongPass123!", is_staff=True)
        self.engineer = user_model.objects.create_user("engineer-one", password="StrongPass123!", first_name="Engineer", last_name="One")
        self.other_engineer = user_model.objects.create_user("engineer-two", password="StrongPass123!", first_name="Engineer", last_name="Two")
        self.ticket = ComplaintTicket.objects.create(
            tki_id="TKI-1001",
            client_id="397",
            opened_at=timezone.now(),
            category=ComplaintTicket.Category.FIBER,
            priority=ComplaintTicket.Priority.HIGH,
            complaint="ONU LOS blinking",
            created_by=self.admin_user,
        )

    def test_dashboard_requires_engineer_login(self):
        response = self.client.get(reverse("tki_dashboard"))
        self.assertRedirects(response, f'{reverse("tki_login")}?next={reverse("tki_dashboard")}')

    def test_dashboard_has_engineer_reports_and_named_teams(self):
        ComplaintTicket.objects.create(
            tki_id="TKI-REPORT-1", client_id="C-100", opened_at=timezone.now(),
            status=ComplaintTicket.Status.PENDING,
            dependency=ComplaintTicket.Dependency.ISP,
            field_support_engineer=ComplaintTicket.SupportEngineer.ABIR,
            higher_level_noc=ComplaintTicket.NocEngineer.HASAN,
            complaint="Upstream issue", remarks="Waiting for ISP feedback",
            attention=True, created_by=self.admin_user,
        )
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("tki_dashboard"), {"period": "daily"})
        self.assertContains(response, "ISP TKI Dashboard")
        self.assertContains(response, "Pending per field engineer")
        self.assertContains(response, "Pending by dependency")
        self.assertContains(response, "Abir")
        self.assertContains(response, "Waiting for ISP feedback")
        self.assertEqual(response.context["summary"]["pending"], 2)
        self.assertEqual(response.context["summary"]["dependency"], 1)

    def test_admin_can_create_for_any_engineer(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("tki_create"), {
            "tki_id": "TKI-1002", "client_id": "3437",
            "opened_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
            "category": ComplaintTicket.Category.ROUTER,
            "priority": ComplaintTicket.Priority.MEDIUM,
            "status": ComplaintTicket.Status.PENDING,
            "complaint": "Slow internet from router",
            "assigned_engineer": self.engineer.pk,
        })
        created = ComplaintTicket.objects.get(tki_id="TKI-1002")
        self.assertRedirects(response, reverse("tki_detail", args=(created.pk,)))
        self.assertEqual(created.assigned_engineer, self.engineer)
        self.assertEqual(created.status, ComplaintTicket.Status.PENDING)

    def test_engineer_cannot_create_tki(self):
        self.client.force_login(self.engineer)
        self.assertEqual(self.client.get(reverse("tki_create")).status_code, 403)

    def test_engineer_can_claim_only_unassigned_tki(self):
        self.client.force_login(self.engineer)
        response = self.client.post(reverse("tki_claim", args=(self.ticket.pk,)))
        self.assertRedirects(response, reverse("tki_detail", args=(self.ticket.pk,)))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_engineer, self.engineer)

    def test_engineer_cannot_take_another_engineers_tki(self):
        self.ticket.assigned_engineer = self.other_engineer
        self.ticket.save()
        self.client.force_login(self.engineer)
        self.assertEqual(self.client.post(reverse("tki_claim", args=(self.ticket.pk,))).status_code, 403)

    def test_assigned_engineer_can_resolve_with_feedback(self):
        self.ticket.assigned_engineer = self.engineer
        self.ticket.save()
        self.client.force_login(self.engineer)
        response = self.client.post(reverse("tki_update", args=(self.ticket.pk,)), {
            "status": ComplaintTicket.Status.SOLVED,
            "findings": "Fiber break identified.",
            "troubleshooting": "Fiber team restored the cable.",
            "resolution": "Client confirmed service restoration.",
        })
        self.assertRedirects(response, reverse("tki_detail", args=(self.ticket.pk,)))
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, ComplaintTicket.Status.SOLVED)
        self.assertIsNotNone(self.ticket.resolved_at)

    def test_other_engineer_cannot_update_ticket(self):
        self.ticket.assigned_engineer = self.other_engineer
        self.ticket.save()
        self.client.force_login(self.engineer)
        response = self.client.post(reverse("tki_update", args=(self.ticket.pk,)), {
            "status": ComplaintTicket.Status.PENDING,
            "findings": "Attempted access",
            "troubleshooting": "None",
            "resolution": "",
        })
        self.assertEqual(response.status_code, 403)
