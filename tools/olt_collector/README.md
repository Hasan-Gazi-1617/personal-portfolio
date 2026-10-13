# Local PC OLT collector

The SNMP poller runs on an authorized Local PC, reads the OLT's configured ONU tables, normalizes the result, and sends it to the private Django dashboard over HTTPS. It does not open an inbound port.

## Model-specific setup is required

Huawei, VSOL, CDATA and different firmware releases may use different ONU table OIDs, row indexes and status enumerations. Obtain the MIB for the exact model/firmware and verify each OID/status value. The example configuration contains placeholders and intentionally cannot poll until configured. Do not guess OIDs.

## Requirements

- Python 3.10+
- Net-SNMP command-line tools including `snmpwalk`
- Read-only SNMP access from the collector PC to the OLT management IP
- HTTPS access from the collector PC to the Render dashboard

## Setup

1. Copy `olt_config.example.json` to `olt_config.json`.
2. Fill in OLT identity, management IP, PON count, exact model-specific OIDs and verified status mapping.
3. Set environment variables locally, never in Git:
   - `OLT_CONFIG_FILE=olt_config.json`
   - `OLT_SNMP_COMMUNITY` (or the environment variable named in `snmp.community_env`)
   - `OLT_DASHBOARD_URL=https://YOUR-RENDER-HOST`
   - `OLT_INGEST_TOKEN` (the same long random secret configured in Render Environment settings)
4. Test manually in PowerShell:

   ```powershell
   $env:OLT_CONFIG_FILE = ".\olt_config.json"
   $env:OLT_SNMP_COMMUNITY = "YOUR_READ_ONLY_COMMUNITY"
   $env:OLT_DASHBOARD_URL = "https://YOUR-RENDER-HOST"
   $env:OLT_INGEST_TOKEN = "YOUR_LONG_RANDOM_INGEST_SECRET"
   python .\poll_snmp.py
   ```

5. Compare the dashboard counts against the OLT CLI before scheduling recurring polls.

## OID mapping

- `oids.status` is the operational-status column.
- Optional `onu_id`, `pon_port` and `serial_number` columns must share the status column's row suffix.
- `status_map` maps the exact raw SNMP value to `online`, `offline` or `unknown`.
- If the ONU ID column is omitted, the row suffix is used.

## Security

SNMP v1/v2c communities are not encrypted. Use only on a trusted management network or VPN with a dedicated read-only community restricted to the collector PC's IP. Keep both SNMP community and dashboard token out of Git, screenshots and chat. Never expose OLT management interfaces to the public internet. The poller sends outbound HTTPS only.

The existing `send_snapshot.py` remains available when another approved poller already generates a validated JSON snapshot.
