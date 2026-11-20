import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def resource_path(relative_path: str) -> Path:
    """Resolve bundled assets in both development and PyInstaller builds."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("NetOps Toolkit")
    icon_path = resource_path("assets/netops-toolkit.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
