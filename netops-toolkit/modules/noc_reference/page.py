"""Searchable, beginner-friendly NOC reference library."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTextBrowser, QSplitter, QApplication,
)


ARTICLES = [
    ("OSI Model", "Fundamentals", "Layer 1 Physical: fiber, copper, optics and signal.\nLayer 2 Data Link: Ethernet, MAC, VLAN, STP.\nLayer 3 Network: IP addressing, routing, ICMP.\nLayer 4 Transport: TCP and UDP ports.\nLayer 5 Session: session establishment and management.\nLayer 6 Presentation: data format, encryption and encoding.\nLayer 7 Application: DNS, HTTP, DHCP, SSH and application protocols.\n\nTroubleshooting tip: start at Layer 1 and move upward. Confirm link, VLAN, IP, route, transport port and application response."),
    ("Common TCP/UDP Ports", "Fundamentals", "20/21 FTP • 22 SSH • 23 Telnet • 25 SMTP • 53 DNS • 67/68 DHCP • 80 HTTP • 110 POP3 • 123 NTP • 143 IMAP • 161/162 SNMP • 179 BGP • 443 HTTPS • 514 Syslog • 1812/1813 RADIUS • 8291 MikroTik WinBox.\n\nA port being open does not prove an application is healthy. Confirm protocol, source/destination and service logs."),
    ("Private IPv4 Ranges", "IP Addressing", "10.0.0.0/8\n172.16.0.0/12\n192.168.0.0/16\n\nCarrier-grade NAT shared range: 100.64.0.0/10. It is not a normal RFC1918 private range. Avoid overlapping customer, management and infrastructure address plans."),
    ("Linux Network Commands", "Linux", "ip addr                 Show interfaces and addresses\nip route                 Show routing table\nip neigh                 Show ARP/neighbor table\nping -c 4 1.1.1.1        Test reachability\ntraceroute example.com   Trace route (install if missing)\nss -tulpn               Show listening sockets\ndig example.com          DNS lookup\ncurl -Iv https://site    Inspect HTTP/TLS response\nethtool eth0             NIC link and speed details\ntcpdump -ni eth0         Capture packets (authorized interfaces only)"),
    ("MikroTik RouterOS Checks", "MikroTik", "/interface print\n/interface ethernet monitor ether1 once\n/ip address print\n/ip route print detail\n/ip dns print\n/ip firewall filter print stats\n/ip firewall nat print stats\n/ppp active print\n/log print where topics~\"error\"\n\nUse read-only checks first. Review the target router and configuration before applying changes."),
    ("VLAN Troubleshooting", "Switching", "1. Confirm VLAN exists on both devices.\n2. Confirm access ports are untagged in the intended VLAN.\n3. Confirm trunk ports carry the VLAN as tagged.\n4. Check PVID/native VLAN consistency.\n5. Check allowed VLAN lists and STP state.\n6. Verify gateway, DHCP scope and routing.\n\nA VLAN mismatch often causes one-way connectivity or DHCP failure."),
    ("GPON / OLT Troubleshooting", "Fiber & GPON", "1. Check OLT chassis, board and PON port status.\n2. Check ONU registration, serial number and last-down reason.\n3. Compare OLT Tx and ONU Rx optical levels with vendor limits.\n4. Inspect connector cleanliness, bends, splitter stages and splices.\n5. Check distance, dying-gasp events and LOS alarms.\n6. Confirm service VLAN, GEM/service-port mapping and PPPoE path.\n\nDo not diagnose optical faults from estimated calculator output alone. Measure the actual signal."),
    ("DNS Troubleshooting", "Diagnostics", "Compare the configured resolver with trusted public resolvers.\nLinux: resolvectl status; dig A example.com; dig AAAA example.com\nWindows: ipconfig /all; nslookup example.com\nCheck NXDOMAIN, SERVFAIL, timeout, stale cache, DNS interception and split-horizon records. Different CDN answers are not automatically a fault."),
    ("TCP Connection Checks", "Diagnostics", "Linux: nc -vz host 443\nWindows PowerShell: Test-NetConnection host -Port 443\nA timeout can mean filtering, routing loss, server silence or an unavailable path. A refused connection means a reachable endpoint rejected the TCP connection. Always compare from another network before assigning an ISP fault."),
    ("Incident Notes / TKI", "NOC Workflow", "Initial Investigation: record customer report and scope.\nTroubleshooting: list checks and observed results.\nRoot Cause: state the evidence-backed cause.\nAction Taken: record exact change or repair.\nVerification: confirm service is restored.\nCustomer Confirmation: record customer feedback.\n\nSeparate confirmed facts from assumptions. Include timestamps, affected service, device/interface and before/after measurements."),
]


class NOCReferencePage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        title = QLabel("NOC Reference Library")
        title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel("Search practical network references, commands and step-by-step troubleshooting notes. Select any topic to read its guide.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search OSI, VLAN, GPON, DNS, MikroTik, Linux commands...")
        self.search.setMinimumHeight(40)
        root.addWidget(self.search)

        split = QSplitter()
        self.list = QListWidget()
        self.detail = QTextBrowser()
        self.detail.setOpenExternalLinks(True)
        split.addWidget(self.list)
        split.addWidget(self.detail)
        split.setSizes([280, 760])
        root.addWidget(split, 1)

        copy_row = QHBoxLayout()
        self.copy = QPushButton("Copy Guide")
        self.clear = QPushButton("Clear Search")
        self.clear.setObjectName("clearButton")
        copy_row.addWidget(self.copy)
        copy_row.addWidget(self.clear)
        copy_row.addStretch()
        root.addLayout(copy_row)

        self.search.textChanged.connect(self._filter)
        self.list.currentItemChanged.connect(self._show)
        self.copy.clicked.connect(self._copy)
        self.clear.clicked.connect(self.search.clear)
        self._filter("")

    def _filter(self, query):
        term = query.lower().strip()
        self.list.clear()
        for title, category, body in ARTICLES:
            if term in title.lower() or term in category.lower() or term in body.lower():
                item = QListWidgetItem(f"{title}  ·  {category}")
                item.setData(256, (title, category, body))
                self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)
        else:
            self.detail.setPlainText("No matching reference found. Try a different keyword.")

    def _show(self, current, previous=None):
        if not current:
            return
        title, category, body = current.data(256)
        self.detail.setPlainText(f"{title}\n{category}\n\n{body}")

    def _copy(self):
        item = self.list.currentItem()
        if item:
            title, category, body = item.data(256)
            QApplication.clipboard().setText(f"{title}\n{category}\n\n{body}")
