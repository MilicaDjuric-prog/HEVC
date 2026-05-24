import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import GlavniProzor


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HEVC Video Kompresija")
    
    prozor = GlavniProzor()
    prozor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()