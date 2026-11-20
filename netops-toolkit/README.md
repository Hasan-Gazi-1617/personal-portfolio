# NetOps Toolkit

Cross-platform network diagnostics desktop application built with Python and PySide6.

## Features in v0.1.0
- Dashboard: host, OS, local IP and network interfaces
- Ping diagnostics
- DNS A/AAAA lookup
- Redesigned dual-stack IP Calculator with separate IPv4 and IPv6 tabs\n- Live prefix slider, quick examples, subnet splitting, address ranges, masks and copy actions
- Dark and light themes

## Installation

See the [Windows and Linux installation guide](INSTALLATION.md) for release downloads, first launch, source setup, and troubleshooting.

Download ready-to-run builds from [GitHub Releases](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest).

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
