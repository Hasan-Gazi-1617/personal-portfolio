"""Simple, evidence-led Website Block Checker dashboard."""
import html
import ipaddress
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QTabWidget, QFrame, QGridLayout, QTextBrowser, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView
)
from core.worker import Worker
from modules.website_analyzer.lookup import analyze_website_dashboard


class WebsiteAnalyzerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.last_result = None
        self.diagnosis = None

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(10)

        title = QLabel("Website Network Block Checker")
        title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel(
            "Main question: Can this website be opened from your current network? "
            "If not, identify the type of failure and show the network path."
        )
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        search = QHBoxLayout()
        self.target = QLineEdit()
        self.target.setPlaceholderText("Enter website, e.g. example.com")
        self.target.setMinimumHeight(44)
        search.addWidget(self.target, 1)
        search.addWidget(QLabel("Global checks"))
        self.probe_count = QSpinBox()
        self.probe_count.setRange(4, 20)
        self.probe_count.setValue(12)
        self.probe_count.setMinimumHeight(44)
        search.addWidget(self.probe_count)
        self.run_button = QPushButton("Check Website")
        self.run_button.setMinimumHeight(44)
        search.addWidget(self.run_button)
        self.export_button = QPushButton("Export")
        self.export_button.setEnabled(False)
        search.addWidget(self.export_button)
        root.addLayout(search)

        self.status = QLabel("Enter a website and click Check Website.")
        self.status.setObjectName("muted")
        root.addWidget(self.status)

        verdict_card = QFrame()
        verdict_card.setObjectName("panel")
        verdict_layout = QVBoxLayout(verdict_card)
        verdict_layout.setContentsMargins(18, 16, 18, 16)
        verdict_header = QHBoxLayout()
        verdict_header.addWidget(QLabel("FINAL RESULT FOR YOUR NETWORK"))
        verdict_header.addStretch()
        self.verdict_badge = QLabel("NOT TESTED")
        self.verdict_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verdict_badge.setStyleSheet(
            "font-weight:700;padding:6px 12px;border-radius:8px;background:#64748b;color:white"
        )
        verdict_header.addWidget(self.verdict_badge)
        verdict_layout.addLayout(verdict_header)
        self.verdict_title = QLabel("Is this website blocked on my network?")
        self.verdict_title.setStyleSheet("font-size:23px;font-weight:800")
        self.verdict_title.setWordWrap(True)
        verdict_layout.addWidget(self.verdict_title)
        self.verdict_detail = QLabel(
            "Run a check to get a clear answer. The tool will not label a timeout as a confirmed block."
        )
        self.verdict_detail.setWordWrap(True)
        self.verdict_detail.setObjectName("muted")
        verdict_layout.addWidget(self.verdict_detail)
        root.addWidget(verdict_card)

        self.summary_grid = QGridLayout()
        self.summary_grid.setSpacing(8)
        self.summary_values = {}
        for i, key in enumerate(("DNS", "TCP 443", "HTTPS / TLS", "Global checks")):
            card = QFrame()
            card.setObjectName("panel")
            layout = QVBoxLayout(card)
            label = QLabel(key)
            label.setObjectName("muted")
            value = QLabel("Not tested")
            value.setStyleSheet("font-size:16px;font-weight:700")
            value.setWordWrap(True)
            layout.addWidget(label)
            layout.addWidget(value)
            self.summary_values[key] = value
            self.summary_grid.addWidget(card, 0, i)
        root.addLayout(self.summary_grid)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self.path_view = QTextBrowser()
        self.path_view.setOpenExternalLinks(True)
        self.location_view = QTextBrowser()
        self.location_view.setOpenExternalLinks(True)
        self.details = QTextBrowser()
        self.details.setOpenExternalLinks(True)
        self.trace_table = self._table(["Hop", "Router / IP", "What it means"])
        trace_tab = QWidget()
        trace_layout = QVBoxLayout(trace_tab)
        trace_layout.addWidget(QLabel(
            "A silent hop means no traceroute reply. It is not proof that the router blocks the website."
        ))
        trace_layout.addWidget(self.trace_table, 1)

        self.tabs.addTab(self.path_view, "Simple Diagnosis")
        self.tabs.addTab(self.location_view, "Where is the problem?")
        self.tabs.addTab(trace_tab, "Network Path")
        self.tabs.addTab(self.details, "Technical Details")

        self.run_button.clicked.connect(self.run_analysis)
        self.target.returnPressed.connect(self.run_analysis)
        self.export_button.clicked.connect(self.export_report)

    def _table(self, headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _fill(self, table, rows):
        table.setRowCount(len(rows))
        for row_index, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                table.setItem(row_index, column, item)

    def run_analysis(self):
        if self.worker and self.worker.isRunning():
            return
        target = self.target.text().strip()
        if not target:
            self.status.setText("Please enter a website first.")
            return
        self.run_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.run_button.setText("Checking…")
        self.status.setText("Checking your DNS, website connection, HTTPS and network path…")
        self.worker = Worker(analyze_website_dashboard, target, 443, self.probe_count.value())
        self.worker.done.connect(self.show_result)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(self.finish)
        self.worker.start()

    def finish(self):
        self.run_button.setEnabled(True)
        self.run_button.setText("Check Website")

    def show_error(self, error):
        self.verdict_badge.setText("CHECK FAILED")
        self.verdict_title.setText("Could not complete the website check")
        self.verdict_detail.setText(str(error))
        self.status.setText("Check failed. Verify the domain and your Internet connection.")

    def _probe_rows(self, report):
        rows = []
        pattern = re.compile(
            r"^\s{2}(.+?)\s*/\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\S+)\s*\|\s*(HTTP RESPONSE|UNREACHABLE|PENDING)\s*\|\s*(.*)$"
        )
        for line in report.splitlines():
            match = pattern.match(line)
            if match:
                country, city, asn, ip, status, detail = match.groups()
                code = re.search(r"HTTP (\d{3})", detail)
                rows.append({
                    "country": country, "city": city, "asn": asn, "ip": ip,
                    "status": status, "detail": detail,
                    "code": int(code.group(1)) if code else None,
                })
        return rows

    def _diagnose(self, data):
        report = data.get("report", "")
        tcp = {int(row["port"]): row for row in data.get("tcp", [])}
        probes = self._probe_rows(report)
        https = re.search(r"HTTPS:\s*HTTP\s+(\d{3})", report, re.I)
        https_failed = re.search(r"HTTPS:\s*Connection failed", report, re.I)
        http = re.search(r"HTTP:\s*HTTP\s+(\d{3})", report, re.I)
        dns_ok = bool(data.get("addresses"))
        tcp443 = tcp.get(443, {}).get("status", "NOT TESTED")
        code = int(https.group(1)) if https else (int(http.group(1)) if http else None)
        successful_global = sum(1 for p in probes if p["status"] == "HTTP RESPONSE" and p["code"] not in (401, 403, 451))
        global_policy = sum(1 for p in probes if p["code"] in (401, 403, 451))

        if code is not None and 200 <= code < 400:
            verdict = "NOT BLOCKED"
            title = "Website is reachable from your network"
            detail = f"Your network received HTTP {code}. A successful HTTP response or redirect means the website endpoint responded."
            color = "#16a34a"
            local_state = f"HTTP {code}"
        elif code in (401, 403, 451):
            verdict = "POLICY RESPONSE"
            title = f"Website responded with HTTP {code}"
            detail = "A server, CDN, WAF or intermediary refused this request. This does not prove your ISP is the blocker."
            color = "#d97706"
            local_state = f"HTTP {code}"
        elif code is not None and code >= 500:
            verdict = "SERVER ERROR"
            title = f"Website responded with HTTP {code}"
            detail = "Your request reached an HTTP service, but the service returned a server error. This is not evidence of ISP blocking."
            color = "#d97706"
            local_state = f"HTTP {code}"
        elif code is not None:
            verdict = "REACHABLE (HTTP ERROR)"
            title = f"Website responded with HTTP {code}"
            detail = "The website endpoint returned an HTTP response, so the network path reached an HTTP service. This response alone does not mean the ISP blocked it."
            color = "#16a34a"
            local_state = f"HTTP {code}"
        elif not dns_ok:
            verdict = "WEBSITE NOT OPENING"
            title = "Website name could not be found on this network"
            detail = "Your device could not resolve this website. This may be a DNS outage or DNS filtering. The tool cannot yet confirm that your ISP blocked it."
            color = "#d97706"
            local_state = "DNS lookup failed"
        elif tcp443 == "OPEN":
            verdict = "WEBSITE NOT OPENING"
            title = "Website is not opening, but the connection reaches its port"
            detail = "Your network can reach TCP port 443, but the HTTPS request did not finish. This points to a TLS, CDN, server or application problem. ISP blocking is not confirmed."
            color = "#d97706"
            local_state = "Port open; HTTPS failed"
        elif tcp443 in ("FILTERED / TIMEOUT", "UNREACHABLE"):
            if successful_global >= 2:
                verdict = "POSSIBLE NETWORK BLOCK"
                title = "Website fails here but works from other locations"
                detail = "This is a possible local-network or ISP-path block. It could also be a routing problem. Compare with a second ISP and check ISP filtering logs before confirming."
                color = "#d97706"
            else:
                verdict = "WEBSITE NOT OPENING"
                title = "Website could not be reached from this network"
                detail = "The connection failed. A block, routing issue, remote outage or firewall can cause this. Current evidence does not identify which one."
                color = "#d97706"
            local_state = tcp443
        else:
            verdict = "WEBSITE NOT OPENING"
            title = "Website could not be opened from this network"
            detail = "The website did not return a usable response. The exact cause needs further comparison tests."
            color = "#d97706"
            local_state = "Connection needs checking"

        location = "Not confirmed"
        location_reason = "The current tests cannot identify a specific router or ISP device as the blocking point."
        if verdict == "POSSIBLE NETWORK BLOCK":
            location_reason = "The website works from other probe locations but not from this network. The exact point (device, router, ISP, upstream or destination) is not confirmed."
        elif verdict == "POLICY RESPONSE":
            location_reason = "The HTTP refusal came from the website, CDN, WAF or an intermediary. The responding component's identity is not established."
        elif not dns_ok:
            location_reason = "The failure is at the name-resolution stage. Check the configured DNS server and compare public resolver answers."

        return {
            "verdict": verdict, "title": title, "detail": detail, "color": color,
            "local_state": local_state, "dns_ok": dns_ok, "tcp443": tcp443,
            "https_state": f"HTTP {code}" if code is not None else ("Handshake / request failed" if https_failed else "No HTTP response"),
            "global_ok": successful_global, "global_policy": global_policy,
            "global_failed": sum(1 for p in probes if p["status"] == "UNREACHABLE"),
            "location": location, "location_reason": location_reason,
            "probes": probes,
        }

    def show_result(self, data):
        self.last_result = data
        diagnosis = self._diagnose(data)
        self.diagnosis = diagnosis
        self.verdict_badge.setText(diagnosis["verdict"])
        self.verdict_badge.setStyleSheet(
            f"font-weight:700;padding:6px 12px;border-radius:8px;background:{diagnosis['color']};color:white"
        )
        self.verdict_title.setText(diagnosis["title"])
        self.verdict_detail.setText(diagnosis["detail"])
        self.summary_values["DNS"].setText("Resolved" if diagnosis["dns_ok"] else "Failed")
        self.summary_values["TCP 443"].setText(diagnosis["tcp443"])
        self.summary_values["HTTPS / TLS"].setText(diagnosis["https_state"])
        self.summary_values["Global checks"].setText(
            f"{diagnosis['global_ok']} responded / {diagnosis['global_failed']} failed"
        )
        self.status.setText(f"Completed: {data.get('host')}  •  {data.get('analysis_time')}")

        dns_rows = [
            ("DNS", "PASS" if diagnosis["dns_ok"] else "FAIL", "Website name resolved to IP addresses"),
            ("TCP port 443", diagnosis["tcp443"], "Connection test from this computer"),
            ("HTTPS / TLS", diagnosis["https_state"], "Secure website request result"),
            ("Global probes", f"{diagnosis['global_ok']} responded", "Third-party locations only; not a substitute for testing your ISP"),
        ]
        self.path_view.setHtml(self._simple_html(data, diagnosis, dns_rows))
        self.location_view.setHtml(self._location_html(diagnosis))
        trace = data.get("trace", {})
        hop_rows = []
        for line in trace.get("hops", []):
            parts = line.strip().split(maxsplit=1)
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            hop, address = parts
            silent = "*" in address or "timed out" in address.lower() or "timeout" in address.lower()
            hop_rows.append((hop, address, "No reply; not proof of blocking" if silent else "Router replied to traceroute"))
        self._fill(self.trace_table, hop_rows)
        self.details.setPlainText(self._technical_report(data, diagnosis))
        self.export_button.setEnabled(True)

    def _simple_html(self, data, d, rows):
        host = html.escape(data.get("host", ""))
        steps = [
            ("1. Your device", "Test started from this computer", "ok"),
            ("2. DNS lookup", "Website name found" if d["dns_ok"] else "Website name not found", "ok" if d["dns_ok"] else "bad"),
            ("3. TCP connection", f"Port 443: {d['tcp443']}", "ok" if d["tcp443"] == "OPEN" else "warn"),
            ("4. HTTPS request", d["https_state"], "ok" if d["https_state"].startswith("HTTP ") else "warn"),
            ("5. Website response", d["title"], "ok" if d["verdict"] in ("NOT BLOCKED", "REACHABLE (HTTP ERROR)") else "warn"),
        ]
        colors = {"ok": "#16a34a", "warn": "#d97706", "bad": "#dc2626"}
        flow = "".join(
            f"<div style='padding:10px;margin:7px 0;border-left:5px solid {colors[state]};background:rgba(127,127,127,.08);border-radius:5px'>"
            f"<b>{label}</b><br>{html.escape(value)}</div>"
            for label, value, state in steps
        )
        return (
            f"<h2>{host}</h2><p><b>Simple result:</b> {html.escape(d['verdict'])}</p>"
            f"{flow}<h3>What should I understand?</h3><p>{html.escape(d['detail'])}</p>"
            "<p><b>Remember:</b> A failed connection does not automatically mean your ISP blocked the site. "
            "The exact blocking point is shown only when evidence supports it.</p>"
        )

    def _location_html(self, d):
        return (
            f"<h2>Where could the problem be?</h2><h3>{html.escape(d['location'])}</h3>"
            f"<p>{html.escape(d['location_reason'])}</p>"
            "<h3>Check these points in order</h3><ol>"
            "<li><b>Your device:</b> VPN, proxy, firewall or security software.</li>"
            "<li><b>Your router:</b> DNS, firewall or access-control rules.</li>"
            "<li><b>Your ISP:</b> DNS filtering, firewall, routing or policy rules.</li>"
            "<li><b>Upstream provider:</b> routing or peering path.</li>"
            "<li><b>Website server / CDN:</b> outage, security policy or TLS problem.</li>"
            "</ol><p><b>Current finding:</b> the tests do not identify a specific device as the blocker. "
            "Do not treat a silent traceroute hop as a confirmed block point.</p>"
        )

    def _technical_report(self, data, d):
        lines = [
            "WEBSITE NETWORK BLOCK CHECK",
            f"Website: {data.get('host')}",
            f"Final verdict: {d['verdict']}",
            f"Explanation: {d['detail']}",
            f"Blocking location: {d['location']}",
            f"Location note: {d['location_reason']}",
            "",
            "LOCAL TCP TESTS",
        ]
        for item in data.get("tcp", []):
            lines.append(
                f"Port {item['port']}: {item['status']} | "
                f"Latency: {item['latency_ms']} ms | {item['detail']}"
            )
        lines.extend(["", "FULL ORIGINAL DIAGNOSTIC REPORT", data.get("report", "")])
        lines.extend(["", "LOCAL ROUTE TRACE", data.get("trace", {}).get("output", "Unavailable")])
        return "\n".join(lines)

    def export_report(self):
        if not self.last_result:
            return
        host = self.last_result.get("host", "website")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export website check",
            f"{host}-block-check.txt", "Text report (*.txt)"
        )
        if path:
            try:
                self.details.toPlainText()
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(self._technical_report(self.last_result, self.diagnosis))
                QMessageBox.information(self, "Export complete", "Website check report saved.")
            except OSError as exc:
                QMessageBox.critical(self, "Export failed", str(exc))
