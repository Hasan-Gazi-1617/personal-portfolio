"""Wireshark-inspired packet capture page using Scapy/Npcap/libpcap."""
from datetime import datetime
from pathlib import Path

from scapy.all import AsyncSniffer, wrpcap
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog,
    QMessageBox, QSplitter, QHeaderView)


class CaptureController(QObject):
    packet_seen = Signal(object)
    state_changed = Signal(str)
    failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.sniffer = None
        self.packets = []

    def start(self, iface=None, capture_filter=""):
        if self.sniffer and self.sniffer.running:
            return
        self.packets.clear()
        try:
            self.sniffer = AsyncSniffer(
                iface=iface or None,
                filter=capture_filter or None,
                prn=self._on_packet,
                store=True,
            )
            self.sniffer.start()
            self.state_changed.emit("Capturing")
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_packet(self, packet):
        self.packets.append(packet)
        self.packet_seen.emit(packet)

    def stop(self):
        if self.sniffer and self.sniffer.running:
            try:
                self.sniffer.stop()
            except Exception as exc:
                self.failed.emit(str(exc))
        self.state_changed.emit("Stopped")

    def export(self, path):
        if not self.packets:
            raise ValueError("There are no captured packets to export.")
        wrpcap(path, self.packets)


def describe_packet(packet):
    src = dst = "-"
    sport = dport = "-"
    protocol = "OTHER"
    if IP in packet:
        src, dst = packet[IP].src, packet[IP].dst
    elif IPv6 in packet:
        src, dst = packet[IPv6].src, packet[IPv6].dst
    elif Ether in packet:
        src, dst = packet[Ether].src, packet[Ether].dst
    if packet.haslayer("DNS") or (TCP in packet and packet[TCP].dport == 53) or (UDP in packet and (packet[UDP].sport == 53 or packet[UDP].dport == 53)):
        protocol = "DNS"
    elif packet.haslayer("ARP"):
        protocol = "ARP"
    elif ICMP in packet:
        protocol = "ICMP"
    elif packet.haslayer("ICMPv6"):
        protocol = "ICMPv6"
    elif TCP in packet:
        sport, dport = str(packet[TCP].sport), str(packet[TCP].dport)
        protocol = "HTTPS" if 443 in (packet[TCP].sport, packet[TCP].dport) else "HTTP" if 80 in (packet[TCP].sport, packet[TCP].dport) else "TCP"
    elif UDP in packet:
        protocol, sport, dport = "UDP", str(packet[UDP].sport), str(packet[UDP].dport)
    elif packet.haslayer("Raw"):
        protocol = "DATA"
    return {
        "time": datetime.fromtimestamp(float(packet.time)).strftime("%H:%M:%S.%f")[:-3],
        "src": src, "dst": dst, "protocol": protocol,
        "sport": sport, "dport": dport, "length": str(len(packet)),
    }


class NetworkAnalyzerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.capture = CaptureController()
        self.capture.packet_seen.connect(self.add_packet)
        self.capture.state_changed.connect(self.set_state)
        self.capture.failed.connect(self.show_error)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        title = QLabel("Network Analyzer"); title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel("Live packet capture and protocol inspection. Capture only on networks you are authorized to monitor.")
        subtitle.setObjectName("muted"); root.addWidget(subtitle)

        controls = QHBoxLayout()
        self.interface = QComboBox(); self.interface.setEditable(True)
        self.interface.addItem("Default interface")
        try:
            from scapy.all import get_if_list
            self.interface.addItems(get_if_list())
        except Exception:
            pass
        self.bpf = QLineEdit(); self.bpf.setPlaceholderText("BPF filter (e.g. tcp port 443)")
        self.start_btn = QPushButton("Start Capture")
        self.stop_btn = QPushButton("Stop"); self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton("Clear All"); self.clear_btn.setObjectName("clearButton")
        self.export_btn = QPushButton("Export PCAP"); self.export_btn.setEnabled(False)
        controls.addWidget(QLabel("Interface")); controls.addWidget(self.interface, 1)
        controls.addWidget(self.bpf, 2); controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn); controls.addWidget(self.export_btn); controls.addWidget(self.clear_btn)
        root.addLayout(controls)

        filter_row = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Filter displayed packets by IP, port or text")
        self.protocol_filter = QComboBox(); self.protocol_filter.addItems(["All protocols","TCP","UDP","ICMP","ICMPv6","DNS","ARP","DATA","OTHER"])
        self.status = QLabel("Ready"); self.status.setObjectName("muted")
        filter_row.addWidget(self.search, 2); filter_row.addWidget(self.protocol_filter); filter_row.addWidget(self.status)
        root.addLayout(filter_row)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["No.","Time","Source","Destination","Protocol","Length","Ports"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.details = QTextEdit(); self.details.setReadOnly(True); self.details.setPlaceholderText("Select a packet to inspect its decoded layers.")
        splitter.addWidget(self.table); splitter.addWidget(self.details); splitter.setSizes([430,180])
        root.addWidget(splitter, 1)

        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.capture.stop)
        self.clear_btn.clicked.connect(self.clear_all)
        self.export_btn.clicked.connect(self.export_capture)
        self.search.textChanged.connect(self.refresh_filter)
        self.protocol_filter.currentTextChanged.connect(self.refresh_filter)
        self.table.itemSelectionChanged.connect(self.show_packet_details)

    def start_capture(self):
        iface = self.interface.currentText().strip()
        if iface == "Default interface": iface = ""
        self.start_btn.setEnabled(False)
        self.capture.start(iface, self.bpf.text().strip())

    def set_state(self, state):
        self.status.setText(f"{state}  |  {len(self.capture.packets)} packets")
        running = state == "Capturing"
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.export_btn.setEnabled(bool(self.capture.packets))

    def show_error(self, message):
        self.status.setText("Capture error")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.warning(self, "Packet capture", f"{message}\n\nLinux may require elevated capture permissions. Windows requires Npcap.")

    def add_packet(self, packet):
        self.set_state("Capturing")
        self.refresh_filter()

    def refresh_filter(self):
        query = self.search.text().lower().strip()
        proto = self.protocol_filter.currentText()
        self.table.setRowCount(0)
        for index, packet in enumerate(self.capture.packets, 1):
            info = describe_packet(packet)
            line = " ".join(info.values()).lower()
            if query and query not in line: continue
            if proto != "All protocols" and info["protocol"] != proto: continue
            row = self.table.rowCount(); self.table.insertRow(row)
            values = [str(index), info["time"], info["src"], info["dst"], info["protocol"], info["length"], f'{info["sport"]} → {info["dport"]}']
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.status.setText(f"{'Capturing' if self.capture.sniffer and self.capture.sniffer.running else 'Stopped'}  |  {len(self.capture.packets)} packets")

    def show_packet_details(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        packet_no = int(self.table.item(rows[0].row(), 0).text()) - 1
        if 0 <= packet_no < len(self.capture.packets):
            packet = self.capture.packets[packet_no]
            self.details.setPlainText(packet.show(dump=True))

    def export_capture(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export packet capture", "capture.pcap", "PCAP files (*.pcap)")
        if path:
            try: self.capture.export(path)
            except Exception as exc: QMessageBox.warning(self, "Export failed", str(exc))

    def clear_all(self):
        self.capture.stop()
        self.capture.packets.clear()
        self.table.setRowCount(0)
        self.details.clear()
        self.search.clear()
        self.protocol_filter.setCurrentIndex(0)
        self.status.setText("Ready")
        self.export_btn.setEnabled(False)
