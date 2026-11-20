# NetOps Toolkit

Cross-platform network diagnostics desktop application built with Python and PySide6.

## Features in v0.1.0
- Dashboard: host, OS, local IP and network interfaces
- Ping diagnostics
- DNS A/AAAA lookup
- IPv4/IPv6 CIDR calculator
- Dark and light themes

## Run
Python 3.11+ is required.

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Build on the target OS with `pip install pyinstaller`, then `pyinstaller --noconfirm --windowed --name NetOpsToolkit app.py`. PyInstaller builds must run on each target OS; it is not a cross-compiler.

Only test systems and networks you own or are authorized to assess.
