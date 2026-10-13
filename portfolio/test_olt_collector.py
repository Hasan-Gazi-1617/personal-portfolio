from unittest import TestCase
from unittest.mock import patch

from tools.olt_collector.poll_snmp import parse_walk_output, index_suffix, build_snapshot


class OltSnmpCollectorTests(TestCase):
    def test_parse_walk_output(self):
        parsed = parse_walk_output('.1.3.6.1.4.1.9.1 = INTEGER: 1\n.1.3.6.1.4.1.9.2 = STRING: "online"\n')
        self.assertEqual(parsed[".1.3.6.1.4.1.9.1"], "1")
        self.assertEqual(parsed[".1.3.6.1.4.1.9.2"], "online")

    def test_index_suffix(self):
        self.assertEqual(index_suffix(".1.3.6.1.4.1.9.7", "1.3.6.1.4.1.9"), "7")
        self.assertEqual(index_suffix(".1.3.6.1.4.1.10.7", "1.3.6.1.4.1.9"), "")

    @patch("tools.olt_collector.poll_snmp.walk")
    def test_build_snapshot(self, mocked_walk):
        config = {
            "olt": {"identifier":"test-olt","name":"Test OLT","vendor":"cdata","management_ip":"192.0.2.10","location":"POP","pon_port_count":8},
            "snmp": {"version":"2c"},
            "oids": {"status":"1.3.6.1.4.1.999.1","onu_id":"1.3.6.1.4.1.999.2","pon_port":"1.3.6.1.4.1.999.3","serial_number":"1.3.6.1.4.1.999.4"},
            "status_map": {"1":"online","2":"offline"}
        }
        def fake_walk(ip, oid, snmp, community):
            return {
                "1.3.6.1.4.1.999.1": {".1.3.6.1.4.1.999.1.11":"1",".1.3.6.1.4.1.999.1.12":"2"},
                "1.3.6.1.4.1.999.2": {".1.3.6.1.4.1.999.2.11":"ONU-11",".1.3.6.1.4.1.999.2.12":"ONU-12"},
                "1.3.6.1.4.1.999.3": {".1.3.6.1.4.1.999.3.11":"PON 1",".1.3.6.1.4.1.999.3.12":"PON 2"},
                "1.3.6.1.4.1.999.4": {".1.3.6.1.4.1.999.4.11":"SERIAL11",".1.3.6.1.4.1.999.4.12":"SERIAL12"}
            }[oid]
        mocked_walk.side_effect = fake_walk
        snapshot = build_snapshot(config, "test-community")
        self.assertEqual([o["status"] for o in snapshot["onus"]], ["online","offline"])
        self.assertEqual(snapshot["onus"][0]["pon_port"], "PON 1")
        self.assertEqual(snapshot["onus"][0]["serial_number"], "SERIAL11")
