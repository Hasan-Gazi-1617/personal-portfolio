# NetOps Toolkit

Cross-platform desktop network operations and diagnostics toolkit built with Python and PySide6. The application header centers the NetOps Toolkit title and provides a direct Check My Portfolio link.

## Features

- **Network Analyzer:** Wireshark-inspired live packet capture, interface selection, BPF capture filters, protocol/IP/port display filters, decoded packet details and PCAP export. The PCAP File Inspector opens offline PCAP/PCAPNG files, shows protocol counts and lets you inspect decoded packet layers.
- **Website Network Block Checker:** Starts with one clear question: is the website reachable from this computer's current network? Shows a simple final verdict, DNS/TCP/HTTPS status cards, a step-by-step connection path, a possible fault-domain explanation, route trace and technical evidence. Global probes are supporting comparison only. Timeouts, HTTP policy responses and silent traceroute hops are not automatically labelled as ISP blocks.
- **Ping Test:** User-configurable request count (1-1000), automatic/IPv4/IPv6 mode and raw platform ping output.
- **IP Calculator:** IPv4 and IPv6 subnet calculation, prefix slider, subnet splitting, address ranges, masks and copy actions.
- **Fiber & OLT Tools:** GPON optical link-budget estimate, splitter/connector/splice loss, ONU receive-power assessment and practical OLT troubleshooting reference.
- **Bandwidth & Unit Converter:** bps/Kbps/Mbps/Gbps/Tbps and byte-throughput conversion, download-time estimate, shared-capacity planning and 30-day traffic projection.
- **NOC Reference Library:** searchable OSI, TCP/UDP ports, private IP ranges, Linux and MikroTik commands, VLAN, DNS, GPON and incident/TKI guides.
- Dark and light themes. Every diagnostic module includes a **Clear All** action.

## Website Block Checker: how to read the result

- The main result is one of: NOT BLOCKED, POLICY RESPONSE, SERVER ERROR, POSSIBLE NETWORK BLOCK, WEBSITE NOT OPENING (DNS problem) or WEBSITE NOT OPENING / POSSIBLE NETWORK BLOCK. A successful HTTP response (including a redirect) means the website responded from this network. HTTP 403/451 means a server or intermediary refused the request, not necessarily the ISP.
- The page is organized into Simple Diagnosis, Where is the problem?, Network Path and Technical Details. Export saves the verdict and supporting evidence.
- Route Trace runs from the computer using the installed system utility (`traceroute` or `tracepath` on Linux/macOS, `tracert` on Windows). On Ubuntu/Debian, install it with `sudo apt install traceroute`. A hop that does not answer may be filtering ICMP/UDP probes or rate-limiting; it does not prove that traffic is blocked at that hop.
- TCP port tests report OPEN, CLOSED, FILTERED/TIMEOUT or UNREACHABLE. A timeout is ambiguous and must be compared with a second network and repeated tests.

- Enter a domain such as `example.com` or a URL such as `https://example.com`. The tool tests access from the computer running NetOps Toolkit. Global probes are separate third-party checks and do not directly test the user's ISP.
- DNS answers can vary by resolver, region, CDN, time and client network. The IP list is the answer visible from the computer running NetOps Toolkit.
- RDAP allocation ranges describe registry allocation. BGP prefixes describe routed announcements. They are different and neither one proves that an IP range is blocked.
- Global reachability checks use third-party probe nodes. The app displays the country/city/ASN returned by the provider; it cannot test every ISP or every network in a country.
- A failed probe is **not proof of ISP blocking**. DNS, routing, firewall, TLS, server policy, geo restrictions and probe-node availability can all affect results. The report compares local DNS with Google and Cloudflare DNS-over-HTTPS, groups failed probes by their reported ASN, highlights HTTP 403/451 policy responses, and explains likely fault domains. ASN correlation is only an anomaly to investigate, not a definitive block verdict. Public DNS differences can also be caused by CDN geography, caching or resolver policy.
- HTTP 403/451 responses are policy/authentication responses from the server or an intermediary. They do not independently identify which ISP, if any, applied a block.
- External RDAP, BGP and probe services must be reachable from the computer for their respective sections to return data.

## Other important notes

- Packet capture requires suitable privileges and packet-capture support. Windows requires Npcap; Linux generally requires libpcap and capture permissions; macOS requires packet-capture permissions.
- Use packet capture only on networks and devices you own or are authorized to monitor.

## Download

Open [GitHub Releases](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest) and download the asset for your operating system:

| OS | Package |
|---|---|
| Windows 10/11 | `NetOpsToolkit-Windows.exe` |
| Ubuntu / Debian | `NetOpsToolkit-Linux.deb` |
| Other compatible Linux | `NetOpsToolkit-Linux.AppImage` |
| macOS | `NetOpsToolkit-macOS.dmg` |

A package is available only after the corresponding workflow build succeeds and the release asset is published.

## Build from source

Python 3.11+ is required.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Packet capture prerequisites

- **Windows:** Install Npcap from the official Npcap website. Select the WinPcap API-compatible mode if the installer offers it.
- **Ubuntu / Debian:** The DEB package depends on `libpcap0.8`. Packet capture may require elevated permissions. For a packaged install, an administrator may grant capture capabilities with `sudo setcap cap_net_raw,cap_net_admin=eip /opt/netops-toolkit/NetOpsToolkit`. Do not run the entire desktop session as root.
- **macOS:** Allow packet capture access when prompted and ensure the account has the required permissions.

## Project links

- [Source code](https://github.com/Hasan-Gazi-1617/personal-portfolio/tree/main/netops-toolkit)
- [Latest releases](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases)
- [Report an issue](https://github.com/Hasan-Gazi-1617/personal-portfolio/issues)
