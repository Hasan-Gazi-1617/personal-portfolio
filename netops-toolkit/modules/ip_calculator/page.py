"""Modern dual-stack IPv4 / IPv6 calculator page for NetOps Toolkit."""
import ipaddress
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QSlider, QSpinBox, QComboBox, QTabWidget,
    QScrollArea, QSizePolicy
)


class CalculatorTab(QWidget):
    def __init__(self, version: int):
        super().__init__()
        self.version = version
        self.maximum = 32 if version == 4 else 128
        self.default_value = "192.168.1.0/24" if version == 4 else "2001:db8::/64"
        self._building = False
        self._build_ui()
        self.update_results()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)

        quick = QHBoxLayout()
        quick.addWidget(self._muted("TRY"))
        examples = (["192.168.1.0/24", "10.0.0.0/8", "172.16.0.0/12", "10.0.0.0/31"]
                    if self.version == 4 else
                    ["2001:db8::/32", "2001:db8:1234::/48", "fd00::/8", "fe80::/10"])
        for value in examples:
            btn = QPushButton(value)
            btn.setObjectName("quickChip")
            btn.clicked.connect(lambda checked=False, v=value: self.set_value(v))
            quick.addWidget(btn)
        quick.addStretch()
        outer.addLayout(quick)

        input_row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(self._muted(f"IPv{self.version} address"))
        self.address = QLineEdit(self.default_value)
        self.address.setMinimumHeight(42)
        self.address.setPlaceholderText("Enter address or CIDR")
        self.address.textChanged.connect(self._sync_prefix_from_text)
        left.addWidget(self.address)
        input_row.addLayout(left, 3)

        right = QVBoxLayout()
        prefix_head = QHBoxLayout()
        prefix_head.addWidget(self._muted("Prefix length"))
        prefix_head.addStretch()
        self.prefix_value = QLabel("/24" if self.version == 4 else "/64")
        self.prefix_value.setObjectName("prefixBadge")
        prefix_head.addWidget(self.prefix_value)
        right.addLayout(prefix_head)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.maximum)
        self.slider.setValue(24 if self.version == 4 else 64)
        self.slider.valueChanged.connect(self._prefix_changed)
        right.addWidget(self.slider)
        input_row.addLayout(right, 1)
        outer.addLayout(input_row)

        split_panel = QFrame()
        split_panel.setObjectName("panel")
        split_layout = QVBoxLayout(split_panel)
        split_layout.setContentsMargins(14, 12, 14, 12)
        split_row = QHBoxLayout()
        split_row.addWidget(self._muted("Divide into"))
        self.split = QComboBox()
        self.split.addItems(["No split", "2 subnets", "4 subnets", "8 subnets", "16 subnets", "32 subnets", "64 subnets"])
        self.split.currentIndexChanged.connect(self.update_results)
        split_row.addWidget(self.split)
        split_row.addStretch()
        split_layout.addLayout(split_row)
        self.bit_visual = QLabel()
        self.bit_visual.setObjectName("bitVisual")
        self.bit_visual.setWordWrap(True)
        split_layout.addWidget(self.bit_visual)
        legend = QHBoxLayout()
        legend.addWidget(self._muted("■ Network bits"))
        legend.addSpacing(18)
        legend.addWidget(self._muted("■ Host bits"))
        legend.addStretch()
        split_layout.addLayout(legend)
        outer.addWidget(split_panel)

        self.results_grid = QGridLayout()
        self.results_grid.setHorizontalSpacing(14)
        self.results_grid.setVerticalSpacing(8)
        outer.addLayout(self.results_grid)

        self.split_title = self._muted("SUBNET BREAKDOWN")
        outer.addWidget(self.split_title)
        self.split_output = QLabel("Choose a split option to list the resulting networks.")
        self.split_output.setObjectName("splitOutput")
        self.split_output.setWordWrap(True)
        outer.addWidget(self.split_output)
        outer.addStretch()

    def _muted(self, text):
        label = QLabel(text)
        label.setObjectName("muted")
        return label

    def set_value(self, value):
        self.address.setText(value)

    def _sync_prefix_from_text(self, text):
        if self._building:
            return
        if "/" in text:
            try:
                prefix = int(text.rsplit("/", 1)[1])
                if 0 <= prefix <= self.maximum:
                    self.slider.blockSignals(True)
                    self.slider.setValue(prefix)
                    self.slider.blockSignals(False)
                    self.prefix_value.setText(f"/{prefix}")
            except ValueError:
                pass
        self.update_results()

    def _prefix_changed(self, value):
        self.prefix_value.setText(f"/{value}")
        raw = self.address.text().strip()
        if raw:
            host = raw.split("/", 1)[0]
            self._building = True
            self.address.setText(f"{host}/{value}")
            self._building = False
        self.update_results()

    def _card(self, title, rows):
        frame = QFrame()
        frame.setObjectName("resultCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel(title)
        heading.setObjectName("cardHeading")
        layout.addWidget(heading)
        for label, value in rows:
            row = QHBoxLayout()
            texts = QVBoxLayout()
            name = QLabel(label)
            name.setObjectName("muted")
            val = QLabel(str(value))
            val.setObjectName("resultValue")
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setWordWrap(True)
            texts.addWidget(name)
            texts.addWidget(val)
            row.addLayout(texts, 1)
            copy = QPushButton("COPY")
            copy.setObjectName("copyButton")
            copy.setMaximumWidth(64)
            copy.clicked.connect(lambda checked=False, v=str(value): self._copy(v))
            row.addWidget(copy, 0, Qt.AlignmentFlag.AlignVCenter)
            layout.addLayout(row)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setObjectName("cardDivider")
            layout.addWidget(line)
        return frame

    def _copy(self, value):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(value)

    def update_results(self):
        while self.results_grid.count():
            item = self.results_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        try:
            raw = self.address.text().strip()
            if not raw:
                raise ValueError("Enter an IPv address in CIDR notation.")
            network = ipaddress.ip_network(raw, strict=False)
            if network.version != self.version:
                raise ValueError(f"Please enter an IPv{self.version} address.")
            prefix = network.prefixlen
            total = network.num_addresses
            if self.version == 4:
                if prefix <= 30:
                    host_first, host_last = network.network_address + 1, network.broadcast_address - 1
                    usable = total - 2
                elif prefix == 31:
                    host_first, host_last, usable = network.network_address, network.broadcast_address, 2
                else:
                    host_first = host_last = network.network_address
                    usable = 1
                first, last = host_first, host_last
                addressing = [
                    ("Network address", network.network_address),
                    ("Broadcast address", network.broadcast_address),
                    ("Usable host range", f"{first}  –  {last}"),
                    ("CIDR notation", network),
                ]
                masks = [
                    ("Subnet mask", network.netmask),
                    ("Wildcard mask", network.hostmask),
                    ("Binary mask", self._binary_mask(network.netmask)),
                ]
                capacity = [
                    ("Total addresses", f"{total:,}"),
                    ("Usable hosts", f"{usable:,}"),
                    ("IP class", self._ip_class(network.network_address)),
                ]
            else:
                first, last = network.network_address, network.broadcast_address
                addressing = [
                    ("Network prefix", network.with_prefixlen),
                    ("First address", first),
                    ("Last address", last),
                    ("Compressed address", network.network_address.compressed),
                    ("Expanded address", network.network_address.exploded),
                ]
                masks = [
                    ("Prefix length", f"/{prefix}"),
                    ("Address type", self._ipv6_type(network.network_address)),
                    ("Scope", "Link-local" if network.network_address.is_link_local else "Global / ULA / Other"),
                ]
                capacity = [
                    ("Total addresses", f"{total:,}"),
                    ("Total addresses (exact)", f"2^{self.maximum-prefix}"),
                    ("Address bits", str(self.maximum)),
                ]
            cards = [self._card("ADDRESSING", addressing), self._card("MASKS", masks), self._card("CAPACITY", capacity)]
            for col, card in enumerate(cards):
                self.results_grid.addWidget(card, 0, col)
            self.bit_visual.setText(self._bit_bar(prefix))
            self._update_split(network)
        except Exception as exc:
            error = QLabel(f"Enter a valid IPv{self.version} address and prefix.\n{exc}")
            error.setObjectName("errorText")
            self.results_grid.addWidget(error, 0, 0, 1, 3)
            self.bit_visual.setText("Network and host bit layout will appear after a valid address is entered.")
            self.split_output.setText("Subnet breakdown unavailable until the address is valid.")

    def _bit_bar(self, prefix):
        network_bits = "■ " * prefix
        host_bits = "□ " * (self.maximum - prefix)
        return f"{network_bits}{host_bits}\nNetwork: {prefix} bits    •    Host: {self.maximum-prefix} bits"

    def _binary_mask(self, mask):
        return ".".join(f"{int(part):08b}" for part in str(mask).split("."))

    def _ip_class(self, address):
        first = int(str(address).split(".")[0])
        if first < 128: return "A"
        if first < 192: return "B"
        if first < 224: return "C"
        if first < 240: return "D (Multicast)"
        return "E (Experimental)"

    def _ipv6_type(self, address):
        if address.is_loopback: return "Loopback"
        if address.is_link_local: return "Link-local"
        if address.is_multicast: return "Multicast"
        if address.is_private: return "Unique-local"
        return "Global unicast / Other"

    def _update_split(self, network):
        count = 1 if self.split.currentIndex() == 0 else 2 ** self.split.currentIndex()
        if count == 1:
            self.split_output.setText("Choose a split option to list the resulting networks.")
            return
        new_prefix = network.prefixlen + int(math.log2(count))
        if new_prefix > self.maximum:
            self.split_output.setText("This network is too small to be divided into that many subnets.")
            return
        subnets = list(network.subnets(new_prefix=new_prefix))
        self.split_output.setText("\n".join(f"{i+1:>2}.  {subnet}" for i, subnet in enumerate(subnets)))


class IPCalculatorPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        title = QLabel("IP Calculator")
        title.setObjectName("title")
        subtitle = QLabel("Dual-stack subnet planning for IPv4 and IPv6 networks.")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.tabs = QTabWidget()
        self.tabs.setObjectName("ipTabs")
        self.ipv4 = CalculatorTab(4)
        self.ipv6 = CalculatorTab(6)
        self.tabs.addTab(self.ipv4, "IPv4")
        self.tabs.addTab(self.ipv6, "IPv6")
        layout.addWidget(self.tabs, 1)
