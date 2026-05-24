import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QProgressBar,
    QGroupBox, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from ui.params_dialog import ParamsDialog
from core.compressor import KompresijaNit, DekompresijaNit
from core.metrics import formatiraj_velicinu, formatiraj_vreme


class GlavniProzor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HEVC Video Kompresija")
        self.setMinimumSize(600, 650)
        self.kompresija_nit = None
        self.dekompresija_nit = None
        self.podesi_ui()
        self.podesi_meni()

    def podesi_meni(self):
        meni_bar = self.menuBar()

        fajl_meni = meni_bar.addMenu("Fajl")
        otvori_akcija = QAction("Otvori video", self)
        otvori_akcija.triggered.connect(self.izaberi_ulazni_fajl)
        fajl_meni.addAction(otvori_akcija)
        fajl_meni.addSeparator()
        izlaz_akcija = QAction("Izlaz", self)
        izlaz_akcija.triggered.connect(self.close)
        fajl_meni.addAction(izlaz_akcija)

        kompresija_meni = meni_bar.addMenu("Kompresija")
        pokreni_akcija = QAction("Pokreni kompresiju", self)
        pokreni_akcija.triggered.connect(self.pokreni_kompresiju)
        kompresija_meni.addAction(pokreni_akcija)

    def podesi_ui(self):
        centralni_widget = QWidget()
        self.setCentralWidget(centralni_widget)
        glavni_raspored = QVBoxLayout(centralni_widget)
        glavni_raspored.setSpacing(10)
        glavni_raspored.setContentsMargins(20, 20, 20, 20)

        # Ulazni fajl
        ulaz_grupa = QGroupBox("Ulazni video fajl")
        ulaz_raspored = QHBoxLayout()
        self.ulaz_polje = QLineEdit()
        self.ulaz_polje.setPlaceholderText("Izaberite video fajl...")
        self.ulaz_polje.setReadOnly(True)
        ulaz_dugme = QPushButton("Pretraži")
        ulaz_dugme.clicked.connect(self.izaberi_ulazni_fajl)
        ulaz_raspored.addWidget(self.ulaz_polje)
        ulaz_raspored.addWidget(ulaz_dugme)
        ulaz_grupa.setLayout(ulaz_raspored)

        # Izlazni fajl
        izlaz_grupa = QGroupBox("Odredišni fajl")
        izlaz_raspored = QHBoxLayout()
        self.izlaz_polje = QLineEdit()
        self.izlaz_polje.setPlaceholderText("Izaberite lokaciju za čuvanje...")
        izlaz_dugme = QPushButton("Pretraži")
        izlaz_dugme.clicked.connect(self.izaberi_izlazni_fajl)
        izlaz_raspored.addWidget(self.izlaz_polje)
        izlaz_raspored.addWidget(izlaz_dugme)
        izlaz_grupa.setLayout(izlaz_raspored)

        # Dugme
        self.kompresuj_dugme = QPushButton("Kompresuj i Dekompresuj")
        self.kompresuj_dugme.setMinimumHeight(40)
        self.kompresuj_dugme.clicked.connect(self.pokreni_kompresiju)
        self.kompresuj_dugme.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #006cbf; }
            QPushButton:disabled { background-color: #cccccc; }
        """)

        # Progress bar
        progres_grupa = QGroupBox("Progres")
        progres_raspored = QVBoxLayout()
        self.progres_bar = QProgressBar()
        self.progres_bar.setValue(0)
        self.progres_label = QLabel("Spreman za kompresiju")
        self.progres_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progres_raspored.addWidget(self.progres_bar)
        progres_raspored.addWidget(self.progres_label)
        progres_grupa.setLayout(progres_raspored)

        # Metrike kompresije
        metrike_grupa = QGroupBox("Rezultati kompresije")
        metrike_raspored = QVBoxLayout()
        metrike_raspored.setSpacing(4)

        self.original_label = QLabel("Originalni fajl: —")
        self.kompresovan_label = QLabel("Kompresovani fajl: —")
        self.procenat_label = QLabel("Kompresija: —")
        self.vreme_label = QLabel("Vreme kompresije: —")
        self.usteda_label = QLabel("Ušteda prostora: —")

        for label in [
            self.original_label,
            self.kompresovan_label,
            self.procenat_label,
            self.vreme_label,
            self.usteda_label
        ]:
            label.setStyleSheet("font-size: 12px; padding: 2px;")
            metrike_raspored.addWidget(label)

        metrike_grupa.setLayout(metrike_raspored)

        # Metrike dekompresije
        dek_metrike_grupa = QGroupBox("Rezultati dekompresije")
        dek_metrike_raspored = QVBoxLayout()
        dek_metrike_raspored.setSpacing(4)

        self.vreme_dekompresije_label = QLabel("Vreme dekompresije: —")
        self.velicina_dekompresije_label = QLabel(
            "Veličina dekompresovanog fajla: —"
        )

        for label in [
            self.vreme_dekompresije_label,
            self.velicina_dekompresije_label
        ]:
            label.setStyleSheet("font-size: 12px; padding: 2px;")
            dek_metrike_raspored.addWidget(label)

        dek_metrike_grupa.setLayout(dek_metrike_raspored)

        # Dodaj sve
        glavni_raspored.addWidget(ulaz_grupa)
        glavni_raspored.addWidget(izlaz_grupa)
        glavni_raspored.addWidget(self.kompresuj_dugme)
        glavni_raspored.addWidget(progres_grupa)
        glavni_raspored.addWidget(metrike_grupa)
        glavni_raspored.addWidget(dek_metrike_grupa)
        glavni_raspored.addStretch()

    def izaberi_ulazni_fajl(self):
        fajl, _ = QFileDialog.getOpenFileName(
            self,
            "Izaberi video fajl",
            os.path.expanduser("~"),  # uvek pocinje od home foldera
            "Video fajlovi (*.avi *.mov *.mp4 *.mkv *.raw *.yuv);;Svi fajlovi (*)"
        )
        if fajl:
            self.ulaz_polje.setText(fajl)
            # Predlozi izlaz u istom folderu kao ulaz
            folder = os.path.dirname(fajl)
            naziv = os.path.splitext(os.path.basename(fajl))[0]
            self.izlaz_polje.setText(
                os.path.join(folder, f"{naziv}_kompresovan.mp4")
            )

    def izaberi_izlazni_fajl(self):
        # Pocni od foldera ulaznog fajla ako postoji
        pocetni_folder = os.path.expanduser("~")
        if self.ulaz_polje.text():
            pocetni_folder = os.path.dirname(self.ulaz_polje.text())

        fajl, _ = QFileDialog.getSaveFileName(
            self,
            "Sacuvaj kao",
            pocetni_folder,
            "MP4 fajlovi (*.mp4);;MKV fajlovi (*.mkv);;Svi fajlovi (*)"
        )
        if fajl:
            self.izlaz_polje.setText(fajl)

    def pokreni_kompresiju(self):
        ulaz = self.ulaz_polje.text()
        izlaz = self.izlaz_polje.text()

        if not ulaz:
            QMessageBox.warning(self, "Greška", "Izaberite ulazni video fajl.")
            return
        if not izlaz:
            QMessageBox.warning(self, "Greška", "Izaberite odredišni fajl.")
            return

        dijalog = ParamsDialog(self)
        if dijalog.exec() != QDialog.DialogCode.Accepted:
            return

        parametri = dijalog.uzmi_parametre()

        self.kompresuj_dugme.setEnabled(False)
        self.progres_bar.setValue(0)
        self.progres_label.setText("Kompresija u toku...")
        self.ocisti_metrike()

        self.kompresija_nit = KompresijaNit(ulaz, izlaz, parametri)
        self.kompresija_nit.progres.connect(self.azuriraj_progres)
        self.kompresija_nit.zavrsen.connect(self.kompresija_zavrsena)
        self.kompresija_nit.greska.connect(self.kompresija_greska)
        self.kompresija_nit.start()

    def kompresija_zavrsena(self, metrike):
        self.progres_bar.setValue(0)
        self.progres_label.setText(
            "Kompresija završena — pokrećem dekompresiju..."
        )

        # Popuni metrike kompresije
        self.original_label.setText(
            f"Originalni fajl: "
            f"{formatiraj_velicinu(metrike['velicina_originala'])}"
        )
        self.kompresovan_label.setText(
            f"Kompresovani fajl: "
            f"{formatiraj_velicinu(metrike['velicina_izlaza'])}"
        )
        self.procenat_label.setText(
            f"Kompresija: {metrike['procenat_kompresije']:.4f}%"
        )
        self.vreme_label.setText(
            f"Vreme kompresije: {formatiraj_vreme(metrike['vreme'])}"
        )
        self.usteda_label.setText(
            f"Ušteda prostora: "
            f"{formatiraj_velicinu(metrike['usteda'])}"
        )

        # Automatski pokreni dekompresiju
        izlaz_kompresije = self.izlaz_polje.text()
        folder = os.path.dirname(izlaz_kompresije)
        naziv = os.path.splitext(os.path.basename(izlaz_kompresije))[0]
        izlaz_dekompresije = os.path.join(folder, f"{naziv}_dekompresovan.avi")

        self.dekompresija_nit = DekompresijaNit(
            izlaz_kompresije,
            izlaz_dekompresije
        )
        self.dekompresija_nit.progres.connect(self.azuriraj_progres)
        self.dekompresija_nit.zavrsen.connect(self.dekompresija_zavrsena)
        self.dekompresija_nit.greska.connect(self.dekompresija_greska)
        self.dekompresija_nit.start()

    def dekompresija_zavrsena(self, metrike):
        self.kompresuj_dugme.setEnabled(True)
        self.progres_bar.setValue(100)
        self.progres_label.setText("Kompresija i dekompresija završene!")

        self.vreme_dekompresije_label.setText(
            f"Vreme dekompresije: {formatiraj_vreme(metrike['vreme'])}"
        )
        self.velicina_dekompresije_label.setText(
            f"Veličina dekompresovanog fajla: "
            f"{formatiraj_velicinu(metrike['velicina_izlaza'])}"
        )

    def kompresija_greska(self, poruka):
        self.kompresuj_dugme.setEnabled(True)
        self.progres_label.setText("Greška!")
        QMessageBox.critical(self, "Greška pri kompresiji", poruka)

    def dekompresija_greska(self, poruka):
        self.kompresuj_dugme.setEnabled(True)
        self.progres_label.setText("Greška!")
        QMessageBox.critical(self, "Greška pri dekompresiji", poruka)

    def azuriraj_progres(self, vrednost):
        self.progres_bar.setValue(vrednost)

    def ocisti_metrike(self):
        self.original_label.setText("Originalni fajl: —")
        self.kompresovan_label.setText("Kompresovani fajl: —")
        self.procenat_label.setText("Kompresija: —")
        self.vreme_label.setText("Vreme kompresije: —")
        self.usteda_label.setText("Ušteda prostora: —")
        self.vreme_dekompresije_label.setText("Vreme dekompresije: —")
        self.velicina_dekompresije_label.setText(
            "Veličina dekompresovanog fajla: —"
        )