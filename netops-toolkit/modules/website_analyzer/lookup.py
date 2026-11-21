"""Website IP allocation, ASN and multi-location reachability diagnostics.

The user enters only a domain/URL. Results distinguish observed reachability
from confirmed blocking; probe failures alone are never labelled as blocks.
"""
import ipaddress
import json
import socket
import ssl
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


USER_AGENT = "NetOpsToolkit/1.1"


def _get_json(url, timeout=12, accept="application/json"):
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _parse_target(value):
    """Return a normalized host and the complete HTTP(S) URL to test."""
    value = (value or "").strip()
    if not value:
        raise ValueError("Enter a website domain or full URL.")
    parsed = urlparse(value if "://" in value else "https://" + value)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS website URLs are supported.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing usernames or passwords are not supported.")
    host = parsed.hostname
    if not host:
        raise ValueError("Enter a valid website domain.")
    try:
        host = host.encode("idna").decode("ascii").lower().rstrip(".")
        explicit_port = parsed.port
    except (UnicodeError, ValueError) as exc:
        raise ValueError("Invalid website hostname or port.") from exc
    if len(host) > 253 or any(not label or len(label) > 63 for label in host.split(".")):
        raise ValueError("The website domain is not valid.")
    if any(ch.isspace() for ch in host):
        raise ValueError("The website domain contains invalid characters.")
    netloc = host + (f":{explicit_port}" if explicit_port else "")
    target_url = parsed._replace(netloc=netloc, path=parsed.path or "/", fragment="").geturl()
    port = explicit_port or (443 if parsed.scheme.lower() == "https" else 80)
    return host, target_url, parsed.scheme.lower(), port


def _normalise_target(value):
    """Backward-compatible hostname-only normalizer."""
    return _parse_target(value)[0]


def _safe_url_display(value):
    parsed = urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}" + (
        "?[query values redacted]" if parsed.query else ""
    )


