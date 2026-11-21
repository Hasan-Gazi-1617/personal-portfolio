"""Bandwidth, data-rate, storage and traffic calculators."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QPushButton, QFrame, QDoubleSpinBox, QSpinBox,
)


# All factors are expressed as bits per second (decimal SI units).
RATE_UNITS = {
    "bps": 1, "Kbps": 1_000, "Mbps": 1_000_000,
    "Gbps": 1_000_000_000, "Tbps": 1_000_000_000_000,
    "KB/s": 8_000, "MB/s": 8_000_000, "GB/s": 8_000_000_000,
}


class BandwidthPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _number(self, value, maximum=1e15):
        field = QDoubleSpinBox()
        field.setRange(0, maximum)
        field.setDecimals(4)
        field.setValue(value)
        field.setMinimumHeight(40)
        return field

    def _build(self):
        root = QVBoxLayout(self)
        title = QLabel("Bandwidth & Unit Converter")
        title.setObjectName("title")
        root.addWidget(title)
        intro = QLabel("Convert network speed and byte throughput, estimate download time, calculate shared capacity and project monthly traffic.")
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        rate_panel = QFrame()
        rate_panel.setObjectName("panel")
        rate = QGridLayout(rate_panel)
        self.rate_value = self._number(100)
        self.rate_from = QComboBox()
        self.rate_from.addItems(list(RATE_UNITS))
        self.rate_to = QComboBox()
        self.rate_to.addItems(list(RATE_UNITS))
        self.rate_to.setCurrentText("Mbps")
        self.rate_output = QLabel("100 Mbps")
        self.rate_output.setObjectName("resultValue")
        self.rate_output.setWordWrap(True)
        rate.addWidget(QLabel("Network speed / throughput"), 0, 0)
        rate.addWidget(QLabel("From"), 0, 1)
        rate.addWidget(QLabel("To"), 0, 2)
        rate.addWidget(self.rate_value, 1, 0)
        rate.addWidget(self.rate_from, 1, 1)
        rate.addWidget(self.rate_to, 1, 2)
        self.rate_button = QPushButton("Convert Speed")
        rate.addWidget(self.rate_button, 2, 0, 1, 3)
        rate.addWidget(self.rate_output, 3, 0, 1, 3)
        root.addWidget(rate_panel)

        transfer_panel = QFrame()
        transfer_panel.setObjectName("panel")
        transfer = QGridLayout(transfer_panel)
        self.file_size = self._number(10)
        self.file_unit = QComboBox()
        self.file_unit.addItems(["MB", "GB", "TB"])
        self.speed = self._number(100)
        self.speed_unit = QComboBox()
        self.speed_unit.addItems(["Mbps", "Gbps"])
        self.transfer_output = QLabel("Estimated download time will appear here.")
        self.transfer_output.setObjectName("resultValue")
        self.transfer_output.setWordWrap(True)
        file_row = QHBoxLayout()
        file_row.addWidget(self.file_size, 1)
        file_row.addWidget(self.file_unit)
        speed_row = QHBoxLayout()
        speed_row.addWidget(self.speed, 1)
        speed_row.addWidget(self.speed_unit)
        transfer.addWidget(QLabel("Download size"), 0, 0)
        transfer.addWidget(QLabel("Connection speed"), 0, 1)
        transfer.addLayout(file_row, 1, 0)
        transfer.addLayout(speed_row, 1, 1)
        self.transfer_button = QPushButton("Calculate Download Time")
        transfer.addWidget(self.transfer_button, 2, 0, 1, 2)
        transfer.addWidget(self.transfer_output, 3, 0, 1, 2)
        root.addWidget(transfer_panel)

        share_panel = QFrame()
        share_panel.setObjectName("panel")
        share = QGridLayout(share_panel)
        self.total_bandwidth = self._number(1000)
        self.subscribers = QSpinBox()
        self.subscribers.setRange(1, 100000)
        self.subscribers.setValue(100)
        self.ratio = self._number(1.0, 100)
        self.shared_output = QLabel("Per-user share will appear here.")
        self.shared_output.setObjectName("resultValue")
        self.shared_output.setWordWrap(True)
        share.addWidget(QLabel("Total bandwidth (Mbps)"), 0, 0)
        share.addWidget(QLabel("Number of users"), 0, 1)
        share.addWidget(QLabel("Oversubscription ratio (1 = 1:1)"), 0, 2)
        share.addWidget(self.total_bandwidth, 1, 0)
        share.addWidget(self.subscribers, 1, 1)
        share.addWidget(self.ratio, 1, 2)
        self.share_button = QPushButton("Calculate Shared Capacity")
        share.addWidget(self.share_button, 2, 0, 1, 3)
        share.addWidget(self.shared_output, 3, 0, 1, 3)
        root.addWidget(share_panel)

        usage_panel = QFrame()
        usage_panel.setObjectName("panel")
        usage = QGridLayout(usage_panel)
        self.average_speed = self._number(10)
        self.utilization = self._number(35, 100)
        self.usage_output = QLabel("Estimated 30-day traffic will appear here.")
        self.usage_output.setObjectName("resultValue")
        self.usage_output.setWordWrap(True)
        usage.addWidget(QLabel("Average traffic rate (Mbps)"), 0, 0)
        usage.addWidget(QLabel("Average utilization (%)"), 0, 1)
        usage.addWidget(self.average_speed, 1, 0)
        usage.addWidget(self.utilization, 1, 1)
        self.usage_button = QPushButton("Estimate 30-Day Data Usage")
        usage.addWidget(self.usage_button, 2, 0, 1, 2)
        usage.addWidget(self.usage_output, 3, 0, 1, 2)
        root.addWidget(usage_panel)
        root.addStretch()

        self.rate_button.clicked.connect(self._convert_rate)
        self.transfer_button.clicked.connect(self._transfer_time)
        self.share_button.clicked.connect(self._share)
        self.usage_button.clicked.connect(self._usage)

    def _convert_rate(self):
        value = self.rate_value.value() * RATE_UNITS[self.rate_from.currentText()]
        result = value / RATE_UNITS[self.rate_to.currentText()]
        self.rate_output.setText(f"{self.rate_value.value():g} {self.rate_from.currentText()} = {result:,.6g} {self.rate_to.currentText()}")

    def _transfer_time(self):
        factors = {"MB": 8_000_000, "GB": 8_000_000_000, "TB": 8_000_000_000_000}
        bits = self.file_size.value() * factors[self.file_unit.currentText()]
        bps = self.speed.value() * RATE_UNITS[self.speed_unit.currentText()]
        if bps <= 0:
            self.transfer_output.setText("Enter a connection speed greater than zero.")
            return
        seconds = bits / bps
        if seconds < 60:
            readable = f"{seconds:.1f} seconds"
        elif seconds < 3600:
            readable = f"{seconds / 60:.1f} minutes"
        elif seconds < 86400:
            readable = f"{seconds / 3600:.2f} hours"
        else:
            readable = f"{seconds / 86400:.2f} days"
        self.transfer_output.setText(f"Estimated ideal transfer time: {readable}\nReal downloads may take longer because of protocol overhead, congestion, server limits and Wi-Fi conditions.")

    def _share(self):
        capacity = self.total_bandwidth.value() / max(1, self.subscribers.value()) / max(0.01, self.ratio.value())
        self.shared_output.setText(f"Estimated average capacity per user: {capacity:.2f} Mbps\nThis is a planning estimate, not a guaranteed per-subscriber speed.")

    def _usage(self):
        seconds = 30 * 24 * 60 * 60
        bits = self.average_speed.value() * 1_000_000 * (self.utilization.value() / 100) * seconds
        gigabytes = bits / 8 / 1_000_000_000
        terabytes = gigabytes / 1000
        self.usage_output.setText(f"Estimated 30-day transfer: {gigabytes:,.2f} GB ({terabytes:.3f} TB)\nAssumes a constant average rate and decimal units. Actual traffic depends on usage patterns and accounting rules.")
