"""Send a collector-produced JSON snapshot to the private Django dashboard.

This is a transport client, not a hardware poller. A vendor-specific, approved
adapter must create the snapshot after model/protocol validation.
"""
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    base_url = os.environ.get("OLT_DASHBOARD_URL", "").rstrip("/")
    token = os.environ.get("OLT_INGEST_TOKEN", "")
    snapshot_path = Path(os.environ.get("OLT_SNAPSHOT_FILE", "olt_snapshot.json"))
    if not base_url.startswith("https://"):
        print("OLT_DASHBOARD_URL must be an HTTPS URL.", file=sys.stderr)
        return 2
    if not token:
        print("OLT_INGEST_TOKEN is required.", file=sys.stderr)
        return 2
    if not snapshot_path.is_file():
        print(f"Snapshot file not found: {snapshot_path}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read JSON snapshot: {exc}", file=sys.stderr)
        return 2
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(body) > 2 * 1024 * 1024:
        print("Snapshot exceeds 2 MiB.", file=sys.stderr)
        return 2
    request = Request(
        base_url + "/api/olt/ingest/",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "HasanNOC-OLT-Collector/0.1",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(json.dumps(result, indent=2))
            return 0
    except HTTPError as exc:
        print(f"Dashboard rejected the report (HTTP {exc.code}).", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(f"Could not submit OLT report: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
