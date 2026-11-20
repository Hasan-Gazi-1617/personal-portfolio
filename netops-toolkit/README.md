# NetOps Toolkit

Cross-platform desktop network operations and diagnostics toolkit built with Python and PySide6.

## Features

- **Network Analyzer:** Wireshark-inspired live packet capture, interface selection, BPF capture filters, protocol/IP/port display filters, decoded packet details and PCAP export.
- **Website IP & Block Detection:** A/AAAA resolution, RDAP allocation range and CIDR summary, registry network information, ASN/provider details where published, and HTTP reachability checks from independent global probe locations.
- **Ping Test:** User-configurable request count (1-1000), automatic/IPv4/IPv6 mode and raw platform ping output.
- **IP Calculator:** IPv4 and IPv6 subnet calculation, prefix slider, subnet splitting, address ranges, masks and copy actions.
- Dark and light themes. Every diagnostic module includes a **Clear All** action.

## Important notes

- Packet capture requires suitable privileges and packet-capture support. Windows requires Npcap; Linux generally requires libpcap and capture permissions; macOS requires packet-capture permissions.
- Global website tests use third-party probe nodes. A failed probe is **not proof of ISP blocking**. DNS, routing, firewall, TLS, server policy, probe-node availability and regional differences can all affect results.
- RDAP allocation ranges are registry allocation data. They are not guaranteed to be the exact BGP-announced route prefix.
- The application does not claim to identify every ISP in a country. Results show the actual probe locations and ASNs returned by the provider.
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
.venv\Scripts\Activate.ps1
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
