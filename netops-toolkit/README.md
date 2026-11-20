# NetOps Toolkit

Cross-platform network diagnostics desktop application built with Python and PySide6.

## Features

- Dashboard: hostname, operating system, local IP and network interfaces
- Ping diagnostics
- DNS A/AAAA lookup
- Dual-stack IP Calculator with separate IPv4 and IPv6 tabs
- Live prefix slider, quick examples, subnet splitting, address ranges, masks and copy actions
- Dark and light themes

## 1. Download the application

For normal use, download the ready-to-run application. You do not need to install Python or run terminal commands.

1. Open the [latest GitHub Release](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest).
2. Find the **Assets** section.
3. Download the file for your operating system:

| Operating system | Download |
|---|---|
| Windows 10/11, 64-bit | [NetOpsToolkit-Windows.exe](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest/download/NetOpsToolkit-Windows.exe) |
| Ubuntu / Debian, 64-bit | [NetOpsToolkit-Linux.deb](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest/download/NetOpsToolkit-Linux.deb) | Recommended; installs app, icon and menu launcher automatically |
| Other compatible Linux distributions | [NetOpsToolkit-Linux.AppImage](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest/download/NetOpsToolkit-Linux.AppImage) | Portable; optional manual icon and menu setup |

If an asset is not listed in the release, that build has not been published yet. Do not use an old download link as proof that a newer build is ready.

## 2. Install and run on Windows

1. Download `NetOpsToolkit-Windows.exe` from the release page.
2. Open File Explorer and go to **Downloads**.
3. Double-click `NetOpsToolkit-Windows.exe`.
4. If Microsoft Defender SmartScreen displays a warning, verify that the file came from this repository's official GitHub Releases page. Only run it if you trust the source.
5. The application should open.

This packaged executable is intended to run without a separate Python installation. It is a portable app; a traditional setup wizard may not be provided. You can move the EXE to a folder where you want to keep it and create a desktop shortcut if desired.

## 3. Install and run on Linux

### Option A: Ubuntu / Debian using the DEB package (recommended)

The DEB package installs NetOps Toolkit, its custom icon and an Applications Menu launcher automatically. No manual icon setup is required.

1. Download [NetOpsToolkit-Linux.deb](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest/download/NetOpsToolkit-Linux.deb).
2. Open **Files → Downloads**.
3. Double-click `NetOpsToolkit-Linux.deb`.
4. Open it with App Center / Software Install and click **Install**.
5. Open **Show Apps**, search for **NetOps Toolkit**, and click its icon.

Or install it from Terminal:

```bash
cd ~/Downloads
sudo apt install ./NetOpsToolkit-Linux.deb
```

To uninstall:

```bash
sudo apt remove netops-toolkit
```

### Option B: AppImage (portable, with manual icon setup)

AppImage is portable. It can run directly, but it does not automatically create an Applications Menu entry on every Linux desktop.

**1. Download and make it executable**

Download [NetOpsToolkit-Linux.AppImage](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest/download/NetOpsToolkit-Linux.AppImage), then open Terminal:

```bash
cd ~/Downloads
chmod +x NetOpsToolkit-Linux.AppImage
```

**2. Run the application**

```bash
./NetOpsToolkit-Linux.AppImage
```

Alternatively, in Files, right-click the AppImage, open **Properties → Permissions**, enable **Allow executing file as a program**, then double-click it.

**3. Extract and install the custom icon**

The icon is bundled inside the AppImage. Extract its contents:

```bash
cd ~/Downloads
./NetOpsToolkit-Linux.AppImage --appimage-extract
```

Create the icon folder and copy the bundled icon:

```bash
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp squashfs-root/netops-toolkit.png ~/.local/share/icons/hicolor/256x256/apps/netops-toolkit.png
mkdir -p ~/.local/share/applications
```

**4. Create an Applications Menu launcher**

This creates a launcher that points to the AppImage in your Downloads folder:

```bash
APPIMAGE="$HOME/Downloads/NetOpsToolkit-Linux.AppImage"
DESKTOP_FILE="$HOME/.local/share/applications/netops-toolkit.desktop"

printf '[Desktop Entry]\nType=Application\nName=NetOps Toolkit\nComment=Network Operations Toolkit\nExec="%s"\nIcon=netops-toolkit\nCategories=Network;Utility;\nTerminal=false\nStartupNotify=true\n' "$APPIMAGE" > "$DESKTOP_FILE"

chmod +x "$DESKTOP_FILE"
```

If you move the AppImage, update the `APPIMAGE=` path and run the launcher creation command again.

**5. Launch from the desktop menu**

Open **Show Apps**, search for **NetOps Toolkit**, and click its icon. If the launcher or icon does not appear immediately, log out and back in.

You can remove the temporary extracted files after copying the icon:

```bash
rm -rf ~/Downloads/squashfs-root
```

**Which Linux file should you choose?** On Ubuntu or Debian, use the DEB package for the easiest installation and automatic menu icon. Use AppImage if you prefer a portable file or use another compatible Linux distribution.

### Linux troubleshooting

- **Permission denied:** run `chmod +x NetOpsToolkit-Linux.AppImage` from Downloads.
- **AppImage FUSE error:** install the FUSE compatibility package supported by your Linux distribution.
- **AppImage icon missing:** repeat the icon extraction and copy commands above.
- **DEB launcher not visible:** log out and back in, then search for **NetOps Toolkit** again.
- **File not found:** check the filename with `ls -l ~/Downloads`.

## 4. Run from source code (developers)

Use this method only if you want to inspect or modify the code. Python 3.11 or newer is required.

### Get the source code

Option A: Clone with Git:

```bash
git clone https://github.com/Hasan-Gazi-1617/personal-portfolio.git
cd personal-portfolio/netops-toolkit
```

Option B: Download the repository ZIP from GitHub, extract it, open the extracted `personal-portfolio` folder, then open a terminal in its `netops-toolkit` subfolder.

### Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Windows PowerShell

Install Python 3.11 or newer first. During installation, enable the option to add Python to PATH if the installer offers it. Then open PowerShell in the `netops-toolkit` folder:

```powershell
py --version
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell prevents virtual-environment activation, use the environment's Python directly instead:

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

### macOS

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## 5. Build an executable from source

Install PyInstaller inside the activated virtual environment:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name NetOpsToolkit app.py
```

The build output is placed in the `dist` directory. This basic command creates a platform-specific bundle, but it does not by itself guarantee an AppImage on Linux. Use the repository's release/build workflow for the distributable format.

**Important:** PyInstaller is not a cross-compiler. Build Windows executables on Windows, Linux packages on Linux, and macOS applications on macOS.

## 6. Update or reinstall

1. Open [GitHub Releases](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest).
2. Download the newest asset for your operating system.
3. Close the old application.
4. Replace the old EXE or AppImage with the newly downloaded file.
5. On Linux, run `chmod +x` on the new AppImage before launching it.

The packaged application does not automatically update itself.

## 7. Project files and help

- [NetOps Toolkit source folder](https://github.com/Hasan-Gazi-1617/personal-portfolio/tree/main/netops-toolkit)
- [Installation guide](INSTALLATION.md)
- [Latest releases and downloads](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases)
- [Report a problem](https://github.com/Hasan-Gazi-1617/personal-portfolio/issues)

## Safety

Use network diagnostic features only on systems and networks you own or are authorized to assess.
