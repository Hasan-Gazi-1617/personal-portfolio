from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QLabel, QPushButton, QStackedWidget, QLineEdit, QSpinBox, QTextEdit,
    QGridLayout, QComboBox, QSizePolicy
)
from core.network_info import snapshot
from core.worker import Worker
from modules.diagnostics.ping import ping
from modules.ip_calculator.page import IPCalculatorPage
from modules.network_analyzer.page import NetworkAnalyzerPage
from modules.network_analyzer.pcap_page import PCAPInspectorPage
from modules.website_analyzer.page import WebsiteAnalyzerPage
from modules.fiber_olt.page import FiberOLTPage
from modules.bandwidth.page import BandwidthPage
from modules.noc_reference.page import NOCReferencePage


PORTFOLIO_URL = "https://personal-portfolio-069p.onrender.com/"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetOps Toolkit | Developed by Hasan")
        self.resize(1480, 940)
        self.setMinimumSize(1120, 760)
        self.theme = "dark"
        self.worker = None

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 22, 16, 18)
        brand = QLabel("NETWORK OPS")
        brand.setObjectName("brand")
        side.addWidget(brand)
        subtitle = QLabel("ENGINEERING WORKSPACE")
        subtitle.setObjectName("muted")
        side.addWidget(subtitle)
        side.addSpacing(22)

        self.stack = QStackedWidget()
        self.nav = []
        pages = [
            ("Dashboard", self.dashboard),
            ("Network Analyzer", NetworkAnalyzerPage),
            ("PCAP File Inspector", PCAPInspectorPage),
            ("Website Block Detection", WebsiteAnalyzerPage),
            ("Ping Test", self.ping_page),
            ("IP Calculator", IPCalculatorPage),
            ("Fiber & OLT Tools", FiberOLTPage),
            ("Bandwidth & Unit Converter", BandwidthPage),
            ("NOC Reference Library", NOCReferencePage),
        ]
        for name, builder in pages:
            button = QPushButton(name)
            button.setCheckable(True)
            button.setChecked(not self.nav)
            button.setMinimumHeight(42)
            button.clicked.connect(lambda checked=False, n=name: self.open_page(n))
            side.addWidget(button)
            self.nav.append((name, button))
            self.stack.addWidget(builder())

        side.addStretch()
        self.theme_btn = QPushButton("Switch to Light Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        side.addWidget(self.theme_btn)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 16, 24, 22)
        content_layout.setSpacing(16)

        header = QGridLayout()
        header.setColumnStretch(0, 1)
        header.setColumnStretch(1, 2)
        header.setColumnStretch(2, 1)
        left_spacer = QLabel("")
        header.addWidget(left_spacer, 0, 0)

        heading = QLabel("NetOps Toolkit")
        heading.setObjectName("appHeaderTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(heading, 0, 1)

        credit = QWidget()
        credit_layout = QHBoxLayout(credit)
        credit_layout.setContentsMargins(0, 0, 0, 0)
        credit_layout.setSpacing(10)
        developed = QLabel("Developed by Hasan")
        developed.setObjectName("muted")
        portfolio = QPushButton("Check My Portfolio")
        portfolio.setObjectName("portfolioLink")
        portfolio.setCursor(Qt.CursorShape.PointingHandCursor)
        portfolio.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(PORTFOLIO_URL)))
        credit_layout.addWidget(developed)
        credit_layout.addWidget(portfolio)
        header.addWidget(credit, 0, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        content_layout.addLayout(header)

        divider = QFrame()
        divider.setObjectName("headerDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        content_layout.addWidget(divider)

        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.stack, 1)

        root.addWidget(sidebar)
        root.addWidget(content, 1)
        self.setCentralWidget(central)
        self.apply_theme()

    def panel(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        return frame

    def dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        title = QLabel("Network Overview")
        title.setObjectName("title")
        layout.addWidget(title)
        info = snapshot()
        grid = QGridLayout()
        values = [
            ("Hostname", info["hostname"]),
            ("Local IP", info["ip"]),
            ("Operating System", info["os"]),
            ("Interfaces", str(len(info["interfaces"]))),
        ]
        for index, (key, value) in enumerate(values):
            card = self.panel()
            label = QLabel(key)
            label.setObjectName("muted")
            val = QLabel(value)
            val.setStyleSheet("font-size:17px;font-weight:700")
            val.setWordWrap(True)
            card.layout().addWidget(label)
            card.layout().addWidget(val)
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        section = QLabel("Detected network interfaces")
        section.setObjectName("muted")
        layout.addWidget(section)
        for item in info["interfaces"]:
            layout.addWidget(QLabel(
                f'{item["name"]}  |  IPv4: {item["ipv4"]}  |  MAC: {item["mac"]}'
            ))
        layout.addStretch()
        return widget

    def tool_page(self, title, description, placeholder, function, button_text,
                  with_count=False, with_family=False):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        heading = QLabel(title)
        heading.setObjectName("title")
        layout.addWidget(heading)
        desc = QLabel(description)
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        row = QHBoxLayout()
        entry = QLineEdit()
        entry.setMinimumHeight(42)
        entry.setPlaceholderText(placeholder)
        row.addWidget(entry, 1)

        count = None
        if with_count:
            count = QSpinBox()
            count.setRange(1, 1000)
            count.setValue(4)
            count.setMinimumHeight(42)
            count.setToolTip("Number of echo requests to send")
            row.addWidget(QLabel("Ping Count"))
            row.addWidget(count)

        family = None
        if with_family:
            family = QComboBox()
            family.addItems(["Auto", "IPv4", "IPv6"])
            row.addWidget(family)

        run_button = QPushButton(button_text)
        clear_button = QPushButton("Clear All")
        clear_button.setObjectName("clearButton")
        row.addWidget(run_button)
        row.addWidget(clear_button)
        layout.addLayout(row)

        output = QTextEdit()
        output.setReadOnly(True)
        output.setPlaceholderText("Results will appear here...")
        layout.addWidget(output, 1)

        def clear():
            if self.worker and self.worker.isRunning():
                return
            entry.clear()
            output.clear()
            if count:
                count.setValue(4)
            if family:
                family.setCurrentIndex(0)
            run_button.setEnabled(True)
            run_button.setText(button_text)

        def run():
            if self.worker and self.worker.isRunning():
                return
            target = entry.text().strip()
            if not target:
                output.setPlainText("Enter a target before starting the test.")
                return
            run_button.setEnabled(False)
            clear_button.setEnabled(False)
            args = [target]
            if with_count:
                args.append(count.value())
            if with_family:
                args.append(family.currentText())
            if title.startswith("Website"):
                args.extend([443, 20])
            output.setPlainText("Running diagnostics. Please wait...")
            self.worker = Worker(function, *args)

            def show_result(result):
                output.setPlainText(str(result))

            self.worker.done.connect(show_result)
            self.worker.failed.connect(lambda error: show_result("Error: " + error))

            def finish():
                run_button.setEnabled(True)
                clear_button.setEnabled(True)
                run_button.setText("Run Again")

            self.worker.finished.connect(finish)
            self.worker.start()

        clear_button.clicked.connect(clear)
        run_button.clicked.connect(run)
        entry.returnPressed.connect(run)
        return widget

    def ping_page(self):
        return self.tool_page(
            "Ping Test",
            "Test a hostname or IP from this computer. Choose request count and IPv4/IPv6 mode.",
            "1.1.1.1 or example.com",
            ping,
            "Run Ping",
            with_count=True,
            with_family=True,
        )

    def open_page(self, name):
        for index, (item, button) in enumerate(self.nav):
            button.setChecked(item == name)
            if item == name:
                self.stack.setCurrentIndex(index)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        path = Path(__file__).parent / "themes" / f"{self.theme}.qss"
        self.setStyleSheet(path.read_text(encoding="utf-8"))
        self.theme_btn.setText(
            "Switch to Light Theme" if self.theme == "dark" else "Switch to Dark Theme"
        )

    def closeEvent(self, event):
        analyzer = self.stack.widget(1)
        if hasattr(analyzer, "capture"):
            analyzer.capture.stop()
        super().closeEvent(event)
