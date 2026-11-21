"""Offline PCAP inspection companion for the live Network Analyzer."""
from collections import Counter
from scapy.utils import PcapReader
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog,
    QMessageBox, QSplitter, QHeaderView,
)
from modules.network_analyzer.page import describe_packet


MAX_PACKETS = 50000


class PCAPInspectorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.packets = []
        self.packet_rows = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        title = QLabel("PCAP File Inspector")
        title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel("Open a .pcap or .pcapng capture, filter packets, inspect decoded layers and review protocol counts. Large files are capped at 50,000 packets for safe desktop memory use.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        controls = QHBoxLayout()
        self.open_button = QPushButton("Open PCAP File")
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setObjectName("clearButton")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter by source, destination, protocol, port or packet text")
        self.protocol = QComboBox()
        self.protocol.addItems(["All protocols", "TCP", "UDP", "HTTP", "HTTPS", "ICMP", "ICMPv6", "DNS", "ARP", "DATA", "OTHER"])
        controls.addWidget(self.open_button)
        controls.addWidget(self.search, 1)
        controls.addWidget(self.protocol)
        controls.addWidget(self.clear_button)
        root.addLayout(controls)

        self.summary = QLabel("No capture loaded.")
        self.summary.setObjectName("muted")
        root.addWidget(self.summary)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["No.", "Time", "Source", "Destination", "Protocol", "Length", "Ports"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Select a packet to inspect its decoded layers.")
        splitter.addWidget(self.table)
        splitter.addWidget(self.details)
        splitter.setSizes([430, 180])
        root.addWidget(splitter, 1)

        self.open_button.clicked.connect(self.open_capture)
        self.clear_button.clicked.connect(self.clear_all)
        self.search.textChanged.connect(self.refresh)
        self.protocol.currentTextChanged.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.show_details)

    def open_capture(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open packet capture", "", "Packet captures (*.pcap *.pcapng *.cap);;All files (*)")
        if not path:
            return
        loaded = []
        try:
            with PcapReader(path) as reader:
                for packet in reader:
                    loaded.append(packet)
                    if len(loaded) >= MAX_PACKETS:
                        break
        except Exception as exc:
            QMessageBox.warning(self, "Could not read capture", f"{exc}\n\nCheck that the file is a valid PCAP/PCAPNG capture.")
            return
        self.packets = loaded
        self.search.clear()
        self.protocol.setCurrentIndex(0)
        self.refresh()
        note = " Showing first 50,000 packets only." if len(loaded) >= MAX_PACKETS else ""
        self.summary.setText(f"Loaded {len(loaded):,} packets from {path}.{note}")

    def refresh(self):
        self.table.setRowCount(0)
        counts = Counter()
        query = self.search.text().strip().lower()
        selected = self.protocol.currentText()
        for index, packet in enumerate(self.packets):
            info = describe_packet(packet)
            counts[info["protocol"]] += 1
            searchable = " ".join(str(value) for value in info.values()).lower()
            if query and query not in searchable:
                continue
            if selected != "All protocols" and info["protocol"] != selected:
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [str(index + 1), info["time"], info["src"], info["dst"], info["protocol"], info["length"], f'{info["sport"]} → {info["dport"]}']
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        if self.packets:
            summary = "  |  ".join(f"{key}: {value}" for key, value in counts.most_common())
            self.summary.setText(f"{len(self.packets):,} packets loaded  |  {self.table.rowCount():,} shown  |  {summary}")
        elif not self.summary.text().startswith("Could not"):
            self.summary.setText("No capture loaded.")

    def show_details(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        number = int(self.table.item(rows[0].row(), 0).text()) - 1
        if 0 <= number < len(self.packets):
            self.details.setPlainText(self.packets[number].show(dump=True))

    def clear_all(self):
        self.packets.clear()
        self.table.setRowCount(0)
        self.details.clear()
        self.search.clear()
        self.protocol.setCurrentIndex(0)
        self.summary.setText("No capture loaded.")
