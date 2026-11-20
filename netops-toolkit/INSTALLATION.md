# NetOps Toolkit Installation Guide

Open the [latest NetOps Toolkit release](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest) and download the file for your operating system.

| Operating system | Download |
|---|---|
| Windows 10/11 (64-bit) | `NetOpsToolkit-Windows.exe` |
| Ubuntu/Debian Linux (64-bit) | `NetOpsToolkit-Linux.deb` (recommended) |
| Other compatible Linux distributions | `NetOpsToolkit-Linux.AppImage` |
| macOS | `NetOpsToolkit-macOS.dmg` |

## Ubuntu / Debian: install with an application icon

1. Download `NetOpsToolkit-Linux.deb`.
2. Open the Downloads folder.
3. Double-click the `.deb` file and install it with App Center / Software Install.
4. Open the Applications menu and search for **NetOps Toolkit**.

The Debian package installs the application, its custom icon, and a desktop launcher automatically. No manual `chmod`, desktop-file creation, or icon copying is needed. The icon is also used by the application window.

You can install it from Terminal instead:

```bash
cd ~/Downloads
sudo apt install ./NetOpsToolkit-Linux.deb
```

To remove it:

```bash
sudo apt remove netops-toolkit
```

## Other Linux distributions: AppImage

The AppImage is portable and does not install a system menu entry by itself on every desktop environment. Make it executable and run it:

```bash
cd ~/Downloads
chmod +x NetOpsToolkit-Linux.AppImage
./NetOpsToolkit-Linux.AppImage
```

For automatic menu integration on Ubuntu/Debian, use the `.deb` package above.

## Windows

1. Download `NetOpsToolkit-Windows.exe`.
2. Open Downloads and double-click the file.
3. If Windows SmartScreen appears, verify the file came from this project's official GitHub Releases page before choosing to run it.

## macOS

1. Download `NetOpsToolkit-macOS.dmg`.
2. Open the DMG and move NetOps Toolkit to Applications.
3. Launch it from Applications. If macOS blocks an unsigned build, only override the warning if you trust the downloaded file.

## Run from source (developers)

Python 3.11 or newer is required. Open a terminal in the `netops-toolkit` directory.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Updating

Download and install the latest release again. The application does not update itself automatically.

## Troubleshooting

- **AppImage Permission denied:** run `chmod +x NetOpsToolkit-Linux.AppImage`.
- **AppImage FUSE error:** install the FUSE compatibility package supported by your Linux distribution.
- **Application menu icon missing after installing the DEB:** log out and back in, or refresh the desktop application menu.
- **Windows/macOS security warning:** verify the download came from this repository's official Releases page before proceeding.

Use network diagnostic features only on systems and networks you own or are authorized to assess.
