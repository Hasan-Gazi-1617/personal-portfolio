from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from portfolio.models import ComplaintTicket


class TicketSLATests(TestCase):
    def make_ticket(self, **kwargs):
        values = {
            "tki_id": "TKI-TEST-001",
            "client_id": "CLIENT-001",
            "opened_at": timezone.now() - timedelta(hours=3),
            "complaint": "Test connectivity issue",
            "category": ComplaintTicket.Category.WIFI,
            "sla_hours": 2,
        }
        values.update(kwargs)
        return ComplaintTicket.objects.create(**values)

    def test_issue_and_support_sla_defaults(self):
        self.assertEqual(ComplaintTicket.default_sla_hours("fiber", "phone"), 4)
        self.assertEqual(ComplaintTicket.default_sla_hours("wifi", "phone"), 1)
        self.assertEqual(ComplaintTicket.default_sla_hours("wifi", "field"), 2)
        self.assertEqual(ComplaintTicket.default_sla_hours("installation", "field"), 24)
        self.assertEqual(ComplaintTicket.default_sla_hours("billing", "field"), 1)

    def test_active_dependency_time_is_excluded_from_sla(self):
        ticket = self.make_ticket(dependency=ComplaintTicket.Dependency.ISP)
        ComplaintTicket.objects.filter(pk=ticket.pk).update(
            dependency_started_at=timezone.now() - timedelta(hours=2)
        )
        ticket.refresh_from_db()
        # Three hours have elapsed overall, but two hours were blocked by dependency.
        self.assertLess(ticket.elapsed_sla_seconds(), 2 * 3600)
        self.assertFalse(ticket.sla_breached)

    def test_clearing_dependency_persists_paused_duration(self):
        ticket = self.make_ticket()
        paused_start = timezone.now() - timedelta(hours=2)
        ComplaintTicket.objects.filter(pk=ticket.pk).update(
            dependency=ComplaintTicket.Dependency.ISP,
            dependency_started_at=paused_start,
        )
        ticket.refresh_from_db()
        ticket.dependency = ""
        ticket.save()
        self.assertGreaterEqual(ticket.dependency_paused_seconds, 2 * 3600 - 5)
        self.assertLess(ticket.elapsed_sla_seconds(), 2 * 3600)

    def test_repeated_client_id_in_same_month_is_flagged(self):
        first = self.make_ticket(tki_id="TKI-REPEAT-1", client_id="REPEAT-CLIENT")
        second = self.make_ticket(
            tki_id="TKI-REPEAT-2",
            client_id="repeat-client",
            opened_at=first.opened_at + timedelta(days=1),
        )
        self.assertEqual(first.status_type, ComplaintTicket.StatusType.NEW)
        first.remarks = "Routine correction after repeat"
        first.save()
        first.refresh_from_db()
        self.assertEqual(first.status_type, ComplaintTicket.StatusType.NEW)
        self.assertEqual(second.status_type, ComplaintTicket.StatusType.REPEAT)
        self.assertEqual(second.repeat_reason, ComplaintTicket.RepeatReason.OTHER)
        self.assertIn("Auto-flagged: repeated Client ID", second.repeat_note)

    def test_same_client_in_different_month_is_not_automatically_flagged(self):
        first = self.make_ticket(tki_id="TKI-MONTH-1", client_id="MONTH-CLIENT")
        second = self.make_ticket(
            tki_id="TKI-MONTH-2",
            client_id="MONTH-CLIENT",
            opened_at=first.opened_at.replace(day=1) - timedelta(days=1),
        )
        self.assertNotEqual(second.status_type, ComplaintTicket.StatusType.REPEAT)
