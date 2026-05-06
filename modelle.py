import math
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ModulStatus(Enum):
    """Repräsentiert den aktuellen Status eines Moduls."""
    OFFEN = "Offen"
    BESTANDEN = "Bestanden"
    ENDGUELTIG_DURCHGEFALLEN = "Endgültig durchgefallen"


class Pruefungsleistung:
    """Kapselt eine einzelne erbrachte Prüfungsleistung (Note)."""

    def __init__(self, note: float) -> None:
        note_float = float(note)
        if not (1.0 <= note_float <= 5.0):
            raise ValueError("Die Note muss zwischen 1.0 und 5.0 liegen!")
        self._note = note_float

    @property
    def note(self) -> float:
        """Gibt die Note als numerischen Wert zurück."""
        return self._note

    @property
    def bestanden(self) -> bool:
        """Prüft, ob die Leistung mit 4.0 oder besser bestanden wurde."""
        return self._note <= 4.0


class Modul:
    """Repräsentiert ein einzelnes Modul im Curriculum."""

    def __init__(self, kurs_id: str, modulname: str, anzahl_ects: int) -> None:
        ects = int(anzahl_ects)
        if ects <= 0 or ects > 30:
            raise ValueError("Die ECTS müssen zwischen 1 und 30 liegen!")

        self._kurs_id = kurs_id
        self._modulname = modulname
        self._anzahl_ects = ects
        self._pruefungsleistungen: List[Pruefungsleistung] = []

    @property
    def kurs_id(self) -> str:
        """Gibt die eindeutige Kurs-ID des Moduls zurück."""
        return self._kurs_id

    @property
    def modulname(self) -> str:
        """Gibt den Namen des Moduls zurück."""
        return self._modulname

    @property
    def anzahl_ects(self) -> int:
        """Gibt die Anzahl der ECTS-Punkte für dieses Modul zurück."""
        return self._anzahl_ects

    @property
    def pruefungsleistungen(self) -> List[Pruefungsleistung]:
        """Gibt eine Liste aller erbrachten Prüfungsleistungen zurück."""
        return self._pruefungsleistungen

    def pruefungsleistung_eintragen(self, leistung: Pruefungsleistung) -> None:
        """Fügt dem Modul eine neue Prüfungsleistung hinzu."""
        if self.status == ModulStatus.BESTANDEN:
            raise ValueError("Modul ist bereits bestanden!")
        if self.status == ModulStatus.ENDGUELTIG_DURCHGEFALLEN:
            raise ValueError("Keine Prüfung mehr für dieses Modul möglich!")
        self._pruefungsleistungen.append(leistung)

    def get_aktuelle_note(self) -> Optional[float]:
        """Gibt die Note des bestandenen Versuchs oder des letzten Fehlversuchs zurück."""
        for p in self._pruefungsleistungen:
            if p.bestanden:
                return p.note

        if len(self._pruefungsleistungen) > 0:
            letzter_versuch = self._pruefungsleistungen[-1]
            return letzter_versuch.note

        return None

    @property
    def ist_bestanden(self) -> bool:
        """Prüft, ob mindestens eine Prüfungsleistung bestanden ist."""
        return any(p.bestanden for p in self._pruefungsleistungen)

    @property
    def status(self) -> ModulStatus:
        """Ermittelt den aktuellen Bestehensstatus des Moduls."""
        if self.ist_bestanden:
            return ModulStatus.BESTANDEN
        if len(self._pruefungsleistungen) >= 3:
            return ModulStatus.ENDGUELTIG_DURCHGEFALLEN
        return ModulStatus.OFFEN


