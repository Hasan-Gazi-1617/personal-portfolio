"""Visual Website IP, reachability and blocking diagnostics dashboard."""
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
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(12)

        title = QLabel("Website IP & Block Intelligence")
        title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel(
            "Trace reachability from this network, inspect global probes, identify network-path anomalies and review evidence."
        )
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        search = QHBoxLayout()
        self.target = QLineEdit()
        self.target.setPlaceholderText("Enter domain or URL, e.g. example.com")
        self.target.setMinimumHeight(42)
        search.addWidget(self.target, 1)
        search.addWidget(QLabel("Global probes"))
        self.probe_count = QSpinBox()
        self.probe_count.setRange(4, 20)
        self.probe_count.setValue(20)
        self.probe_count.setMinimumHeight(42)
        search.addWidget(self.probe_count)
        self.run_button = QPushButton("Run Full Analysis")
        self.run_button.setMinimumHeight(42)
        search.addWidget(self.run_button)
        self.export_button = QPushButton("Export Report")
        self.export_button.setEnabled(False)
        search.addWidget(self.export_button)
        root.addLayout(search)

        self.status = QLabel("Enter a website and run the analysis.")
        self.status.setObjectName("muted")
        root.addWidget(self.status)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)
        self.cards = {}
        for i, key in enumerate(("Assessment", "Local access", "Resolved IPs", "Global probes")):
            card = QFrame()
            card.setObjectName("panel")
            box = QVBoxLayout(card)
            label = QLabel(key)
            label.setObjectName("muted")
            value = QLabel("—")
            value.setStyleSheet("font-size:20px;font-weight:700")
            value.setWordWrap(True)
            box.addWidget(label)
            box.addWidget(value)
            self.cards[key] = value
            self.cards_grid.addWidget(card, 0, i)
        root.addLayout(self.cards_grid)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.overview = QTextBrowser()
        self.dns_table = self._table(["IP address", "IP version", "Scope"])
        self.tcp_table = self._table(["TCP port", "Result", "Latency", "Details"])
        self.probe_table = self._table(["Country", "City", "Probe ASN", "Probe IP", "Result", "HTTP"])
        self.trace_view = QTextBrowser()
        self.trace_view.setOpenExternalLinks(True)
        self.evidence = QTextBrowser()
        self.evidence.setOpenExternalLinks(True)

        self.tabs.addTab(self.overview, "Overview")
        self.tabs.addTab(self.dns_table, "DNS & IP")
        self.tabs.addTab(self.probe_table, "Global Reachability")
        self.tabs.addTab(self.tcp_table, "TCP Diagnostics")
        self.tabs.addTab(self.trace_view, "Route Trace")
        self.tabs.addTab(self.evidence, "Full Evidence")

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
        for r, values in enumerate(rows):
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                table.setItem(r, c, item)

    def run_analysis(self):
        if self.worker and self.worker.isRunning():
            return
        target = self.target.text().strip()
        if not target:
            self.status.setText("Enter a website domain first.")
            return
        self.run_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.run_button.setText("Analyzing…")
        self.status.setText("Running DNS, RDAP/BGP, HTTP/TLS, TCP, route trace and global probes. This may take a little while.")
        self.worker = Worker(analyze_website_dashboard, target, 443, self.probe_count.value())
        self.worker.done.connect(self.show_result)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(self.finish)
        self.worker.start()

    def finish(self):
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Full Analysis")

    def show_error(self, error):
        self.status.setText("Analysis failed: " + str(error))

    def show_result(self, data):
        self.last_result = data
        report = data.get("report", "")
        probes = self._parse_probes(report)
        reachable = sum(1 for p in probes if p[4] == "HTTP RESPONSE")
        failed = sum(1 for p in probes if p[4] == "UNREACHABLE")
        pending = len(probes) - reachable - failed
        local_ok = bool(re.search(r"HTTPS: HTTP (?!4\d\d|5\d\d)\d{3}", report))
        assessment = "INCONCLUSIVE"
        if "HTTP POLICY RESPONSE" in report:
            assessment = "POLICY RESPONSE"
        elif failed and reachable:
            assessment = "MIXED RESULTS"
        elif reachable and not failed:
            assessment = "NO BLOCK SIGNAL"
        self.cards["Assessment"].setText(assessment)
        self.cards["Local access"].setText("HTTPS reachable" if local_ok else "Check required")
        self.cards["Resolved IPs"].setText(str(len(data.get("addresses", []))))
        self.cards["Global probes"].setText(f"{reachable} OK / {failed} failed / {pending} pending")
        self.status.setText(f"Analysis complete for {data.get('host')} • {data.get('analysis_time')}")

        ip_rows = []
        for address in data.get("addresses", []):
            version = "IPv6" if ":" in address else "IPv4"
            scope = "Global" if ipaddress.ip_address(address).is_global else "Private / reserved"
            ip_rows.append((address, version, scope))
        self._fill(self.dns_table, ip_rows)
        self._fill(self.probe_table, probes)
        tcp_rows = []
        for item in data.get("tcp", []):
            tcp_rows.append((item["port"], item["status"], (str(item["latency_ms"]) + " ms") if item["latency_ms"] is not None else "—", item["detail"]))
        self._fill(self.tcp_table, tcp_rows)

        trace = data.get("trace", {})
        trace_html = (
            f"<h2>Route trace to {html.escape(data.get('host',''))}</h2>"
            f"<p><b>Utility:</b> {html.escape(trace.get('command','Unavailable'))}</p>"
            f"<p>{html.escape(trace.get('output','No trace data'))}</p>"
            "<hr><p><b>How to read:</b> Each numbered hop is a router along the path. "
            "A * or timeout means that hop did not reply to the probe. It does not automatically mean traffic is blocked; "
            "routers often suppress traceroute responses.</p>"
        )
        self.trace_view.setHtml(trace_html)
        self.overview.setHtml(self._overview_html(data, report, reachable, failed, assessment))
        evidence_text = report + "\n\n[LOCAL TCP PORT DIAGNOSTICS]\n"
        for item in data.get("tcp", []):
            evidence_text += (
                f"Port {item['port']}: {item['status']} | "
                f"Latency: {item['latency_ms']} ms | {item['detail']}\n"
            )
        evidence_text += "\n[LOCAL ROUTE TRACE]\n"
        evidence_text += trace.get("output", "Route trace unavailable")
        self.evidence.setPlainText(evidence_text)
        self.export_button.setEnabled(True)

    def _parse_probes(self, report):
        rows = []
        pattern = re.compile(
            r"^\s{2}(.+?)\s*/\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\S+)\s*\|\s*(HTTP RESPONSE|UNREACHABLE|PENDING)\s*\|\s*(.*)$"
        )
        for line in report.splitlines():
            match = pattern.match(line)
            if match:
                country, city, asn, ip, status, detail = match.groups()
                code = re.search(r"HTTP (\d{3})", detail)
                rows.append((country, city, asn, ip, status, code.group(1) if code else detail))
        return rows

    def _overview_html(self, data, report, reachable, failed, assessment):
        host = html.escape(data.get("host", ""))
        color = "#16a34a" if assessment == "NO BLOCK SIGNAL" else "#d97706"
        excerpt = []
        for line in report.splitlines():
            if any(key in line for key in ("DNS interpretation:", "MIXED GLOBAL RESULT:", "POSSIBLE NETWORK-PATH", "GLOBAL CONNECTIVITY FAILURE", "HTTP POLICY RESPONSE:", "Assessment:")):
                excerpt.append(html.escape(line.strip()))
        items = "".join(f"<li>{line}</li>" for line in excerpt) or "<li>Review the evidence tabs for detailed findings.</li>"
        return f"""
        <h2>{host}</h2>
        <h3 style="color:{color}">{html.escape(assessment)}</h3>
        <p><b>Local network:</b> {'HTTPS connection succeeded.' if 'HTTPS: HTTP 200' in report or 'HTTPS: HTTP 301' in report else 'Local HTTPS needs review.'}</p>
        <p><b>Global probes:</b> {reachable} HTTP responses, {failed} unreachable.</p>
        <h3>What this means</h3>
        <p>The website is tested from your current computer and from third-party probe locations. A failed remote probe identifies a reachability problem at that probe, not necessarily an ISP block.</p>
        <h3>Key findings</h3><ul>{items}</ul>
        <h3>Where might the failure occur?</h3>
        <ol>
          <li><b>DNS:</b> name-to-IP resolution may be blocked or altered.</li>
          <li><b>Network path:</b> route trace may show where replies stop, but silent hops are not proof of a drop.</li>
          <li><b>TCP port:</b> a timeout or reset may indicate filtering, routing trouble or an unavailable service.</li>
          <li><b>TLS / HTTP:</b> certificate errors or HTTP 403/451 responses can point to TLS or website/CDN policy.</li>
        </ol>
        <p><b>Important:</b> Exact ISP blocking can only be confirmed with repeatable tests from that ISP or filtering evidence from its network.</p>
        """

    def export_report(self):
        if not self.last_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export website diagnostic report",
            f"{self.last_result.get('host','website')}-netops-report.txt",
            "Text report (*.txt)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(self.last_result.get("report", ""))
                    handle.write("\n\n[LOCAL TCP DIAGNOSTICS]\n")
                    for item in self.last_result.get("tcp", []):
                        handle.write(str(item) + "\n")
                    handle.write("\n[ROUTE TRACE]\n")
                    handle.write(self.last_result.get("trace", {}).get("output", "Unavailable"))
                QMessageBox.information(self, "Export complete", "Report saved successfully.")
            except OSError as exc:
                QMessageBox.critical(self, "Export failed", str(exc))
