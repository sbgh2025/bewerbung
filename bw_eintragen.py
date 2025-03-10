import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from datetime import date


# Funktion, um eine Verbindung zur Datenbank herzustellen
def connect_db():
    return sqlite3.connect('Bewerbungsadressat.db')


# Funktion, um eine Datei auszuwählen
def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("Alle Dateien", "*.*"),
                                                     ("PDF Files", "*.pdf"),
                                                     ])
    entry_stellenanzeige.delete(0, tk.END)  # Vorherigen Text löschen
    if filepath:  # Wenn eine Datei ausgewählt wurde
        entry_stellenanzeige.insert(0, filepath)  # Den Pfad der Datei einfügen
    else:  # Wenn der Benutzer keine Datei auswählt
        entry_stellenanzeige.insert(0, '')  # Leeres Feld


# Funktion, um einen neuen Datensatz in die Tabelle 'Bewerbungen' einzutragen
def insert_bewerbung():
    datum = entry_datum_bewerbung.get()
    firma = entry_firma.get()
    ansprechpartner = entry_ansprechpartner.get()
    kontakt = entry_kontakt.get()
    stellenbezeichnung = entry_stellenbezeichnung.get()
    stellenanzeige_path = entry_stellenanzeige.get()

    stellenanzeige_data = None  # Standardmäßig setzen wir das auf None

    if stellenanzeige_path:
        try:
            with open(stellenanzeige_path, 'rb') as file:
                stellenanzeige_data = file.read()  # Binärdaten der Datei lesen
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Die angegebene Datei wurde nicht gefunden.")
            return
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")
            return

    conn = connect_db()
    c = conn.cursor()

    try:
        c.execute('''
        INSERT INTO Bewerbungen (datum, firma, ansprechpartner, kontakt, stellenbezeichnung, stellenanzeige)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (datum, firma, ansprechpartner, kontakt, stellenbezeichnung, stellenanzeige_data))
        conn.commit()
        messagebox.showinfo("Erfolg", "Bewerbung wurde erfolgreich hinzugefügt!")

        # Hinweis auf die Datei
        if stellenanzeige_path:
            messagebox.showinfo("Datei gespeichert",
                                f"Die Datei wurde unter folgendem Pfad gespeichert:\n{stellenanzeige_path}")

    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Hinzufügen der Bewerbung: {e}")
    finally:
        conn.close()

    # Bewerbungen neu laden
    show_bewerbungen()


# Funktion, um alle Bewerbungen anzuzeigen (zum Auswählen einer Bewerbung)
def show_bewerbungen():
    conn = connect_db()
    c = conn.cursor()

    # Je nach Auswahl die Bewerbungen nach Datum oder Firma sortieren
    sortierung = sortierung_combobox.get()
    if sortierung == 'Nach Datum':
        c.execute('SELECT id, datum, firma FROM Bewerbungen ORDER BY datum DESC')
    elif sortierung == 'Nach Firma':
        c.execute('SELECT id, datum, firma FROM Bewerbungen ORDER BY firma ASC')

    bewerbungen = c.fetchall()

    # Bewerbungen in der Auswahl anzeigen
    bewerbung_combobox['values'] = [f"{bewerbung[0]} - {bewerbung[1]} - {bewerbung[2]}" for bewerbung in bewerbungen]
    if bewerbungen:
        bewerbung_combobox.set(bewerbung_combobox['values'][0])  # Standardmäßig erste Bewerbung auswählen
    conn.close()


# Funktion, um eine Reaktion hinzuzufügen
def reaktion_hinzufuegen():
    bewerbung_id = int(bewerbung_combobox.get().split(" - ")[0])  # Extrahiere die ID aus dem ausgewählten Text
    reaktion_name = reaktion_combobox.get()
    bemerkung = bemerkung_text.get("1.0", "end-1c")  # Textfeldinhalt holen

    reaktion_datum = datum_entry.get()
    if not reaktion_datum:  # Wenn das Datum nicht eingegeben wurde, aktuelles Datum verwenden
        reaktion_datum = date.today().strftime("%Y-%m-%d")

    conn = connect_db()
    c = conn.cursor()

    c.execute('SELECT id FROM Reaktion WHERE reaktion = ?', (reaktion_name,))
    reaktion_id = c.fetchone()[0]  # Hole die erste ID (Erwartet, dass genau eine Zeile zurückgegeben wird)

    # Einfügen der Daten in die Tabelle 'Reaktionen_Bewerbung'
    c.execute('''
    INSERT INTO Reaktionen_Bewerbung (datum, bewerbung_id, reaktion_id, bemerkung)
    VALUES (?, ?, ?, ?)
    ''', (reaktion_datum, bewerbung_id, reaktion_id, bemerkung))

    conn.commit()
    conn.close()

    status_label.config(text="Reaktion erfolgreich hinzugefügt!")


# Verbindung zur SQLite-Datenbank herstellen
conn = connect_db()
c = conn.cursor()

# Sicherstellen, dass die Tabelle 'Reaktion' mit Standardwerten befüllt ist
c.execute('SELECT COUNT(*) FROM Reaktion')
if c.fetchone()[0] == 0:
    reaktionen = ['Zusage', 'Absage', 'Telefonat', 'Vorstellungsgespräch']
    for reaktion in reaktionen:
        c.execute('''
        INSERT INTO Reaktion (reaktion)
        VALUES (?)
        ''', (reaktion,))
    conn.commit()

# GUI erstellen
root = tk.Tk()
root.title("Bewerbung Reaktion Hinzufügen")

# Frame für Bewerbung
frame_bewerbung = tk.LabelFrame(root, text="Neue Bewerbung", padx=10, pady=10)
frame_bewerbung.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Eingabefelder für Bewerbung
tk.Label(frame_bewerbung, text="Datum (YYYY-MM-DD):").grid(row=0, column=0, sticky="e")
entry_datum_bewerbung = tk.Entry(frame_bewerbung, width=15)
entry_datum_bewerbung.grid(row=0, column=1)

tk.Label(frame_bewerbung, text="Firma:").grid(row=1, column=0, sticky="e")
entry_firma = tk.Entry(frame_bewerbung, width=25)
entry_firma.grid(row=1, column=1)

tk.Label(frame_bewerbung, text="Ansprechpartner:").grid(row=2, column=0, sticky="e")
entry_ansprechpartner = tk.Entry(frame_bewerbung, width=25)
entry_ansprechpartner.grid(row=2, column=1)

tk.Label(frame_bewerbung, text="Kontakt (Telefon oder E-Mail):").grid(row=3, column=0, sticky="e")
entry_kontakt = tk.Entry(frame_bewerbung, width=25)
entry_kontakt.grid(row=3, column=1)

tk.Label(frame_bewerbung, text="Stellenbezeichnung:").grid(row=4, column=0, sticky="e")
entry_stellenbezeichnung = tk.Entry(frame_bewerbung, width=25)
entry_stellenbezeichnung.grid(row=4, column=1)

tk.Label(frame_bewerbung, text="Stellenanzeige (Pfad zur Datei):").grid(row=5, column=0, sticky="e")
entry_stellenanzeige = tk.Entry(frame_bewerbung, width=25)
entry_stellenanzeige.grid(row=5, column=1)

# Button zum Auswählen der Datei
button_select_file = tk.Button(frame_bewerbung, text="Datei auswählen", command=select_file)
button_select_file.grid(row=5, column=2)

# Button zum Hinzufügen der Bewerbung
button_add_bewerbung = tk.Button(frame_bewerbung, text="Bewerbung hinzufügen", command=insert_bewerbung)
button_add_bewerbung.grid(row=6, columnspan=2, pady=5)

# Frame für die Auswahl und Reaktion auf Bewerbungen
frame_reaktion = tk.LabelFrame(root, text="Reaktion auf Bewerbung", padx=10, pady=10)
frame_reaktion.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# Bewerbung Auswahl (nach Datum oder Firma sortiert)
bewerbung_label = tk.Label(frame_reaktion, text="Bewerbung auswählen:")
bewerbung_label.grid(row=0, column=0, padx=10, pady=5)

bewerbung_combobox = ttk.Combobox(frame_reaktion, width=30)
bewerbung_combobox.grid(row=0, column=1, padx=10, pady=5)

# Sortieroptionen für Bewerbungen
sortierung_label = tk.Label(frame_reaktion, text="Bewerbungen sortieren nach:")
sortierung_label.grid(row=1, column=0, padx=10, pady=5)

sortierung_combobox = ttk.Combobox(frame_reaktion, values=['Nach Datum', 'Nach Firma'], width=15)
sortierung_combobox.grid(row=1, column=1, padx=10, pady=5)
sortierung_combobox.set('Nach Datum')  # Standardwert auf "Nach Datum"


# Event-Handler für die Sortierungsauswahl
def on_sortierung_change(event):
    show_bewerbungen()


# Event zuweisen
sortierung_combobox.bind("<<ComboboxSelected>>", on_sortierung_change)

# Reaktion Auswahl
reaktion_label = tk.Label(frame_reaktion, text="Reaktion:")
reaktion_label.grid(row=2, column=0, padx=10, pady=5)

reaktion_combobox = ttk.Combobox(frame_reaktion, values=['Zusage', 'Absage', 'Telefonat', 'Vorstellungsgespräch'],
                                 width=15)
reaktion_combobox.grid(row=2, column=1, padx=10, pady=5)

# Datum für die Reaktion
datum_label = tk.Label(frame_reaktion, text="Datum der Reaktion (YYYY-MM-DD):")
datum_label.grid(row=3, column=0, padx=10, pady=5)

datum_entry = tk.Entry(frame_reaktion, width=15)
datum_entry.grid(row=3, column=1, padx=10, pady=5)

# Bemerkung Eingabe
bemerkung_label = tk.Label(frame_reaktion, text="Bemerkung:")
bemerkung_label.grid(row=4, column=0, padx=10, pady=5)

bemerkung_text = tk.Text(frame_reaktion, height=3, width=30)
bemerkung_text.grid(row=4, column=1, padx=10, pady=5)

# Button zum Hinzufügen der Reaktion
add_button = tk.Button(frame_reaktion, text="Reaktion hinzufügen", command=reaktion_hinzufuegen)
add_button.grid(row=5, column=0, columnspan=2, pady=5)

# Statuslabel zur Bestätigung
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=2, column=0, columnspan=2, pady=5)

# Bewerbungen anzeigen
show_bewerbungen()

# Fenster starten
root.mainloop()

# Verbindung schließen
conn.close()
