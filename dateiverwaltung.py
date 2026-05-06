import csv
import os
from modelle import Modul, Pruefungsleistung, Semester, Studiengang


class CSVVerwalter:
    """Übernimmt die dauerhafte Datenspeicherung und das Laden aus CSV-Dateien."""

    def __init__(self, datei_module: str = "module.csv", datei_noten: str = "noten.csv") -> None:
        self._datei_module = datei_module
        self._datei_noten = datei_noten

    def speichere_daten(self, studiengang: Studiengang) -> None:
        """Speichert alle Module und Noten des Studiengangs in die CSV-Dateien."""
        with open(self._datei_module, mode='w', newline='', encoding='utf-8') as f_mod, \
                open(self._datei_noten, mode='w', newline='', encoding='utf-8') as f_not:
            writer_mod = csv.writer(f_mod)
            writer_not = csv.writer(f_not)

            writer_mod.writerow(["Semester", "Kurs_ID", "Name", "ECTS"])
            writer_not.writerow(["Kurs_ID", "Note"])

            for semester in studiengang.semester_liste:
                for modul in semester.module:
                    writer_mod.writerow([semester.semesternummer, modul.kurs_id, modul.modulname, modul.anzahl_ects])

                    for leistung in modul.pruefungsleistungen:
                        writer_not.writerow([modul.kurs_id, leistung.note])

    def lade_daten(self, studiengang: Studiengang) -> None:
        """Lädt Daten aus den CSV-Dateien und verknüpft sie mit dem Studiengang."""
        if not os.path.exists(self._datei_module) or not os.path.exists(self._datei_noten):
            return

        with open(self._datei_module, mode='r', encoding='utf-8') as f_mod:
            reader_mod = csv.reader(f_mod)
            next(reader_mod)

            for row in reader_mod:
                if not row: continue

                sem_id = int(row[0])
                kurs_id = row[1]
                modulname = row[2]
                ects = int(row[3])

                aktuelles_semester = next((sem for sem in studiengang.semester_liste if sem.semesternummer == sem_id),
                                          None)

                if aktuelles_semester is None:
                    aktuelles_semester = Semester(sem_id)
                    studiengang.semester_hinzufuegen(aktuelles_semester)

                aktuelles_semester.modul_hinzufuegen(Modul(kurs_id, modulname, ects))

        with open(self._datei_noten, mode='r', encoding='utf-8') as f_not:
            reader_not = csv.reader(f_not)
            next(reader_not)

            for row in reader_not:
                if not row: continue
                kurs_id = row[0]
                note = float(row[1])

                neue_leistung = Pruefungsleistung(note)

                gefunden = False
                for sem in studiengang.semester_liste:
                    for mod in sem.module:
                        if mod.kurs_id == kurs_id:
                            mod.pruefungsleistung_eintragen(neue_leistung)
                            gefunden = True
                            break
                    if gefunden:
                        break