class Semester:
    """Repräsentiert ein einzelnes Semester mit seinen Modulen."""

    def __init__(self, semesternummer: int, soll_ects: int = 22) -> None:
        self._semesternummer = int(semesternummer)
        self._soll_ects = int(soll_ects)
        self._module: List[Modul] = []

    @property
    def semesternummer(self) -> int:
        """Gibt die Nummer des Semesters zurück."""
        return self._semesternummer

    @property
    def module(self) -> List[Modul]:
        """Gibt die Liste der dem Semester zugeordneten Module zurück."""
        return self._module

    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Fügt dem Semester ein neues Modul hinzu."""
        self._module.append(modul)

    def berechne_semester_ects(self) -> int:
        """Berechnet die Summe der ECTS aller bestandenen Module im Semester."""
        summe = 0
        for m in self._module:
            if m.ist_bestanden:
                summe += m.anzahl_ects
        return summe


class Studiengang:
    """Repräsentiert den gesamten Studiengang als zentrales Domänenmodell."""

    def __init__(self, name: str, gesamt_ects: int, regelstudienzeit_semester: int, studienstart_datum: str) -> None:
        self._name = name
        self._gesamt_ects = int(gesamt_ects)
        self._regelstudienzeit_semester = regelstudienzeit_semester
        self._studienstart = datetime.strptime(studienstart_datum, "%d.%m.%Y")
        self._semester_liste: List[Semester] = []

    @property
    def semester_liste(self) -> List[Semester]:
        """Gibt alle angelegten Semester des Studiengangs zurück."""
        return self._semester_liste

    @property
    def name(self) -> str:
        """Gibt den Namen des Studiengangs zurück."""
        return self._name

    @property
    def regelstudienzeit_semester(self) -> int:
        """Gibt die vorgesehene Regelstudienzeit in Semestern zurück."""
        return self._regelstudienzeit_semester

    @property
    def studienstart(self) -> datetime:
        """Gibt das Datum des Studienstarts zurück."""
        return self._studienstart

    @property
    def gesamt_ects(self) -> int:
        """Gibt die zu erreichenden Gesamt-ECTS des Studiengangs zurück."""
        return self._gesamt_ects

    def modul_anlegen(self, kurs_id: str, modulname: str, ects: int) -> None:
        """Legt ein neues Modul im passenden Semester an."""
        for sem in self._semester_liste:
            for mod in sem.module:
                if mod.kurs_id.lower() == kurs_id.lower():
                    raise ValueError("Kurs ID ist schon vorhanden!")
                if mod.modulname.lower() == modulname.lower():
                    raise ValueError("Modulname ist schon vorhanden!")

        aktuelles_sem_nummer = self.get_aktuelles_semester()
        ziel_semester = next((sem for sem in self._semester_liste if sem.semesternummer == aktuelles_sem_nummer), None)

        if ziel_semester is None:
            ziel_semester = Semester(aktuelles_sem_nummer)
            self.semester_hinzufuegen(ziel_semester)

        ziel_semester.modul_hinzufuegen(Modul(kurs_id, modulname, ects))

    def pruefungsleistung_eintragen(self, kurs_id: str, note: float) -> None:
        """Trägt eine neue Prüfungsleistung für ein bestimmtes Modul ein."""
        for sem in self._semester_liste:
            for mod in sem.module:
                if mod.kurs_id == kurs_id:
                    neue_pruefungsleistung = Pruefungsleistung(note)
                    mod.pruefungsleistung_eintragen(neue_pruefungsleistung)
                    return
        raise ValueError(f"Modul mit der ID {kurs_id} wurde nicht gefunden.")

    def get_aktuelles_semester(self) -> int:
        """Berechnet das aktuelle Semester basierend auf dem Studienstart."""
        heute = datetime.now()
        monate_vergangen = (heute.year - self._studienstart.year) * 12 + (heute.month - self._studienstart.month)
        aktuelles_semester = math.ceil((monate_vergangen + 1) / 6)
        return max(1, aktuelles_semester)

    def berechne_notendurchschnitt(self) -> float:
        """Berechnet den nach ECTS gewichteten Notendurchschnitt."""
        summe_gewichtete_noten = 0.0
        gesamt_ects_bestanden = 0

        for s in self._semester_liste:
            for m in s.module:
                if m.ist_bestanden:
                    note = m.get_aktuelle_note()
                    ects = m.anzahl_ects
                    if note is not None:
                        summe_gewichtete_noten += (note * ects)
                    gesamt_ects_bestanden += ects

        if gesamt_ects_bestanden == 0:
            return 0.0

        durchschnitt = summe_gewichtete_noten / gesamt_ects_bestanden
        return round(durchschnitt, 2)

    def berechne_gesamt_ects(self) -> int:
        """Berechnet die Summe aller bisher erreichten ECTS-Punkte."""
        gesamt_ects = 0
        for s in self._semester_liste:
            gesamt_ects += s.berechne_semester_ects()
        return gesamt_ects

    def semester_hinzufuegen(self, semester: Semester) -> None:
        """Fügt dem Studiengang ein neues Semester hinzu."""
        self._semester_liste.append(semester)