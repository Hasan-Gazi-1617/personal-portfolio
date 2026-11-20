from PySide6.QtCore import Qt
from pathlib import Path
from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QFrame,QLabel,QPushButton,QStackedWidget,QLineEdit,QSpinBox,QTextEdit,QGridLayout
from core.network_info import snapshot
from core.worker import Worker
from modules.diagnostics.ping import ping
from modules.dns_tools.lookup import lookup
from modules.ip_calculator.page import IPCalculatorPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetOps Toolkit")
        self.resize(1180,760)
        self.setMinimumSize(900,620)
        self.theme="dark"; self.worker=None
        central=QWidget(); root=QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sidebar=QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(225)
        sl=QVBoxLayout(sidebar); sl.setContentsMargins(16,22,16,18)
        brand=QLabel("NetOps Toolkit"); brand.setObjectName("brand"); sl.addWidget(brand)
        sub=QLabel("NETWORK OPERATIONS"); sub.setObjectName("muted"); sl.addWidget(sub); sl.addSpacing(20)
        self.stack=QStackedWidget(); self.nav=[]
        for name,builder in [("Dashboard",self.dashboard),("Ping Test",self.ping_page),("DNS Lookup",self.dns_page),("IP Calculator",self.subnet_page)]:
            button=QPushButton(name); button.setCheckable(True); button.setChecked(not self.nav)
            button.clicked.connect(lambda checked=False,n=name:self.open_page(n))
            sl.addWidget(button); self.nav.append((name,button)); self.stack.addWidget(builder())
        sl.addStretch(); self.theme_btn=QPushButton("Switch to Light Theme"); self.theme_btn.clicked.connect(self.toggle_theme); sl.addWidget(self.theme_btn)
        credit = QLabel("Developed by Hasan Gazi")
        credit.setAlignment(Qt.AlignCenter)
        credit.setStyleSheet(
            "color: #8b95a5; font-size: 11px; padding-top: 10px;")
        sl.addWidget(credit)
        content=QWidget(); cl=QVBoxLayout(content); cl.setContentsMargins(28,24,28,24)
        heading=QLabel("Monitor  •  Diagnose  •  Optimize your network"); heading.setObjectName("muted")
        cl.addWidget(heading); cl.addWidget(self.stack,1)
        root.addWidget(sidebar); root.addWidget(content,1); self.setCentralWidget(central); self.apply_theme()
    def panel(self):
        frame=QFrame(); frame.setObjectName("panel"); frame.setLayout(QVBoxLayout()); frame.layout().setContentsMargins(16,14,16,14); return frame
    def dashboard(self):
        widget=QWidget(); layout=QVBoxLayout(widget); title=QLabel("Network Overview"); title.setObjectName("title"); layout.addWidget(title)
        info=snapshot(); grid=QGridLayout()
        for i,(key,value) in enumerate([("Hostname",info["hostname"]),("Local IP",info["ip"]),("Operating System",info["os"]),("Interfaces",str(len(info["interfaces"])))]):
            card=self.panel(); label=QLabel(key); label.setObjectName("muted"); val=QLabel(value); val.setStyleSheet("font-size:17px;font-weight:700")
            card.layout().addWidget(label); card.layout().addWidget(val); grid.addWidget(card,i//2,i%2)
        layout.addLayout(grid); layout.addWidget(QLabel("Detected network interfaces"))
        for item in info["interfaces"]: layout.addWidget(QLabel(f'{item["name"]}  |  IPv4: {item["ipv4"]}  |  MAC: {item["mac"]}'))
        layout.addStretch(); return widget
    def tool_page(self,title,description,placeholder,function,button_text,with_count=False):
        widget=QWidget(); layout=QVBoxLayout(widget); heading=QLabel(title); heading.setObjectName("title")
        layout.addWidget(heading); layout.addWidget(QLabel(description)); row=QHBoxLayout()
        entry=QLineEdit(); entry.setPlaceholderText(placeholder); row.addWidget(entry,1); count=None
        if with_count:
            count=QSpinBox(); count.setRange(1,20); count.setValue(4); row.addWidget(QLabel("Count")); row.addWidget(count)
        button=QPushButton(button_text); row.addWidget(button)
        clear_button=QPushButton("Clear All"); clear_button.setObjectName("clearButton"); clear_button.setToolTip("Clear the input and all displayed results"); row.addWidget(clear_button)
        layout.addLayout(row)
        output=QTextEdit(); output.setReadOnly(True); output.setPlaceholderText("Results will appear here..."); layout.addWidget(output,1)
        def clear():
            if self.worker and self.worker.isRunning(): return
            entry.clear()
            output.clear()
            if count: count.setValue(4)
        clear_button.clicked.connect(clear)
        def run():
            if self.worker and self.worker.isRunning(): return
            button.setEnabled(False); clear_button.setEnabled(False); output.setPlainText("Working...")
            args=(entry.text(),count.value()) if count else (entry.text(),)
            self.worker=Worker(function,*args); self.worker.done.connect(output.setPlainText)
            self.worker.failed.connect(lambda error:output.setPlainText("Error: "+error))
            def finish():
                button.setEnabled(True)
                clear_button.setEnabled(True)
            self.worker.finished.connect(finish); self.worker.start()
        button.clicked.connect(run); return widget
    def ping_page(self): return self.tool_page("Ping Test","Check reachability, response time and packet loss.","1.1.1.1 or example.com",ping,"Run Ping",True)
    def dns_page(self): return self.tool_page("DNS Lookup","Resolve IPv4 and IPv6 DNS records.","example.com",lookup,"Lookup")
    def subnet_page(self):
        return IPCalculatorPage()
    def open_page(self,name):
        for index,(item,button) in enumerate(self.nav):
            button.setChecked(item==name)
            if item==name: self.stack.setCurrentIndex(index)
    def toggle_theme(self):
        self.theme="light" if self.theme=="dark" else "dark"; self.apply_theme()
    def apply_theme(self):
        path=Path(__file__).parent/"themes"/f"{self.theme}.qss"
        self.setStyleSheet(path.read_text(encoding="utf-8"))
        self.theme_btn.setText("Switch to Light Theme" if self.theme=="dark" else "Switch to Dark Theme")
