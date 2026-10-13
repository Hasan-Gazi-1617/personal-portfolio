"""Poll an OLT's configured SNMP tables and submit a live snapshot.

Requires Net-SNMP's snmpwalk executable on the collector PC. OIDs and status
values are configuration-driven and must match the exact OLT model/firmware MIB.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def parse_walk_output(output: str) -> dict[str, str]:
    """Convert snmpwalk -On output to {numeric_oid: value}."""
    values = {}
    for line in output.splitlines():
        if " = " not in line:
            continue
        oid, raw = line.split(" = ", 1)
        oid = oid.strip()
        if not re.fullmatch(r"\.\d+(?:\.\d+)*", oid):
            continue
        if ": " in raw:
            kind, remainder = raw.split(": ", 1)
            if kind.upper() in {
                "INTEGER", "INTEGER32", "GAUGE", "GAUGE32", "COUNTER",
                "COUNTER32", "COUNTER64", "TIMETICKS", "OCTET STRING",
                "STRING", "HEX-STRING", "OID", "IPADDRESS", "OPAQUE",
            }:
                raw = remainder
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] == raw[-1] == '"':
            raw = raw[1:-1]
        values[oid] = raw
    return values


def index_suffix(oid: str, base: str) -> str:
    normalized_base = "." + base.strip(".")
    normalized_oid = "." + oid.strip(".")
    if normalized_oid == normalized_base:
        return ""
    prefix = normalized_base + "."
    if normalized_oid.startswith(prefix):
        return normalized_oid[len(prefix):]
    return ""


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = ("identifier", "name", "vendor", "management_ip", "pon_port_count")
    missing = [key for key in required if key not in config.get("olt", {})]
    if missing:
        raise ValueError("Missing olt config fields: " + ", ".join(missing))
    snmp = config.get("snmp", {})
    oids = config.get("oids", {})
    if not snmp.get("community_env"):
        raise ValueError("snmp.community_env must name an environment variable")
    if not oids.get("status"):
        raise ValueError("oids.status must contain the ONU operational-status column OID")
    if not config.get("status_map"):
        raise ValueError("status_map must map device-specific values to online/offline/unknown")
    return config


def walk(ip: str, oid: str, snmp: dict, community: str) -> dict[str, str]:
    executable = shutil.which(snmp.get("walk_command", "snmpwalk"))
    if not executable:
        raise RuntimeError("snmpwalk was not found. Install Net-SNMP on this collector PC.")
    version = str(snmp.get("version", "2c"))
    if version not in {"1", "2c"}:
        raise ValueError("This collector supports SNMP v1/v2c only.")
    command = [
        executable, "-v" + version, "-c", community,
        "-t", str(float(snmp.get("timeout_seconds", 2))),
        "-r", str(int(snmp.get("retries", 1))),
        "-On", ip, oid,
    ]
    result = subprocess.run(
        command, check=False, capture_output=True, text=True,
        timeout=max(10, float(snmp.get("command_timeout_seconds", 60))),
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "snmpwalk failed").strip()
        raise RuntimeError(f"SNMP walk failed for {oid}: {detail[:400]}")
    return parse_walk_output(result.stdout)


def build_snapshot(config: dict, community: str) -> dict:
    olt = config["olt"]
    snmp = config["snmp"]
    oids = config["oids"]
    status_oid = oids["status"].strip(".")
    status_values = walk(olt["management_ip"], status_oid, snmp, community)
    if not status_values:
        raise RuntimeError("The ONU status table returned no rows; verify OID, SNMP access and MIB.")
    optional_tables = {}
    for field in ("onu_id", "pon_port", "serial_number"):
        base = oids.get(field)
        optional_tables[field] = walk(olt["management_ip"], base.strip("."), snmp, community) if base else {}

    status_map = {str(key).strip().lower(): str(value).strip().lower()
                  for key, value in config["status_map"].items()}
    onus = []
    for status_full_oid, raw_status in sorted(status_values.items()):
        suffix = index_suffix(status_full_oid, status_oid)
        if not suffix:
            continue
        status = status_map.get(raw_status.strip().lower(), "unknown")
        if status not in {"online", "offline", "unknown"}:
            status = "unknown"

        def table_value(name: str, default: str = "") -> str:
            base = oids.get(name)
            if not base:
                return default
            full_oid = "." + base.strip(".") + "." + suffix
            value = optional_tables[name].get(full_oid, default)
            return str(value).strip()[:100]

        onu_id = table_value("onu_id", suffix) or suffix
        pon_port = table_value("pon_port", "")
        serial = table_value("serial_number", "")
        onus.append({
            "id": onu_id,
            "pon_port": pon_port[:40],
            "status": status,
            "serial_number": serial[:100],
        })

    if not onus:
        raise RuntimeError("No usable ONU status rows found. Check that configured columns share the same row index.")
    return {
        "olt": {
            "identifier": str(olt["identifier"]),
            "name": str(olt["name"]),
            "vendor": str(olt["vendor"]).lower(),
            "location": str(olt.get("location", "")),
            "management_ip": str(olt["management_ip"]),
            "pon_port_count": int(olt["pon_port_count"]),
        },
        "onus": onus,
    }


def submit_snapshot(payload: dict, base_url: str, token: str) -> dict:
    if not base_url.startswith("https://"):
        raise ValueError("OLT_DASHBOARD_URL must be an HTTPS URL")
    if not token:
        raise ValueError("OLT_INGEST_TOKEN is required")
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(body) > 2 * 1024 * 1024:
        raise ValueError("Snapshot exceeds the dashboard's 2 MiB limit")
    request = Request(
        base_url.rstrip("/") + "/api/olt/ingest/",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "HasanNOC-OLT-SNMP-Collector/1.0",
        },
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    config_path = Path(os.environ.get("OLT_CONFIG_FILE", "olt_config.json"))
    try:
        config = load_config(config_path)
        community_name = config["snmp"]["community_env"]
        community = os.environ.get(community_name, "")
        if not community:
            raise ValueError(f"SNMP community is empty; set environment variable {community_name}")
        payload = build_snapshot(config, community)
        result = submit_snapshot(
            payload,
            os.environ.get("OLT_DASHBOARD_URL", ""),
            os.environ.get("OLT_INGEST_TOKEN", ""),
        )
        print(json.dumps({
            "ok": result.get("ok", False),
            "olt": result.get("olt", config["olt"]["identifier"]),
            "onus_in_snapshot": len(payload["onus"]),
            "created_onus": result.get("created_onus", 0),
            "updated_onus": result.get("updated_onus", 0),
            "events_created": result.get("events_created", 0),
            "received_at": result.get("received_at"),
        }, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError,
            subprocess.TimeoutExpired, HTTPError, URLError, TimeoutError) as exc:
        print(f"OLT collector error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
