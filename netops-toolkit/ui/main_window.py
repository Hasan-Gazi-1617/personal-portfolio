from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QLabel, QPushButton, QStackedWidget, QLineEdit, QSpinBox, QTextEdit,
    QGridLayout, QComboBox
)
from core.network_info import snapshot
from core.worker import Worker
from modules.diagnostics.ping import ping
from modules.ip_calculator.page import IPCalculatorPage
from modules.network_analyzer.page import NetworkAnalyzerPage
from modules.website_analyzer.page import WebsiteAnalyzerPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetOps Toolkit")
        self.resize(1280, 820)
        self.setMinimumSize(980, 680)
        self.theme = "dark"
        self.worker = None

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 22, 16, 18)
        brand = QLabel("NetOps Toolkit")
        brand.setObjectName("brand")
        side.addWidget(brand)
        subtitle = QLabel("NETWORK OPERATIONS")
        subtitle.setObjectName("muted")
        side.addWidget(subtitle)
        side.addSpacing(22)

        self.stack = QStackedWidget()
        self.nav = []
        pages = [
            ("Dashboard", self.dashboard),
            ("Network Analyzer", NetworkAnalyzerPage),
            ("Website Network Block Checker", WebsiteAnalyzerPage),
            ("Ping Test", self.ping_page),
            ("IP Calculator", IPCalculatorPage),
        ]
        for name, builder in pages:
            button = QPushButton(name)
            button.setCheckable(True)
            button.setChecked(not self.nav)
            button.clicked.connect(lambda checked=False, n=name: self.open_page(n))
            side.addWidget(button)
            self.nav.append((name, button))
            self.stack.addWidget(builder())

        side.addStretch()
        self.theme_btn = QPushButton("Switch to Light Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        side.addWidget(self.theme_btn)
        credit = QLabel("Developed by Hasan Gazi")
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit.setStyleSheet("color:#8b95a5;font-size:11px;padding-top:10px")
        side.addWidget(credit)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 24)
        heading = QLabel("Monitor  •  Analyze  •  Diagnose")
        heading.setObjectName("muted")
        content_layout.addWidget(heading)
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
            "Set the request count yourself and test a hostname or IP using automatic, IPv4 or IPv6 mode.",
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
