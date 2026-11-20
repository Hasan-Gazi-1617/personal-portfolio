import dns.resolver

def lookup(host):
    host = host.strip().rstrip(".")
    if not host or any(c.isspace() for c in host):
        raise ValueError("Enter a valid domain name.")
    resolver = dns.resolver.Resolver()
    output = []
    for kind in ("A", "AAAA"):
        try:
            answers = resolver.resolve(host, kind, lifetime=5)
            output.append(kind + ":")
            output.extend("  " + answer.to_text() for answer in answers)
        except dns.resolver.NXDOMAIN:
            output.append(kind + ": domain does not exist")
        except dns.resolver.NoAnswer:
            output.append(kind + ": no record")
        except dns.exception.Timeout:
            output.append(kind + ": query timed out")
        except dns.resolver.NoNameservers:
            output.append(kind + ": no responding nameserver")
    return "\n".join(output)
