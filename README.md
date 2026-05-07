Installationsanleitung

Portfolio: Studium-Dashboard

1.	GitHub-Repository

    Der gesamte Quellcode inklusive dieser Dokumentation ist unter folgendem Link verfügbar:

    https://github.com/DennisG44/Studien_Dashboard.git

3.	Systemvoraussetzungen

  	Um das Programm erfolgreich auszuführen, werden folgende Komponenten benötigt:
  	- Ein aktuelles Windows-Betriebssystem (getestet unter Windows 10/11)
    - Python 3.14 oder neuer (inklusive pip zur Paketverwaltung)

5.	Installation und Start
    
    Folgen Sie diesen einfachen Schritten, um das Dashboard auf Ihrem System zu starten:

    Schritt 1: Programmcode herunterladen
    1. Öffnen Sie den oben genannten GitHub-Link in Ihrem Browser.
    2. Klicken Sie auf die grüne Schaltfläche "Code" und wählen Sie "Download ZIP".
    3. Entpacken Sie den Inhalt der ZIP-Datei in einen beliebigen Ordner auf Ihrem Computer.


    Schritt 2: In das Projektverzeichnis wechseln

  	Öffnen Sie den gerade entpackten Ordner im Windows Explorer.
    Klicken Sie oben in die Adresszeile des Ordners, löschen Sie den Text, tippen Sie einfach cmd ein und drücken Sie Enter. Dadurch öffnet sich das Terminal (die Eingabeaufforderung) automatisch im richtigen Verzeichnis.

    Schritt 3: Abhängigkeiten installieren

  	Das Dashboard benötigt die Bibliotheken customtkinter und matplotlib. Führen Sie den folgenden Befehl in der Eingabeaufforderung aus:

  	pip install customtkinter matplotlib

    Schritt 4: Programm starten

  	Nachdem die Pakete installiert wurden, können Sie die Anwendung über die Hauptdatei starten. Geben Sie dazu im Terminal folgenden Befehl ein:

  	python main.py
