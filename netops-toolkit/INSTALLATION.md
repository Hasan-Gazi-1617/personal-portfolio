# NetOps Toolkit Installation Guide

This guide covers the ready-to-run Windows and Linux downloads, plus running the source code for development.

## 1. Download the application

Open the [latest NetOps Toolkit release](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest).

Download the file for your operating system:

| Operating system | Release file |
|---|---|
| Windows 10/11 (64-bit) | `NetOpsToolkit-Windows.exe` |
| Linux (64-bit) | `NetOpsToolkit-Linux.AppImage` |

Do not download the source-code ZIP if you only want to run the application.

## 2. Windows installation and first launch

1. Open the latest release page linked above.
2. Download `NetOpsToolkit-Windows.exe`.
3. Open your **Downloads** folder.
4. Double-click `NetOpsToolkit-Windows.exe`.
5. If Windows SmartScreen appears, verify that you downloaded the file from this project's official GitHub Releases page. Only continue if you trust the file.
6. The application should open. If Windows asks for permission, review the prompt before allowing it.

This release is a standalone executable; Python does not need to be installed separately.

## 3. Linux installation and first launch

1. Open the latest release page linked above.
2. Download `NetOpsToolkit-Linux.AppImage`.
3. Open Terminal.
4. Move to the Downloads folder:

```bash
cd ~/Downloads
```

5. Give the AppImage permission to run:

```bash
chmod +x NetOpsToolkit-Linux.AppImage
```

6. Launch it:

```bash
./NetOpsToolkit-Linux.AppImage
```

You can also open the Downloads folder in the file manager, right-click the AppImage, open **Properties → Permissions**, enable **Allow executing file as a program**, then double-click it (the exact wording can vary by desktop environment).

If the AppImage reports a FUSE-related error, check your Linux distribution's AppImage/FUSE support and install the compatible FUSE package for that distribution. Package names differ between distributions and releases.

## 4. Run from source (developers)

Python 3.11 or newer is required. Download or clone the repository, then open a terminal in the `netops-toolkit` directory.

### Linux

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

If PowerShell blocks virtual-environment activation, you can run the environment's Python directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

## 5. Build the executable yourself

Install PyInstaller inside the activated virtual environment:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name NetOpsToolkit app.py
```

Run the build on the operating system you are targeting. PyInstaller is not a cross-compiler: build the Windows executable on Windows and the Linux AppImage/package on Linux using the project's build workflow.

## 6. Update the application

When a newer release is published, download the new file from [GitHub Releases](https://github.com/Hasan-Gazi-1617/personal-portfolio/releases/latest) and replace the older copy. Your downloaded executable does not update itself.

## 7. Troubleshooting

- **The download is missing:** Check the latest release page and confirm that an asset for your operating system has been published.
- **Linux says Permission denied:** Run the `chmod +x` command shown above.
- **Linux reports a FUSE error:** Install the FUSE/AppImage compatibility package supported by your distribution.
- **Windows warns about an unknown publisher:** Confirm the file came from this repository's official Releases page before deciding whether to run it.
- **The app does not start:** Download the release asset again and check the project's GitHub Issues for a matching report.

## Safety

Use network diagnostic features only on systems and networks you own or are authorized to assess.
