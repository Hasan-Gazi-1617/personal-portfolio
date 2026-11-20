# NetOps Toolkit

Cross-platform desktop network operations and diagnostics toolkit built with Python and PySide6.

## Features

- **Network Analyzer:** Wireshark-inspired live packet capture, interface selection, BPF capture filters, protocol/IP/port display filters, decoded packet details and PCAP export.
- **Website IP & Block Detection:** Enter only a website domain or URL. The tool automatically discovers IPv4/IPv6 addresses, looks up RDAP allocation ranges and CIDR summaries, retrieves BGP-announced prefixes and ASN/organization/country data where available, checks local HTTP/HTTPS reachability, inspects the TLS certificate, and compares HTTP reachability from independent global probe nodes. Probe country, city, IP and ASN are shown when supplied by the probe provider.
- **Ping Test:** User-configurable request count (1-1000), automatic/IPv4/IPv6 mode and raw platform ping output.
- **IP Calculator:** IPv4 and IPv6 subnet calculation, prefix slider, subnet splitting, address ranges, masks and copy actions.
- Dark and light themes. Every diagnostic module includes a **Clear All** action.

## Website analysis: important interpretation

- The Website IP & Block Detection page needs only a domain such as `example.com` or a URL such as `https://example.com`; port and probe count are internal defaults.
- DNS answers can vary by resolver, region, CDN, time and client network. The IP list is the answer visible from the computer running NetOps Toolkit.
- RDAP allocation ranges describe registry allocation. BGP prefixes describe routed announcements. They are different and neither one proves that an IP range is blocked.
- Global reachability checks use third-party probe nodes. The app displays the country/city/ASN returned by the provider; it cannot test every ISP or every network in a country.
- A failed probe is **not proof of ISP blocking**. DNS, routing, firewall, TLS, server policy, geo restrictions and probe-node availability can all affect results. Repeated failures from probes sharing an ASN while other networks succeed are an anomaly to investigate, not a definitive block verdict.
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
