import json
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from .models import ONUEvent, ONUStatus


class OLTMonitorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.payload = {
            "olt_key": "cdata-gpon-15",
            "observed_at": "2026-09-22T10:00:00Z",
            "onus": [
                {
                    "pon_id": "0/0/5",
                    "onu_id": "4",
                    "serial": "D011A6B0A814",
                    "description": "MIT-CPID1449",
                    "status": "online",
                }
            ],
        }

    def _post(self, payload):
        return self.client.post(
            reverse("olt_ingest"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-token",
        )

    def test_dashboard_requires_owner_session(self):
        response = self.client.get(reverse("olt_dashboard"))
        self.assertRedirects(response, reverse("owner_login"))

    @patch.dict("os.environ", {"OLT_INGEST_TOKEN": "test-token"})
    def test_online_to_offline_creates_down_event(self):
        self.assertEqual(self._post(self.payload).status_code, 200)
        self.payload["observed_at"] = "2026-09-22T10:01:00Z"
        self.payload["onus"][0]["status"] = "offline"
        self.payload["onus"][0]["down_reason"] = "LOS"
        response = self._post(self.payload)
        self.assertEqual(response.status_code, 200)
        onu = ONUStatus.objects.get()
        self.assertEqual(onu.description, "MIT-CPID1449")
        self.assertEqual(onu.status, ONUStatus.OFFLINE)
        self.assertEqual(ONUEvent.objects.filter(event_type=ONUEvent.DOWN).count(), 1)
