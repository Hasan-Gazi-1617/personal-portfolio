"""Website IP allocation and multi-location reachability diagnostics."""
import ipaddress
import json
import socket
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def _get_json(url, timeout=12):
    request = Request(url, headers={"User-Agent": "NetOpsToolkit/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _normalise_target(value):
    value = value.strip()
    if not value:
        raise ValueError("Enter a website domain, for example example.com.")
    parsed = urlparse(value if "://" in value else "//" + value)
    host = parsed.hostname
    if not host:
        raise ValueError("Enter a valid website domain.")
    try:
        return host.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Invalid international domain name.") from exc


def _cidr_ranges(start, end):
    try:
        return [str(net) for net in ipaddress.summarize_address_range(
            ipaddress.ip_address(start), ipaddress.ip_address(end))]
    except ValueError:
        return []


def analyze_website(target, port=443, probe_count=20):
    host = _normalise_target(target)
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise RuntimeError(f"Local DNS resolution failed: {exc}") from exc
    addresses = sorted({item[4][0] for item in records}, key=lambda item: (ipaddress.ip_address(item).version, item))
    if not addresses:
        raise RuntimeError("No A or AAAA address was returned.")

    lines = [
        "WEBSITE IP & GLOBAL REACHABILITY REPORT",
        f"Website: {host}",
        f"Local DNS addresses: {len(addresses)}",
        "",
        "RESOLVED IP ADDRESSES",
    ]
    for address in addresses:
        lines.append(f"  IPv{ipaddress.ip_address(address).version}: {address}")
    lines.extend(["", "IP ALLOCATION / ASN INFORMATION"])
    for address in addresses:
        lines.append(f"\n[{address}]")
        try:
            rdap = _get_json("https://rdap.org/ip/" + quote(address), timeout=12)
            start, end = rdap.get("startAddress"), rdap.get("endAddress")
            if start and end:
                lines.append(f"  RDAP allocation range: {start} - {end}")
                for block in _cidr_ranges(start, end):
                    lines.append(f"  CIDR summary: {block}")
            lines.append(f"  Network name: {rdap.get('name') or 'Not published'}")
            lines.append(f"  Country: {rdap.get('country') or 'Not published'}")
            lines.append(f"  Handle: {rdap.get('handle') or 'Not published'}")
            try:
                bgp = _get_json("https://api.bgpview.io/ip/" + quote(address), timeout=10).get("data", {})
                prefixes = bgp.get("prefixes", [])
                if prefixes:
                    prefix = prefixes[0]
                    asn = prefix.get("asn", {})
                    lines.append(f"  BGP route prefix: {prefix.get('prefix', 'Not published')}")
                    lines.append(f"  Origin ASN: AS{asn.get('asn', 'Unknown')}")
                    lines.append(f"  ASN name: {asn.get('name') or 'Not published'}")
                    lines.append(f"  ASN country: {asn.get('country_code') or 'Not published'}")
                else:
                    lines.append("  BGP route / ASN: No route data returned")
            except Exception as bgp_error:
                lines.append(f"  BGP route / ASN lookup unavailable: {bgp_error}")
            for entity in rdap.get("entities", []):
                for item in entity.get("vcardArray", [None, []])[1]:
                    if item and item[0] == "fn":
                        lines.append(f"  Registry contact: {item[3]}")
                        break
        except Exception as exc:
            lines.append(f"  RDAP lookup unavailable: {exc}")

    lines.extend(["", "GLOBAL HTTP REACHABILITY"])
    try:
        request_url = f"https://check-host.net/check-http?host={quote(host)}&max_nodes={max(1, min(int(probe_count), 20))}"
        response = _get_json(request_url, timeout=20)
        request_id = response.get("request_id")
        nodes = response.get("nodes", {})
        if not request_id:
            raise RuntimeError("Global probe provider did not return a request ID.")
        lines.append(f"Probe request: {request_id}")
        lines.append(f"Report: {response.get('permanent_link', 'Not available')}")
        results = {}
        for attempt in range(6):
            time.sleep(2)
            results = _get_json(f"https://check-host.net/check-result/{quote(request_id)}", timeout=15)
            if nodes and all(results.get(node) is not None for node in nodes):
                break
        lines.append("")
        reachable = failed = pending = 0
        for node, meta in nodes.items():
            country = meta[1] if len(meta) > 1 else "Unknown"
            city = meta[2] if len(meta) > 2 else "Unknown"
            asn = meta[4] if len(meta) > 4 else "Unknown ASN"
            data = results.get(node)
            if data is None:
                status = "PENDING"; pending += 1
                detail = "Probe did not return a result in time"
            elif isinstance(data, list) and data and isinstance(data[0], list):
                first = data[0]
                code = first[3] if len(first) > 3 else None
                http_response = str(code).isdigit() and 100 <= int(code) <= 599
                if http_response:
                    status = "HTTP POLICY RESPONSE" if int(code) in (401, 403, 451) else "REACHABLE"
                    reachable += 1
                else:
                    status = "UNREACHABLE"
                    failed += 1
                detail = f"HTTP {code or 'no status'}: {first[2] if len(first) > 2 else 'No response'}"
            else:
                status = "UNREACHABLE"; failed += 1
                detail = str(data)
            lines.append(f"  {country} / {city} / {asn}: {status} | {detail}")
        lines.extend([
            "",
            f"Summary: {reachable} reachable, {failed} unsuccessful, {pending} pending",
            "IMPORTANT: An unsuccessful probe is not proof of ISP blocking. It can also indicate routing, DNS, TLS, server, firewall, or probe-node failure.",
            "This test uses third-party global probe nodes. It does not identify every ISP in a country.",
        ])
    except Exception as exc:
        lines.extend(["", f"Global probe test unavailable: {exc}",
                      "Local DNS and RDAP results above are still valid."])
    return "\n".join(lines)
