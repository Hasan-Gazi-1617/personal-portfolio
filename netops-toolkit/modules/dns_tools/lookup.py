import ipaddress

import dns.exception
import dns.resolver
import dns.reversename


RECORD_TYPES = ("A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA")


def _query_record(resolver, name, record_type):
    """Return a readable result for one DNS record without affecting other queries."""
    try:
        answer = resolver.resolve(name, record_type, lifetime=2.5, search=False)
        ttl = answer.rrset.ttl if answer.rrset is not None else "unknown"
        lines = [f"{record_type}  |  TTL: {ttl}s"]
        for item in answer:
            lines.append(f"  {item.to_text()}")
        return lines
    except dns.resolver.NXDOMAIN:
        return [f"{record_type}  |  Domain does not exist"]
    except dns.resolver.NoAnswer:
        return [f"{record_type}  |  No record found"]
    except dns.resolver.NoNameservers:
        return [f"{record_type}  |  No responding name server"]
    except dns.exception.Timeout:
        return [f"{record_type}  |  Query timed out"]
    except dns.exception.DNSException as error:
        return [f"{record_type}  |  DNS error: {error}"]


def lookup(host):
    """Look up common DNS records for a domain, or PTR for an IP address."""
    host = host.strip().rstrip(".")
    if not host or any(char.isspace() for char in host):
        raise ValueError("Enter a valid domain name or IP address.")

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.5
    resolver.lifetime = 3.0

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None

    if address is not None:
        reverse_name = dns.reversename.from_address(str(address))
        output = [
            "DNS LOOKUP RESULTS",
            f"Target: {address}",
            "Lookup type: Reverse DNS (PTR)",
            f"DNS servers: {', '.join(resolver.nameservers)}",
            "",
        ]
        output.extend(_query_record(resolver, reverse_name, "PTR"))
        return "\n".join(output)

    try:
        domain = host.encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise ValueError("Enter a valid international or standard domain name.") from error

    if len(domain) > 253 or any(
        not label or len(label) > 63
        or label.startswith("-") or label.endswith("-")
        or not all(char.isalnum() or char == "-" for char in label)
        for label in domain.split(".")
    ):
        raise ValueError("Enter a valid domain name, for example example.com.")

    output = [
        "DNS LOOKUP RESULTS",
        f"Domain: {domain}",
        "Lookup type: Forward DNS",
        f"DNS servers: {', '.join(resolver.nameservers)}",
        "",
    ]

    for record_type in RECORD_TYPES:
        output.extend(_query_record(resolver, domain, record_type))
        output.append("")

    output.append("Note: 'No record found' means this record type was not published for the domain.")
    return "\n".join(output).rstrip()
