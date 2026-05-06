from modelle import Studiengang
from dateiverwaltung import CSVVerwalter
from gui import DashboardApp
from controller import DashboardController


def main() -> None:
    """
    Der zentrale Einstiegspunkt der Applikation (Composition Root).
    Hier werden alle Kernkomponenten instanziiert und miteinander verknüpft.
    """
    # 1. Domänenmodell instanziieren
    mein_studium = Studiengang("Cyber Security", 180, 8, "01.12.2025")

    # 2. Persistenzschicht (Verwalter) erstellen und bestehende Daten laden
    verwalter = CSVVerwalter()
    verwalter.lade_daten(mein_studium)

    # 3. Service-Schicht (Controller) erstellen und Abhängigkeiten injizieren
    controller = DashboardController(mein_studium, verwalter)

    # 4. View (GUI) erstellen und NUR den Controller übergeben (Dependency Injection)
    app = DashboardApp(controller)

    # 5. Applikation starten
    app.mainloop()


if __name__ == "__main__":
    main()