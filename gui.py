import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator
from datetime import datetime
from typing import Callable, List, Optional, Any
from modelle import ModulStatus


class BasisWizard(ctk.CTkToplevel):
    """
    Basisklasse für alle Eingabefenster (Wizards).
    Stellt Hilfsmethoden bereit.
    """

    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.eingabe: Optional[ctk.CTkEntry] = None

    def zeige_warnung(self, nachricht: str) -> None:
        """Zeigt ein temporäres Warnfenster an."""
        warnung = ctk.CTkToplevel(self)
        warnung.title("Warnung")
        warnung.geometry("300x150")
        warnung.attributes("-topmost", True)
        warnung.grab_set()
        lbl = ctk.CTkLabel(warnung, text=nachricht, font=("Arial", 14), wraplength=250)
        lbl.pack(pady=30)
        btn = ctk.CTkButton(warnung, text="OK", command=warnung.destroy)
        btn.pack()
        warnung.bind("<Return>", lambda _event: warnung.destroy())

    def fenster_leeren(self) -> None:
        """Entfernt alle aktuellen Widgets aus dem Fenster."""
        for widget in self.winfo_children():
            if not isinstance(widget, ctk.CTkToplevel):
                widget.destroy()

    def erstelle_eingabe_schritt(self, label_text: str, button_text: str, command_func: Callable) -> None:
        """Hilfsmethode, um einen typischen Eingabeschritt zu zeichnen."""
        self.fenster_leeren()
        lbl = ctk.CTkLabel(self, text=label_text, font=("Arial", 16, "bold"))
        lbl.pack(pady=20)

        neues_eingabefeld = ctk.CTkEntry(self, width=200)
        neues_eingabefeld.pack(pady=10)
        neues_eingabefeld.focus()
        neues_eingabefeld.bind("<Return>", command_func)

        self.eingabe = neues_eingabefeld

        btn = ctk.CTkButton(self, text=button_text, command=command_func)
        btn.pack(pady=10)


class ModulWizard(BasisWizard):
    """
    Wizard zur Erfassung der Daten für ein neues Modul.
    Besitzt keine Kenntnis über das Domänenmodell.
    """

    def __init__(self, parent: Any, existierende_ids: List[str], existierende_namen: List[str],
                 callback_speichern: Callable[[str, str, int], None]) -> None:
        super().__init__(parent)
        self.existierende_ids = existierende_ids
        self.existierende_namen = existierende_namen
        self.callback_speichern = callback_speichern

        self.title("Modul hinzufügen")
        self.geometry("450x200")
        self.attributes("-topmost", True)

        self.kurs_id = ""
        self.modulname = ""
        self.ects = 0

        self.zeige_schritt_1()

    def zeige_schritt_1(self) -> None:
        self.erstelle_eingabe_schritt("Kurs ID eingeben:", "Weiter", self.verarbeite_schritt_1)

    def verarbeite_schritt_1(self, _event: Any = None) -> None:
        if self.eingabe is None:
            return

        wert = self.eingabe.get().strip()
        if not wert:
            self.zeige_warnung("Bitte eine Kurs ID eingeben!")
            return

        if wert.lower() in self.existierende_ids:
            self.zeige_warnung(f"Die Kurs ID '{wert}' ist schon vorhanden!")
            return

        self.kurs_id = wert
        self.zeige_schritt_2()

    def zeige_schritt_2(self) -> None:
        self.erstelle_eingabe_schritt("Modulname eingeben:", "Weiter", self.verarbeite_schritt_2)

    def verarbeite_schritt_2(self, _event: Any = None) -> None:
        if self.eingabe is None:
            return

        wert = self.eingabe.get().strip()
        if not wert:
            self.zeige_warnung("Bitte einen Modulnamen eingeben!")
            return

        if wert.lower() in self.existierende_namen:
            self.zeige_warnung(f"Der Modulname '{wert}' ist schon vorhanden!")
            return

        self.modulname = wert
        self.zeige_schritt_3()

    def zeige_schritt_3(self) -> None:
        self.erstelle_eingabe_schritt("ECTS eingeben:", "Fertig", self.verarbeite_schritt_3)

    def verarbeite_schritt_3(self, _event: Any = None) -> None:
        if self.eingabe is None:
            return

        wert = self.eingabe.get().strip()
        if not wert:
            self.zeige_warnung("Bitte ECTS eingeben!")
            return

        try:
            self.ects = int(wert)
            if self.ects <= 0 or self.ects > 30:
                self.zeige_warnung("Fehler: ECTS müssen zwischen 1 und 30 liegen!")
                return
        except ValueError:
            self.zeige_warnung("Fehler: ECTS muss eine ganze Zahl sein!")
            return

        self.callback_speichern(self.kurs_id, self.modulname, self.ects)
        self.destroy()