def _local_url_test(target_url, timeout=12):
    """Request the exact entered URL and retain HTTP evidence without logging query values."""
    started = time.perf_counter()
    result = {
        "target": _safe_url_display(target_url),
        "status_code": None,
        "final_url": None,
        "server": "Not disclosed",
        "content_type": "Not disclosed",
        "elapsed_ms": None,
        "error": None,
    }
    request = Request(target_url, headers={
        "User-Agent": USER_AGENT,
        "Range": "bytes=0-0",
        "Accept": "*/*",
    }, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            result.update({
                "status_code": response.status,
                "final_url": _safe_url_display(response.geturl()),
                "server": response.headers.get("Server", "Not disclosed"),
                "content_type": response.headers.get("Content-Type", "Not disclosed"),
            })
    except HTTPError as exc:
        result.update({
            "status_code": exc.code,
            "final_url": _safe_url_display(exc.geturl()),
            "server": exc.headers.get("Server", "Not disclosed"),
            "content_type": exc.headers.get("Content-Type", "Not disclosed"),
        })
    except (URLError, TimeoutError, OSError, ssl.SSLError) as exc:
        reason = getattr(exc, "reason", exc)
        result["error"] = f"{type(reason).__name__}: {reason}"
    finally:
        result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return result


def _cidr_ranges(start, end):
    try:
        return [str(net) for net in ipaddress.summarize_address_range(
            ipaddress.ip_address(start), ipaddress.ip_address(end))]
    except (ValueError, TypeError):
        return []


def _resolve_addresses(host):
    results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return sorted(
        {item[4][0].split("%", 1)[0] for item in results},
        key=lambda value: (ipaddress.ip_address(value).version, value),
    )


def _local_web_test(host, port=443, timeout=8):
    """Check HTTPS and HTTP from this computer; do not download page content."""
    report = []
    for scheme, default_port in (("https", 443), ("http", 80)):
        target_port = int(port) if scheme == "https" and int(port) != 443 else default_port
        url = f"{scheme}://{host}" + (f":{target_port}" if target_port != default_port else "/")
        if not url.endswith("/"):
            url += "/"
        request = Request(url, headers={
            "User-Agent": USER_AGENT,
            "Range": "bytes=0-0",
            "Accept": "*/*",
        }, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                report.append(
                    f"{scheme.upper()}: HTTP {response.status} | "
                    f"Final URL: {response.geturl()} | "
                    f"Server: {response.headers.get('Server', 'Not disclosed')}"
                )
        except HTTPError as exc:
            # An HTTP response, including 403/404/5xx, proves the web server replied.
            report.append(
                f"{scheme.upper()}: HTTP {exc.code} | "
                f"Final URL: {exc.geturl()} | Server: "
                f"{exc.headers.get('Server', 'Not disclosed')}"
            )
        except (URLError, TimeoutError, OSError, ssl.SSLError) as exc:
            report.append(f"{scheme.upper()}: Connection failed | {exc}")
    return report


def _tls_certificate(host, port=443, timeout=8):
    context = ssl.create_default_context()
    with socket.create_connection((host, int(port)), timeout=timeout) as raw:
        with context.wrap_socket(raw, server_hostname=host) as secured:
            cert = secured.getpeercert()
            subject = dict(item[0] for item in cert.get("subject", []))
            issuer = dict(item[0] for item in cert.get("issuer", []))
            return {
                "TLS": secured.version() or "Unknown",
                "Cipher": (secured.cipher() or ("Unknown",))[0],
                "Certificate subject": subject.get("commonName", host),
                "Certificate issuer": issuer.get("commonName", "Not published"),
                "Valid from": cert.get("notBefore", "Not published"),
                "Valid until": cert.get("notAfter", "Not published"),
            }


def _allocation_and_bgp(address):
    data = {"address": address, "rdap": None, "bgp": None, "errors": []}
    try:
        rdap = _get_json("https://rdap.org/ip/" + quote(address), timeout=12)
        data["rdap"] = {
            "start": rdap.get("startAddress"),
            "end": rdap.get("endAddress"),
            "cidrs": _cidr_ranges(rdap.get("startAddress"), rdap.get("endAddress"))
                if rdap.get("startAddress") and rdap.get("endAddress") else [],
            "name": rdap.get("name") or "Not published",
            "country": rdap.get("country") or "Not published",
            "handle": rdap.get("handle") or "Not published",
        }
    except Exception as exc:
        data["errors"].append(f"RDAP: {exc}")
    try:
        bgp = _get_json("https://api.bgpview.io/ip/" + quote(address), timeout=12).get("data", {})
        prefixes = []
        for item in bgp.get("prefixes", []):
            asn = item.get("asn") or {}
            prefixes.append({
                "prefix": item.get("prefix", "Unknown"),
                "asn": asn.get("asn", "Unknown"),
                "name": asn.get("name") or "Not published",
                "country": asn.get("country_code") or "Not published",
                "description": asn.get("description") or "",
            })
        data["bgp"] = prefixes
    except Exception as exc:
        data["errors"].append(f"BGP/ASN: {exc}")
    return data


def _global_reachability(host, probe_count=20):
    count = max(1, min(int(probe_count), 20))
    url = f"https://check-host.net/check-http?host={quote(host)}&max_nodes={count}"
    response = _get_json(url, timeout=20)
    request_id = response.get("request_id")
    nodes = response.get("nodes", {})
    if not request_id:
        raise RuntimeError("Global probe provider did not return a request ID.")

    results = {}
    # The provider processes nodes asynchronously. Poll for up to 30 seconds.
    for _ in range(10):
        time.sleep(2)
        results = _get_json(
            f"https://check-host.net/check-result/{quote(request_id)}", timeout=15
        )
        if nodes and all(results.get(node) is not None for node in nodes):
            break

    rows = []
    for node, meta in nodes.items():
        meta = meta if isinstance(meta, (list, tuple)) else []
        country = meta[1] if len(meta) > 1 else "Unknown"
        city = meta[2] if len(meta) > 2 else "Unknown"
        node_ip = meta[3] if len(meta) > 3 else "Unknown"
        asn = meta[4] if len(meta) > 4 else "Unknown ASN"
        result = results.get(node)
        row = {
            "country": country, "city": city, "ip": node_ip, "asn": asn,
            "status": "PENDING", "detail": "No result returned before timeout",
            "http_code": None,
        }
        if isinstance(result, list) and result and isinstance(result[0], list):
            first = result[0]
            code = first[3] if len(first) > 3 else None
            row["http_code"] = code
            detail = first[2] if len(first) > 2 else "No response detail"
            if str(code).isdigit() and 100 <= int(code) <= 599:
                row["status"] = "HTTP RESPONSE"
                row["detail"] = f"HTTP {code}: {detail}"
            else:
                row["status"] = "UNREACHABLE"
                row["detail"] = str(detail)
        elif result is not None:
            row["status"] = "UNREACHABLE"
            row["detail"] = str(result)
        rows.append(row)
    return response.get("permanent_link"), rows


def _compare_public_dns(host, local_addresses):
    """Compare local DNS with Google and Cloudflare DNS-over-HTTPS answers."""
    rows = []
    public_answers = set()
    for record_type in ("A", "AAAA"):
        endpoints = {
            "Google": "https://dns.google/resolve?name=" + quote(host) + "&type=" + record_type,
            "Cloudflare": "https://cloudflare-dns.com/dns-query?name=" + quote(host) + "&type=" + record_type,
        }
        for provider, url in endpoints.items():
            try:
                data = _get_json(url, timeout=8, accept="application/dns-json" if provider == "Cloudflare" else "application/json")
                values = sorted({item.get("data", "").strip().rstrip(".") for item in data.get("Answer", []) if item.get("data")})
                public_answers.update(values)
                rows.append("  " + record_type + " / " + provider + ": " + (", ".join(values) if values else "No answer"))
            except Exception as exc:
                rows.append("  " + record_type + " / " + provider + ": Lookup unavailable (" + str(exc) + ")")
    local_set = set(local_addresses)
    if public_answers and not local_set:
        finding = "LOCAL DNS returned no address, while a public resolver returned records. Local resolver failure or DNS filtering is possible."
    elif public_answers and local_set != public_answers:
        finding = "Local and public DNS answers differ. CDN geography, cache, resolver policy or DNS filtering may explain the difference."
    elif public_answers:
        finding = "Local and public DNS have overlapping results; no obvious DNS discrepancy was detected."
    else:
        finding = "Public DNS comparison unavailable; no DNS filtering conclusion can be made."
    rows.append("  DNS interpretation: " + finding)
    return rows

def analyze_website(target, port=443, probe_count=20, url_test=None):
    """Run domain-level checks and an exact full-URL request."""
    host, target_url, scheme, target_port = _parse_target(target)
    url_test = url_test or _local_url_test(target_url)
    try:
        addresses = _resolve_addresses(host)
    except socket.gaierror as exc:
        raise RuntimeError(
            f"DNS resolution failed for {host}: {exc}\n"
            "Check the spelling and your local DNS/network connection."
        ) from exc
    if not addresses:
        raise RuntimeError("DNS returned no IPv4 or IPv6 address for this website.")

    lines = [
        "=" * 68,
        "NETOPS TOOLKIT | WEBSITE IP & BLOCK DETECTION REPORT",
        "=" * 68,
        f"Website host: {host}",
        f"Exact URL tested: {url_test['target']}",
        f"Analysis time (local): {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Resolved addresses: {len(addresses)}",
        "",
        "[1] DNS / IP ADDRESS DISCOVERY",
    ]
    for address in addresses:
        ip = ipaddress.ip_address(address)
        lines.append(f"  IPv{ip.version:<1}  {address}  |  {ip.is_global and 'Global' or 'Non-global/reserved'}")

    lines.extend(["", "[2] IP ALLOCATION, CIDR, BGP ROUTE & ASN"])
    all_prefixes = set()
    for address in addresses:
        info = _allocation_and_bgp(address)
        lines.append(f"\n  IP: {address}")
        rdap = info["rdap"]
        if rdap:
            lines.append(f"    Registry allocation: {rdap['start'] or '?'} - {rdap['end'] or '?'}")
            lines.append(f"    Allocation CIDR summary: {', '.join(rdap['cidrs']) or 'Not available'}")
            lines.append(f"    Registry/network: {rdap['name']} | Country: {rdap['country']} | Handle: {rdap['handle']}")
        if info["bgp"]:
            for prefix in info["bgp"]:
                all_prefixes.add(prefix["prefix"])
                lines.append(
                    f"    BGP announced prefix: {prefix['prefix']} | "
                    f"AS{prefix['asn']} | {prefix['name']} | {prefix['country']}"
                )
        else:
            lines.append("    BGP route/ASN: No route data returned")
        for error in info["errors"]:
            lines.append(f"    Lookup note: {error}")
    lines.append("\n  Unique BGP prefixes: " + (", ".join(sorted(all_prefixes)) if all_prefixes else "Not available"))

    lines.extend(["", "[3] DNS CROSS-CHECK (LOCAL VS PUBLIC RESOLVERS)"])
    lines.extend(_compare_public_dns(host, addresses))

    lines.extend(["", "[4] EXACT URL / APPLICATION-PATH TEST"])
    lines.append("  Requested URL: " + url_test["target"])
    if url_test["status_code"] is not None:
        lines.append(f"  HTTP status: {url_test['status_code']}")
        lines.append("  Final URL: " + str(url_test["final_url"] or "Not available"))
        lines.append("  Server: " + str(url_test["server"]))
        lines.append("  Content-Type: " + str(url_test["content_type"]))
    else:
        lines.append("  HTTP response: Not received")
        lines.append("  Error: " + str(url_test["error"] or "No details"))
    lines.append("  Request duration: " + str(url_test["elapsed_ms"]) + " ms")
    lines.append("  Note: this is a local exact-path test; global probes below test the hostname only.")

    lines.extend(["", "[5] LOCAL ROOT HTTP / HTTPS REACHABILITY"])
    for result in _local_web_test(host, port):
        lines.append("  " + result)

    lines.extend(["", "[6] TLS CERTIFICATE / ENCRYPTION"])
    try:
        cert = _tls_certificate(host, port)
        for key, value in cert.items():
            lines.append(f"  {key}: {value}")
    except Exception as exc:
        lines.append(f"  TLS inspection unavailable: {exc}")

    lines.extend(["", "[7] GLOBAL COUNTRY / ISP-PROBE REACHABILITY"])
    probes = []
    try:
        report_url, probes = _global_reachability(host, probe_count)
        if report_url:
            lines.append(f"  Provider report: {report_url}")
        reachable = failed = pending = policy = 0
        for probe in probes:
            status = probe["status"]
            if status == "HTTP RESPONSE":
                if probe["http_code"] in (401, 403, 451):
                    policy += 1
                else:
                    reachable += 1
            elif status == "UNREACHABLE":
                failed += 1
            else:
                pending += 1
            lines.append(
                f"  {probe['country']} / {probe['city']} | {probe['asn']} | "
                f"{probe['ip']} | {status} | {probe['detail']}"
            )
        lines.extend([
            "",
            f"  Probe summary: {reachable} HTTP responses, {policy} policy/auth responses, "
            f"{failed} unreachable, {pending} pending",
        ])
    except Exception as exc:
        lines.append(f"  Global probe service unavailable: {exc}")
        lines.append("  Local DNS, IP, allocation and TLS checks are reported separately.")

    lines.extend(["", "[8] AUTOMATIC ROOT-CAUSE FINDINGS"])
    asn_groups = {}
    policy_hits = []
    for probe in probes:
        asn = str(probe.get("asn") or "Unknown ASN")
        group = asn_groups.setdefault(asn, {"failed": 0, "responded": 0})
        if probe.get("status") == "UNREACHABLE":
            group["failed"] += 1
        elif probe.get("status") == "HTTP RESPONSE":
            group["responded"] += 1
            if probe.get("http_code") in (403, 451):
                policy_hits.append(probe)
    failed_total = sum(group["failed"] for group in asn_groups.values())
    response_total = sum(group["responded"] for group in asn_groups.values())
    if policy_hits:
        locations = sorted({str(item.get("country", "Unknown")) for item in policy_hits})
        lines.append("  HTTP POLICY RESPONSE: 403/451 observed in " + ", ".join(locations) + ".")
        lines.append("    Likely explanation: website/CDN/WAF or an intermediary returned a policy response; ISP identity is unknown.")
    correlated = [(asn, group) for asn, group in asn_groups.items() if group["failed"] >= 2 and group["failed"] > group["responded"]]
    if correlated and response_total:
        lines.append("  POSSIBLE NETWORK-PATH / ASN ANOMALY:")
        for asn, group in correlated:
            lines.append("    " + asn + ": " + str(group["failed"]) + " failed, " + str(group["responded"]) + " responded.")
        lines.append("    Possible causes: routing, filtering, firewall or probe-node failure. This is not confirmed ISP blocking.")
    elif failed_total and response_total:
        lines.append("  MIXED GLOBAL RESULT: " + str(response_total) + " responded; " + str(failed_total) + " failed.")
        lines.append("    Likely causes include route differences, DNS, TLS, firewall, geo-policy or probe-node failure.")
        lines.append("    Assessment: INCONCLUSIVE. Repeat tests from the actual affected ISP.")
    elif failed_total and not response_total:
        lines.append("  GLOBAL CONNECTIVITY FAILURE: all completed probes failed.")
        lines.append("    Possible causes: website outage, DNS, routing, firewall or probe-provider issue. Assessment: INCONCLUSIVE.")
    elif response_total:
        lines.append("  NO BLOCK SIGNAL IN TESTED PROBES: " + str(response_total) + " probe(s) received an HTTP response.")
        lines.append("    Redirects such as HTTP 301/302 mean the web endpoint responded successfully.")
    else:
        lines.append("  No completed probe data was available for an automatic diagnosis.")
    lines.extend([
        "",
        "[6] BLOCKING / FAILURE ASSESSMENT",
        "  A probe failure is NOT proof that an ISP blocks this website or its IP range.",
        "  Repeated failures from probes sharing an ASN, while other ASNs succeed, are an ISP-level anomaly worth investigating.",
        "  HTTP 403/451 indicates an HTTP policy response from the responding server or an intermediary; it does not by itself identify the blocking ISP.",
        "  DNS failure, routing loss, TLS errors, server outage, geo-policy and probe-node failure can produce similar symptoms.",
        "  RDAP allocation ranges and BGP announced prefixes are different data; neither proves that a network blocks the site.",
        "",
        "Scope: exact URL/path is tested from this computer; global probes below test the hostname only.",
        "Use this report for diagnostics. Confirm suspected filtering with repeated tests and independent probes in the affected ISP.",
        "=" * 68,
    ])
    lines.extend(["", "[9] PLAIN-LANGUAGE ROOT-CAUSE GUIDE"])
    lines.extend([
        "  DNS filtering: local DNS returns no answer or a different address from independent resolvers.",
        "  Routing issue: DNS resolves, but packets cannot reach the destination network.",
        "  TCP/firewall filtering: port 80/443 is reset, refused or times out.",
        "  TLS issue: TCP connects, but certificate validation or TLS negotiation fails.",
        "  Website/CDN policy: HTTP 403/451 is returned by the origin, CDN, WAF or an intermediary.",
        "  Geo-policy: website/CDN applies rules based on request location.",
        "  Probe failure: the third-party test node itself may be offline or have a route problem.",
    ])
    lines.extend(["", "[10] NOC ENGINEER VERIFICATION"])
    lines.extend([
        "  1. Repeat the test at least 3 times at different times.",
        "  2. Test from the suspected ISP and a second independent ISP.",
        "  3. Compare local DNS answers with an independent resolver.",
        "  4. Check TCP 443, TLS handshake and traceroute/MTR from the affected ISP.",
        "  5. Ask the ISP NOC to inspect DNS policy, firewall/ACL, routing and filtering logs.",
        "  6. Confirm a block only when repeatable tests or ISP-side logs identify the filtering point.",
        "",
        "IMPORTANT: Probe ASN describes the probe node network, not every ISP in that country.",
        "RDAP allocation ranges and BGP announced prefixes do not prove blocking.",
        "CONFIRMED requires direct evidence; PROBABLE means multiple matching signals; INCONCLUSIVE means insufficient evidence.",
    ])
    return "\n".join(lines)


def _trace_route(host, max_hops=20, timeout=2):
    """Run a bounded system traceroute. Missing system utilities are reported clearly."""
    import platform
    import shutil
    import subprocess

    system = platform.system().lower()
    if system == "windows":
        command = ["tracert", "-d", "-h", str(max_hops), "-w", str(timeout * 1000), host]
    elif shutil.which("traceroute"):
        command = ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout), host]
    elif shutil.which("tracepath"):
        command = ["tracepath", "-m", str(max_hops), host]
    else:
        return {
            "available": False,
            "command": "traceroute / tracepath",
            "output": "Traceroute utility is not installed. Linux: sudo apt install traceroute",
            "hops": [],
        }
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=max_hops * timeout + 8,
            check=False,
        )
        output = (completed.stdout or completed.stderr or "").strip()
        hops = []
        for line in output.splitlines():
            stripped = line.strip()
            if stripped:
                hops.append(stripped)
        return {
            "available": True, "command": " ".join(command[:-1]) + " [target]",
            "output": output or "No hop output returned.",
            "hops": hops,
        }
    except subprocess.TimeoutExpired:
        return {"available": True, "command": "traceroute", "output": "Trace timed out.", "hops": []}
    except Exception as exc:
        return {"available": False, "command": "traceroute", "output": str(exc), "hops": []}


