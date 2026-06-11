from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox,
    QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt


class ParamsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parametri kompresije")
        self.setMinimumWidth(400)
        self.podesi_ui()

    def podesi_ui(self):
        glavni_raspored = QVBoxLayout()

        # Format
        format_grupa = QGroupBox("Format izlaza")
        format_raspored = QVBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(['HEVC', 'H.264', 'MPEG-2', 'VP9'])
        format_raspored.addWidget(self.format_combo)
        format_grupa.setLayout(format_raspored)

        # CRF kvalitet
        crf_grupa = QGroupBox("Kvalitet kompresije")
        crf_raspored = QVBoxLayout()

        crf_opis = QLabel("Manji broj = bolji kvalitet, veći fajl")
        crf_opis.setStyleSheet("color: gray; font-size: 11px;")

        crf_vrednost_raspored = QHBoxLayout()
        self.crf_label = QLabel("CRF: 28")
        self.crf_label.setMinimumWidth(70)

        self.crf_slider = QSlider(Qt.Orientation.Horizontal)
        self.crf_slider.setMinimum(0)
        self.crf_slider.setMaximum(51)
        self.crf_slider.setValue(28)
        self.crf_slider.valueChanged.connect(self.azuriraj_crf)

        crf_vrednost_raspored.addWidget(self.crf_label)
        crf_vrednost_raspored.addWidget(self.crf_slider)

        crf_raspored.addWidget(crf_opis)
        crf_raspored.addLayout(crf_vrednost_raspored)
        crf_grupa.setLayout(crf_raspored)

        # Rezolucija
        rezolucija_grupa = QGroupBox("Rezolucija izlaza")
        rezolucija_raspored = QVBoxLayout()
        self.rezolucija_combo = QComboBox()
        self.rezolucija_combo.addItems([
            'Originalna', '1080p', '720p', '480p'
        ])
        rezolucija_raspored.addWidget(self.rezolucija_combo)
        rezolucija_grupa.setLayout(rezolucija_raspored)

        # Dugmad
        dugmad_raspored = QHBoxLayout()
        self.otkazi_dugme = QPushButton("Otkaži")
        self.kompresuj_dugme = QPushButton("Kompresuj")
        self.kompresuj_dugme.setDefault(True)

        self.otkazi_dugme.clicked.connect(self.reject)
        self.kompresuj_dugme.clicked.connect(self.accept)

        dugmad_raspored.addWidget(self.otkazi_dugme)
        dugmad_raspored.addWidget(self.kompresuj_dugme)

        # Dodaj sve u glavni raspored
        glavni_raspored.addWidget(format_grupa)
        glavni_raspored.addWidget(crf_grupa)
        glavni_raspored.addWidget(rezolucija_grupa)
        glavni_raspored.addLayout(dugmad_raspored)

        self.setLayout(glavni_raspored)

    def azuriraj_crf(self, vrednost):
        self.crf_label.setText(f"CRF: {vrednost}")

    def uzmi_parametre(self):
        return {
            'format': self.format_combo.currentText(),
            'crf': self.crf_slider.value(),
            'rezolucija': self.rezolucija_combo.currentText()
        }