class PruefungsleistungWizard(BasisWizard):
    """
    Wizard zur Erfassung einer neuen Note.
    Erhält eine fertige Liste an Modulen von der Haupt-App.
    """

    def __init__(self, parent: Any, modul_auswahl: List[str], callback_speichern: Callable[[str, float], None]) -> None:
        super().__init__(parent)
        self.callback_speichern = callback_speichern
        self.modul_auswahl = modul_auswahl

        self.title("Prüfungsleistung hinzufügen")
        self.geometry("450x200")
        self.attributes("-topmost", True)

        self.gewaehlte_kurs_id = ""
        self.dropdown: Optional[ctk.CTkOptionMenu] = None

        self.zeige_schritt_1()

    def zeige_schritt_1(self) -> None:
        self.fenster_leeren()
        lbl = ctk.CTkLabel(self, text="Wähle das Modul aus:", font=("Arial", 16, "bold"))
        lbl.pack(pady=20)

        neues_dropdown = ctk.CTkOptionMenu(self, values=self.modul_auswahl, width=250)
        neues_dropdown.pack(pady=10)
        self.dropdown = neues_dropdown

        self.bind("<Return>", self.verarbeite_schritt_1)
        btn = ctk.CTkButton(self, text="Weiter", command=self.verarbeite_schritt_1)
        btn.pack(pady=10)

    def verarbeite_schritt_1(self, _event: Any = None) -> None:
        if self.dropdown is None:
            return

        auswahl = self.dropdown.get()
        self.gewaehlte_kurs_id = auswahl.split(",")[0].strip()

        self.unbind("<Return>")
        self.zeige_schritt_2()

    def zeige_schritt_2(self) -> None:
        self.erstelle_eingabe_schritt("Note eingeben:", "Fertig", self.verarbeite_schritt_2)

    def verarbeite_schritt_2(self, _event: Any = None) -> None:
        if self.eingabe is None:
            return

        wert = self.eingabe.get().strip()
        wert = wert.replace(",", ".")
        if not wert:
            self.zeige_warnung("Bitte eine Note eingeben!")
            return

        try:
            note = float(wert)
            if not (1.0 <= note <= 5.0):
                self.zeige_warnung("Fehler: Note muss zwischen 1.0 und 5.0 liegen!")
                return
        except ValueError:
            self.zeige_warnung("Fehler: Note muss eine Zahl sein (z.B. 2.3)!")
            return

        self.callback_speichern(self.gewaehlte_kurs_id, note)
        self.destroy()


