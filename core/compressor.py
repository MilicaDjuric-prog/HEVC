import ffmpeg
import time
import os
from PyQt6.QtCore import QThread, pyqtSignal


class KompresijaNit(QThread):
    progres = pyqtSignal(int)
    zavrsen = pyqtSignal(dict)
    greska = pyqtSignal(str)

    def __init__(self, ulaz, izlaz, parametri):
        super().__init__()
        self.ulaz = ulaz
        self.izlaz = izlaz
        self.parametri = parametri

    def run(self):
        try:
            velicina_originala = os.path.getsize(self.ulaz)
            pocetak = time.time()
            stream = ffmpeg.input(self.ulaz)

            if self.parametri['rezolucija'] != 'Originalna':
                visina = int(self.parametri['rezolucija'].replace('p', ''))
                stream = ffmpeg.filter(stream, 'scale', -2, visina)

            codec_mapa = {
                'HEVC': 'libx265',
                'H.264': 'libx264',
                'MPEG-2': 'mpeg2video',
                'VP9': 'libvpx-vp9'
            }
            codec = codec_mapa[self.parametri['format']]

            self.progres.emit(10)

            
            if self.parametri['format'] in ['HEVC', 'H.264']:
                (
                    ffmpeg
                    .output(stream, self.izlaz,
                            vcodec=codec,
                            crf=self.parametri['crf'],
                            preset=self.parametri['preset'])
                    .overwrite_output()
                    .run(quiet=True)
                )
            else:
                (
                    ffmpeg
                    .output(stream, self.izlaz,
                            vcodec=codec,
                            crf=self.parametri['crf'])
                    .overwrite_output()
                    .run(quiet=True)
                )

            self.progres.emit(100)

            vreme = time.time() - pocetak
            velicina_izlaza = os.path.getsize(self.izlaz)
            procenat = (1 - velicina_izlaza / velicina_originala) * 100
            usteda = velicina_originala - velicina_izlaza

            self.zavrsen.emit({
                'velicina_originala': velicina_originala,
                'velicina_izlaza': velicina_izlaza,
                'procenat_kompresije': procenat,
                'vreme': vreme,
                'usteda': usteda
            })

        except Exception as e:
            self.greska.emit(str(e))


#  DekompresijaNit pocinje ovde, van KompresijaNit klase
class DekompresijaNit(QThread):
    progres = pyqtSignal(int)
    zavrsen = pyqtSignal(dict)
    greska = pyqtSignal(str)

    def __init__(self, ulaz, izlaz):
        super().__init__()
        self.ulaz = ulaz
        self.izlaz = izlaz

    def run(self):
        try:
            velicina_originala = os.path.getsize(self.ulaz)
            pocetak = time.time()

            self.progres.emit(10)

            (
                ffmpeg
                .input(self.ulaz)
                .output(self.izlaz, vcodec='rawvideo')
                .overwrite_output()
                .run(quiet=True)
            )

            self.progres.emit(100)

            vreme = time.time() - pocetak
            velicina_izlaza = os.path.getsize(self.izlaz)

            self.zavrsen.emit({
                'velicina_originala': velicina_originala,
                'velicina_izlaza': velicina_izlaza,
                'vreme': vreme
            })

        except Exception as e:
            self.greska.emit(str(e))