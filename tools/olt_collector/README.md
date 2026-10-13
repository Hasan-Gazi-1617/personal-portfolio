# Local PC OLT collector — integration contract

The Django dashboard and authenticated ingestion endpoint are the first implementation stage. This folder documents the local-agent contract; it does **not** claim to poll hardware yet.

## Why a local collector

The portfolio is hosted on Render, while OLT management IPs are normally reachable only from the NOC/local network. The collector should run on an authorized Local PC that can reach the OLT management plane, then send outbound HTTPS requests to Django. Do not expose OLT management interfaces to the public internet.

## Before enabling vendor polling

For each Huawei, VSOL, CDATA or other OLT, confirm the exact model, firmware, management IP/reachability and whether SNMP (preferably read-only SNMPv3) or SSH/CLI access is approved. Protocol is currently unknown, so no SNMP OIDs or CLI parsing assumptions are enabled by this first stage.

## Ingestion API

- Endpoint: `POST /api/olt/ingest/`
- Authentication: `Authorization: Bearer <OLT_INGEST_TOKEN>`
- Configure a long random `OLT_INGEST_TOKEN` environment variable on Render and keep the same secret only on the trusted collector PC.
- Content type: `application/json`
- Payload is limited by the endpoint to 2 MiB.

Example payload (test format only; not real/live data):

```json
{
  "olt": {
    "identifier": "pop-a-olt-01",
    "name": "POP A OLT 01",
    "vendor": "Huawei",
    "location": "POP A",
    "management_ip": "192.0.2.10",
    "pon_port_count": 16
  },
  "onus": [
    {"id": "onu-001", "pon_port": "0/1/1", "status": "online", "serial_number": "EXAMPLE0001"},
    {"id": "onu-002", "pon_port": "0/1/1", "status": "offline", "serial_number": "EXAMPLE0002"}
  ]
}
```

Accepted ONU status values are `online`, `offline`, and `unknown`. Each report represents the current observed state for the included ONUs. Events are created when a known ONU changes between online and offline. The API does not delete unseen ONUs; a vendor adapter must report a complete inventory or explicitly handle stale records.

## Safety checklist

- Use read-only monitoring credentials and least privilege.
- Keep management IPs and credentials out of public HTML, source control and logs.
- Do not put the ingestion token in browser JavaScript.
- Do not set up polling until the device model/protocol and allowed access method are confirmed.
