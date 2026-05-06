from modelle import Studiengang
from dateiverwaltung import CSVVerwalter

class DashboardController:
    """
    Zentrale Service- und Steuerungsschicht (Controller) der Anwendung.
    Nimmt Daten aus der Benutzeroberfläche entgegen, orchestriert die
    Geschäftslogik im Domänenmodell und delegiert die Datenspeicherung.
    """

    def __init__(self, studiengang: Studiengang, verwalter: CSVVerwalter) -> None:
        self._studiengang = studiengang
        self._verwalter = verwalter

    def modul_hinzufuegen(self, kurs_id: str, modulname: str, ects: int) -> None:
        """
        Delegiert das Anlegen eines neuen Moduls an das Domänenmodell
        und triggert bei Erfolg die persistente Speicherung.
        """
        self._studiengang.modul_anlegen(kurs_id, modulname, ects)
        self._verwalter.speichere_daten(self._studiengang)

    def pruefungsleistung_eintragen(self, kurs_id: str, note: float) -> None:
        """
        Delegiert das Eintragen einer neuen Note an das Domänenmodell
        und triggert bei Erfolg die persistente Speicherung.
        """
        self._studiengang.pruefungsleistung_eintragen(kurs_id, note)
        self._verwalter.speichere_daten(self._studiengang)

    @property
    def studiengang(self) -> Studiengang:
        """Gibt das Domänenmodell für Lesezugriffe (View-Aktualisierung) zurück."""
        return self._studiengang