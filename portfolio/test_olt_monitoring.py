import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import OLTDevice, ONUStatus, OLTEvent


@override_settings(SECURE_SSL_REDIRECT=False)
class OLTMonitoringTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["owner_access"] = True
        session.save()
        self.headers = {"HTTP_AUTHORIZATION": "Bearer test-collector-secret"}
        self.payload = {
            "olt": {
                "identifier": "pop-a-olt-01",
                "name": "POP A OLT 01",
                "vendor": "Huawei",
                "location": "POP A",
                "management_ip": "192.0.2.10",
                "pon_port_count": 16,
            },
            "onus": [
                {"id": "onu-001", "pon_port": "0/1/1", "status": "online", "serial_number": "EXAMPLE0001"},
                {"id": "onu-002", "pon_port": "0/1/1", "status": "offline", "serial_number": "EXAMPLE0002"},
            ],
        }

    @patch.dict("os.environ", {"OLT_INGEST_TOKEN": "test-collector-secret"})
    def test_private_dashboard_shows_empty_state_without_fake_data(self):
        self.client.session["owner_access"] = True
        response = self.client.get(reverse("olt_monitoring_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collector not connected")
        self.assertContains(response, "No OLT data received yet")
        self.assertEqual(OLTDevice.objects.count(), 0)

    def test_dashboard_requires_owner_session(self):
        self.client.session.flush()
        response = self.client.get(reverse("olt_monitoring_dashboard"))
        self.assertRedirects(response, reverse("owner_login"))

    @patch.dict("os.environ", {"OLT_INGEST_TOKEN": "test-collector-secret"})
    def test_ingestion_requires_bearer_token(self):
        response = self.client.post(
            reverse("olt_ingest"),
            data=json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(OLTDevice.objects.count(), 0)

    @patch.dict("os.environ", {"OLT_INGEST_TOKEN": "test-collector-secret"})
    def test_ingestion_records_inventory_and_status_transitions(self):
        response = self.client.post(
            reverse("olt_ingest"),
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(OLTDevice.objects.count(), 1)
        self.assertEqual(ONUStatus.objects.count(), 2)
        self.assertEqual(OLTEvent.objects.count(), 2)
        self.payload["onus"][0]["status"] = "offline"
        response = self.client.post(
            reverse("olt_ingest"),
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(OLTEvent.objects.count(), 3)
        self.assertEqual(ONUStatus.objects.get(onu_id="onu-001").status, "offline")

    @patch.dict("os.environ", {"OLT_INGEST_TOKEN": "test-collector-secret"})
    def test_invalid_ip_is_rejected_without_creating_olt(self):
        self.payload["olt"]["management_ip"] = "not-an-ip"
        response = self.client.post(
            reverse("olt_ingest"),
            data=json.dumps(self.payload),
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(OLTDevice.objects.count(), 0)