def _tcp_port_checks(host, ports=(80, 443, 8080, 8443), timeout=3):
    rows = []
    for port in ports:
        started = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                elapsed = (time.perf_counter() - started) * 1000
                rows.append({"port": port, "status": "OPEN", "latency_ms": round(elapsed, 1), "detail": "TCP connection established"})
        except ConnectionRefusedError:
            rows.append({"port": port, "status": "CLOSED", "latency_ms": None, "detail": "Connection refused"})
        except socket.timeout:
            rows.append({"port": port, "status": "FILTERED / TIMEOUT", "latency_ms": None, "detail": "Connection timed out; filtering and route issues are both possible"})
        except OSError as exc:
            rows.append({"port": port, "status": "UNREACHABLE", "latency_ms": None, "detail": str(exc)})
    return rows


def analyze_website_dashboard(target, port=443, probe_count=20):
    """Return exact-URL and domain-level evidence for the dashboard."""
    host, target_url, scheme, target_port = _parse_target(target)
    url_test = _local_url_test(target_url)
    try:
        report = analyze_website(target, port, probe_count, url_test=url_test)
    except RuntimeError as exc:
        # Preserve a useful diagnosis when the local resolver cannot resolve
        # the domain instead of aborting the whole dashboard.
        if "DNS resolution failed" not in str(exc) and "DNS returned no" not in str(exc):
            raise
        url_status = (
            f"HTTP {url_test['status_code']}"
            if url_test["status_code"] is not None
            else f"No HTTP response | {url_test['error'] or 'No additional error detail'}"
        )
        report = (
            "=" * 68 + "\n"
            "NETOPS TOOLKIT | WEBSITE & NETWORK ROOT CAUSE REPORT\n"
            + "=" * 68 + "\n"
            + f"Website host: {host}\n"
            + f"Exact URL tested: {url_test['target']}\n"
            + f"LOCAL DNS ERROR: {exc}\n"
            + f"EXACT URL TEST: {url_status}\n"
            + "\n".join(_compare_public_dns(host, []))
        )
    try:
        addresses = _resolve_addresses(host)
    except Exception:
        addresses = []
    tcp = _tcp_port_checks(host)
    trace_target = addresses[0] if addresses else host
    trace = _trace_route(trace_target)
    return {
        "host": host,
        "target_url": url_test["target"],
        "url_test": url_test,
        "trace_target": trace_target,
        "report": report,
        "addresses": addresses,
        "tcp": tcp,
        "trace": trace,
        "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
            + "\n".join(_compare_public_dns(host, []))
        )
    try:
        addresses = _resolve_addresses(host)
    except Exception:
        addresses = []
    tcp = _tcp_port_checks(host)
    trace_target = addresses[0] if addresses else host
    trace = _trace_route(trace_target)
    return {
        "host": host,
        "trace_target": trace_target,
        "report": report,
        "addresses": addresses,
        "tcp": tcp,
        "trace": trace,
        "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