class DashboardApp(ctk.CTk):
    """
    Hauptfenster der Applikation (View).
    Fängt Interaktionen ab und kommuniziert ausschließlich mit dem Controller.
    """

    def __init__(self, controller: Any) -> None:
        super().__init__()
        self.controller = controller

        studiengang = self.controller.studiengang

        self.title("Studium - Dashboard")
        self.geometry("1000x650")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.titel_label = None
        self.content_frame = None
        self.left_frame = None
        self.schnitt_box = None
        self.schnitt_titel = None
        self.schnitt_label = None
        self.fortschritt_box = None
        self.fortschritt_titel = None
        self.progress_canvas = None
        self.right_frame = None
        self.figure = None
        self.ax = None
        self.canvas = None

        self.erstelle_widgets(studiengang.name)

    def erstelle_widgets(self, studiengang_name: str) -> None:
        self.titel_label = ctk.CTkLabel(self, text=f"Studium-Dashboard: {studiengang_name}",
                                        font=("Arial", 44, "bold"))
        self.titel_label.pack(pady=(20, 10))

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.schnitt_box = ctk.CTkFrame(self.left_frame)
        self.schnitt_box.pack(fill="both", expand=True, pady=(0, 10))

        self.schnitt_titel = ctk.CTkLabel(self.schnitt_box, text="Durchschnittsnote", font=("Arial", 18, "bold"))
        self.schnitt_titel.pack(pady=(30, 0))

        self.schnitt_label = ctk.CTkLabel(self.schnitt_box, text="-", font=("Arial", 80, "bold"))
        self.schnitt_label.pack(pady=(10, 30))

        self.fortschritt_box = ctk.CTkFrame(self.left_frame)
        self.fortschritt_box.pack(fill="both", expand=True, pady=(10, 0))

        self.fortschritt_titel = ctk.CTkLabel(self.fortschritt_box, text="Studium - Fortschritt",
                                              font=("Arial", 18, "bold"))
        self.fortschritt_titel.pack(pady=(15, 0))

        self.progress_canvas = ctk.CTkCanvas(self.fortschritt_box, width=380, height=140, bg="#2b2b2b",
                                             highlightthickness=0)
        self.progress_canvas.pack(pady=(5, 15))

        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.figure, self.ax = plt.subplots(figsize=(5, 4), facecolor='#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')

        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=20, fill="x", padx=50)

        btn_add_modul = ctk.CTkButton(button_frame, text="Modul hinzufügen", font=("Arial", 18), height=50,
                                      command=self.oeffne_modul_wizard)
        btn_add_modul.pack(side="left", expand=True, padx=20)

        btn_add_note = ctk.CTkButton(button_frame, text="Prüfungsleistung hinzufügen", font=("Arial", 18), height=50,
                                     command=self.oeffne_leistung_wizard)
        btn_add_note.pack(side="right", expand=True, padx=20)

        self.aktualisiere_anzeigen()

    def oeffne_modul_wizard(self) -> None:
        studiengang = self.controller.studiengang
        existierende_ids = []
        existierende_namen = []

        for sem in studiengang.semester_liste:
            for mod in sem.module:
                existierende_ids.append(mod.kurs_id.lower())
                existierende_namen.append(mod.modulname.lower())

        ModulWizard(self, existierende_ids, existierende_namen, self.aktion_modul_hinzufuegen_speichern)

    def aktion_modul_hinzufuegen_speichern(self, kurs_id: str, modulname: str, ects: int) -> None:
        try:
            self.controller.modul_hinzufuegen(kurs_id, modulname, ects)
            self.aktualisiere_anzeigen()
        except ValueError as e:
            self.zeige_haupt_warnung(str(e))

    def zeige_haupt_warnung(self, nachricht: str) -> None:
        warnung = ctk.CTkToplevel(self)
        warnung.title("Hinweis")
        warnung.geometry("350x150")
        warnung.attributes("-topmost", True)
        lbl = ctk.CTkLabel(warnung, text=nachricht, font=("Arial", 14), wraplength=300)
        lbl.pack(pady=30)
        btn = ctk.CTkButton(warnung, text="OK", command=warnung.destroy)
        btn.pack()
        warnung.bind("<Return>", lambda _event: warnung.destroy())

    def oeffne_leistung_wizard(self) -> None:
        studiengang = self.controller.studiengang
        modul_auswahl = []

        for sem in studiengang.semester_liste:
            for mod in sem.module:
                if mod.status == ModulStatus.OFFEN:
                    modul_auswahl.append(f"{mod.kurs_id}, {mod.modulname}")

        if not modul_auswahl:
            self.zeige_haupt_warnung(
                "Es gibt aktuell keine offenen Module! Alle angelegten Module sind bereits bestanden, haben keine Versuche mehr oder es wurden noch keine angelegt.")
            return

        PruefungsleistungWizard(self, modul_auswahl, self.aktion_leistung_hinzufuegen_speichern)

    def aktion_leistung_hinzufuegen_speichern(self, kurs_id: str, note: float) -> None:
        try:
            self.controller.pruefungsleistung_eintragen(kurs_id, note)
            self.aktualisiere_anzeigen()
        except ValueError as e:
            self.zeige_haupt_warnung(str(e))

    def aktualisiere_anzeigen(self) -> None:
        studiengang = self.controller.studiengang
        ects_ist = studiengang.berechne_gesamt_ects()
        gesamt = studiengang.gesamt_ects
        schnitt = studiengang.berechne_notendurchschnitt()

        anzeige_schnitt = f"{schnitt:.1f}" if schnitt > 0 else "-"
        self.schnitt_label.configure(text=anzeige_schnitt)

        self.progress_canvas.delete("all")

        x0, x1 = 30, 350
        y0, y1 = 70, 95

        heute = datetime.now()
        start = studiengang.studienstart
        monate_vergangen = (heute.year - start.year) * 12 + (heute.month - start.month)

        gesamt_monate = studiengang.regelstudienzeit_semester * 6
        ects_pro_monat = gesamt / gesamt_monate if gesamt_monate > 0 else 5
        theoretische_ects = max(0, monate_vergangen * ects_pro_monat)

        soll = int(theoretische_ects // 5) * 5
        soll = min(soll, gesamt)

        ist_x = x0 + (ects_ist / gesamt) * (x1 - x0) if gesamt > 0 else x0
        soll_x = x0 + (soll / gesamt) * (x1 - x0) if gesamt > 0 else x0

        self.progress_canvas.create_rectangle(x0, y0, x1, y1, fill="#444444", outline="")
        self.progress_canvas.create_rectangle(x0, y0, ist_x, y1, fill="#1f538d", outline="")

        self.progress_canvas.create_text(x0, y1 + 15, text="0 ECTS", fill="white", font=("Arial", 14), anchor="w")
        self.progress_canvas.create_text(x1, y1 + 15, text=f"{gesamt} ECTS", fill="white", font=("Arial", 14),
                                         anchor="e")

        self.progress_canvas.create_line(soll_x, y0 - 45, soll_x, y1 + 10, fill="#e63946", dash=(4, 4), width=2)
        self.progress_canvas.create_text(soll_x, y0 - 50, text=f"SOLL: {soll}", fill="#e63946",
                                         font=("Arial", 14, "bold"), anchor="s")

        self.progress_canvas.create_text(ist_x, y0 - 15, text=f"IST: {ects_ist}", fill="#6ea8fe",
                                         font=("Arial", 14, "bold"), anchor="s")

        self.ax.clear()

        max_sem = 8
        for sem in studiengang.semester_liste:
            if sem.semesternummer > max_sem:
                max_sem = sem.semesternummer

        x_semester = [str(i) for i in range(1, max_sem + 1)]
        y_ects = [0] * max_sem

        for sem in studiengang.semester_liste:
            if 1 <= sem.semesternummer <= max_sem:
                y_ects[sem.semesternummer - 1] = sem.berechne_semester_ects()

        self.ax.bar(x_semester, y_ects, color='#1f538d')

        self.ax.set_title("ECTS pro Semester", color='white', pad=15, fontdict={'weight': 'bold'})
        self.ax.set_xlabel("Semester", color='white', labelpad=10)
        self.ax.set_ylabel("Erreichte ECTS", color='white')

        hoechster_wert = max(y_ects) if y_ects else 0

        if hoechster_wert < 20:
            self.ax.set_ylim(0, 20)
        else:
            self.ax.set_ylim(0, hoechster_wert + 5)

        self.ax.yaxis.set_major_locator(MultipleLocator(5))

        self.ax.grid(axis='y', linestyle='--', alpha=0.3)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')

        self.canvas.draw()