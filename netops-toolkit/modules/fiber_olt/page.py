"""Fiber link-budget and GPON/OLT field reference tools."""
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFrame, QTextBrowser, QDoubleSpinBox, QSpinBox,
)


SPLITTER_LOSS = {
    "1:2": 3.6, "1:4": 7.2, "1:8": 10.5, "1:16": 13.7,
    "1:32": 17.1, "1:64": 20.4, "1:128": 23.5,
}


class FiberOLTPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _spin(self, value, maximum=10000, decimals=2):
        field = QDoubleSpinBox()
        field.setRange(0, maximum)
        field.setDecimals(decimals)
        field.setValue(value)
        field.setMinimumHeight(38)
        return field

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        title = QLabel("Fiber & OLT Tools")
        title.setObjectName("title")
        root.addWidget(title)
        intro = QLabel("Estimate GPON optical loss, received power and link margin. Values are planning estimates; verify real optical levels with a calibrated power meter.")
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        panel = QFrame()
        panel.setObjectName("panel")
        grid = QGridLayout(panel)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.tx = self._spin(5.0, 20)
        self.distance = self._spin(5.0, 200)
        self.wavelength = QComboBox()
        self.wavelength.addItems(["1490 nm downstream (0.25 dB/km)", "1310 nm upstream (0.35 dB/km)", "1550 nm video (0.22 dB/km)", "Custom attenuation"])
        self.attenuation = self._spin(0.25, 5)
        self.splitter = QComboBox()
        self.splitter.addItems(list(SPLITTER_LOSS))
        self.connectors = QSpinBox()
        self.connectors.setRange(0, 100)
        self.connectors.setValue(4)
        self.splices = QSpinBox()
        self.splices.setRange(0, 500)
        self.splices.setValue(8)
        self.connector_loss = self._spin(0.3, 5)
        self.splice_loss = self._spin(0.1, 5)
        fields = [
            ("OLT Tx power (dBm)", self.tx), ("Fiber length (km)", self.distance),
            ("Wavelength / profile", self.wavelength), ("Fiber attenuation (dB/km)", self.attenuation),
            ("Splitter ratio", self.splitter), ("Connector count", self.connectors),
            ("Splice count", self.splices), ("Loss per connector (dB)", self.connector_loss),
            ("Loss per splice (dB)", self.splice_loss),
        ]
        for index, (label, field) in enumerate(fields):
            row, col = divmod(index, 3)
            cell = QVBoxLayout()
            caption = QLabel(label)
            caption.setObjectName("muted")
            cell.addWidget(caption)
            cell.addWidget(field)
            grid.addLayout(cell, row, col)
        root.addWidget(panel)

        actions = QHBoxLayout()
        self.calculate = QPushButton("Calculate Link Budget")
        self.clear = QPushButton("Clear All")
        self.clear.setObjectName("clearButton")
        actions.addWidget(self.calculate)
        actions.addWidget(self.clear)
        actions.addStretch()
        root.addLayout(actions)

        self.result = QLabel("Enter your link values, then calculate the estimated ONU receive power.")
        self.result.setObjectName("splitOutput")
        self.result.setWordWrap(True)
        self.result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.result)

        reference = QTextBrowser()
        reference.setOpenExternalLinks(True)
        reference.setHtml("""
        <h3>GPON field reference</h3>
        <p><b>Typical planning ranges (check your OLT/ONU datasheet):</b></p>
        <ul>
          <li>Class B+: approximately +1.5 to +5 dBm OLT Tx; ONU sensitivity often around -27 dBm.</li>
          <li>Class C+: higher optical budget; exact limits depend on vendor and optics.</li>
          <li>Common splitter insertion loss: 1:2 3.6 dB, 1:4 7.2 dB, 1:8 10.5 dB, 1:16 13.7 dB, 1:32 17.1 dB, 1:64 20.4 dB.</li>
          <li>Low ONU Rx can indicate dirty connectors, excessive split loss, bends, damaged fiber or long distance.</li>
        </ul>
        <h3>OLT / ONU troubleshooting sequence</h3>
        <ol>
          <li>Check OLT PON port state and optical Tx power.</li>
          <li>Check ONU state, serial number, distance and last-down cause.</li>
          <li>Measure optical power at the distribution point and customer end.</li>
          <li>Inspect and clean connectors, then check splitter and splice losses.</li>
          <li>Compare readings with the vendor's supported optical budget.</li>
        </ol>
        <p><b>Safety:</b> Never look into a fiber connector. Use an optical power meter and follow laser-safety procedures.</p>
        """)
        root.addWidget(reference, 1)

        self.wavelength.currentIndexChanged.connect(self._sync_attenuation)
        self.calculate.clicked.connect(self._calculate)
        self.clear.clicked.connect(self._clear)

    def _sync_attenuation(self, index):
        presets = [0.25, 0.35, 0.22, self.attenuation.value()]
        if index < 3:
            self.attenuation.setValue(presets[index])
            self.attenuation.setEnabled(False)
        else:
            self.attenuation.setEnabled(True)

    def _calculate(self):
        fiber = self.distance.value() * self.attenuation.value()
        split = SPLITTER_LOSS[self.splitter.currentText()]
        connector = self.connectors.value() * self.connector_loss.value()
        splice = self.splices.value() * self.splice_loss.value()
        total = fiber + split + connector + splice
        rx = self.tx.value() - total
        margin = rx - (-27.0)
        state = "WITHIN ESTIMATED CLASS B+ SENSITIVITY" if rx >= -27 else "BELOW TYPICAL CLASS B+ SENSITIVITY"
        if rx > -8:
            state = "CHECK OVERLOAD LIMITS: RECEIVED POWER MAY BE TOO HIGH"
        self.result.setText(
            f"ESTIMATED ONU RX POWER: {rx:.2f} dBm\n"
            f"Total estimated optical loss: {total:.2f} dB\n"
            f"  Fiber: {fiber:.2f} dB | Splitter: {split:.2f} dB\n"
            f"  Connectors: {connector:.2f} dB | Splices: {splice:.2f} dB\n"
            f"Margin against -27 dBm reference: {margin:.2f} dB\n\n"
            f"ASSESSMENT: {state}\n"
            "This is an estimate, not a live OLT reading. Confirm with actual optical measurements and the exact transceiver specification."
        )

    def _clear(self):
        self.tx.setValue(5.0)
        self.distance.setValue(5.0)
        self.wavelength.setCurrentIndex(0)
        self.splitter.setCurrentIndex(4)
        self.connectors.setValue(4)
        self.splices.setValue(8)
        self.connector_loss.setValue(0.3)
        self.splice_loss.setValue(0.1)
        self.result.setText("Enter your link values, then calculate the estimated ONU receive power.")
