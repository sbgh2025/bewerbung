import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Funktion, um Bewerbungen mit Reaktionen anzuzeigen
def bewerbung_anzeigen(sort_by="datum"):
    # SQL Query zum Abrufen der Bewerbungen mit Reaktionen sortiert nach dem gewählten Kriterium
    if sort_by == "firma":
        order_by = "b.firma"
    else:
        order_by = "b.datum"

    c.execute(f'''
    SELECT b.datum AS bewerbung_datum, b.firma, b.ansprechpartner, b.stellenbezeichnung,
           r.reaktion, rb.datum AS reaktion_datum, rb.bemerkung
    FROM Bewerbungen b
    JOIN Reaktionen_Bewerbung rb ON b.id = rb.bewerbung_id
    JOIN Reaktion r ON rb.reaktion_id = r.id
    ORDER BY {order_by} DESC
    ''')

    bewerbungen_reaktionen = c.fetchall()

    # Leere die Treeview
    for row in treeview.get_children():
        treeview.delete(row)

    # Bewerbungen und Reaktionen in Treeview einfügen
    for bewerbung in bewerbungen_reaktionen:
        treeview.insert("", "end", values=bewerbung)


# Funktion, um eine Bewerbung mit Reaktionen zu löschen
def bewerbung_loeschen():
    # Hole die ausgewählte Bewerbung
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Keine Bewerbung ausgewählt!")
        return

    bewerbung_daten = treeview.item(selected_item)["values"]
    bewerbung_id = bewerbung_daten[0]  # Die ID der Bewerbung (erste Spalte)

    try:
        # Lösche zuerst die Reaktionen zur Bewerbung
        c.execute('DELETE FROM Reaktionen_Bewerbung WHERE bewerbung_id = ?', (bewerbung_id,))
        # Lösche dann die Bewerbung
        c.execute('DELETE FROM Bewerbungen WHERE id = ?', (bewerbung_id,))
        conn.commit()
        messagebox.showinfo("Erfolg", "Bewerbung und Reaktionen wurden erfolgreich gelöscht.")
        bewerbung_anzeigen()  # Aktualisiere die Anzeige
    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Löschen: {e}")


# Funktion zum Exportieren der Bewerbungen mit Reaktionen in eine PDF-Datei
def export_pdf():
    c.execute('''
    SELECT b.datum AS bewerbung_datum, b.firma, b.ansprechpartner, b.stellenbezeichnung,
           r.reaktion, rb.datum AS reaktion_datum, rb.bemerkung
    FROM Bewerbungen b
    JOIN Reaktionen_Bewerbung rb ON b.id = rb.bewerbung_id
    JOIN Reaktion r ON rb.reaktion_id = r.id
    ORDER BY b.datum DESC
    ''')

    bewerbungen_reaktionen = c.fetchall()

    if not bewerbungen_reaktionen:
        messagebox.showwarning("Keine Daten", "Es gibt keine Bewerbungen, die exportiert werden können.")
        return

    # Erstelle das PDF
    pdf_filename = "Bewerbungen_mit_Reaktionen.pdf"
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)

    pdf.setFont("Helvetica", 10)

    # Header
    pdf.drawString(100, 750, "Bewerbungen mit Reaktionen")
    pdf.drawString(100, 735, "===============================================")

    y_position = 710

    # Daten in das PDF einfügen
    for bewerbung in bewerbungen_reaktionen:
        pdf.drawString(100, y_position, f"Bewerbung Datum: {bewerbung[0]} - Firma: {bewerbung[1]}")
        pdf.drawString(100, y_position - 15, f"Ansprechpartner: {bewerbung[2]} - Stellenbezeichnung: {bewerbung[3]}")
        pdf.drawString(100, y_position - 30, f"Reaktion: {bewerbung[4]} - Reaktion Datum: {bewerbung[5]}")
        pdf.drawString(100, y_position - 45, f"Bemerkung: {bewerbung[6]}")
        y_position -= 60

        # Seitenumbruch wenn zu viele Einträge
        if y_position < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 750

    # Speichern des PDFs
    pdf.save()
    messagebox.showinfo("Erfolg", f"PDF wurde erfolgreich exportiert: {pdf_filename}")


# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('Bewerbungsadressat.db')
c = conn.cursor()

# GUI erstellen
root = Tk()
root.title("Bewerbungen mit Reaktionen")

# Auswahl, nach welchem Kriterium die Bewerbungen angezeigt werden (Firma oder Datum)
sort_label = Label(root, text="Sortieren nach:")
sort_label.pack(padx=10, pady=10)

sort_combobox = ttk.Combobox(root, values=["Datum", "Firma"])
sort_combobox.set("Datum")  # Setzt "Datum" als Standardwert
sort_combobox.pack(padx=10, pady=10)

# Button zum Anzeigen der Bewerbungen mit Reaktionen
anzeigen_button = Button(root, text="Bewerbungen mit Reaktionen anzeigen", command=lambda: bewerbung_anzeigen(sort_by=sort_combobox.get().lower()))
anzeigen_button.pack(padx=10, pady=10)

# Treeview zur Anzeige der Bewerbungen und Reaktionen
treeview = ttk.Treeview(root, columns=(
    "Bewerbung Datum", "Firma", "Ansprechpartner", "Stellenbezeichnung", "Reaktion", "Reaktion Datum", "Bemerkung"),
                        show="headings")

# Spaltenüberschriften festlegen
treeview.heading("Bewerbung Datum", text="Bewerbung Datum")
treeview.heading("Firma", text="Firma")
treeview.heading("Ansprechpartner", text="Ansprechpartner")
treeview.heading("Stellenbezeichnung", text="Stellenbezeichnung")
treeview.heading("Reaktion", text="Reaktion")
treeview.heading("Reaktion Datum", text="Reaktion Datum")
treeview.heading("Bemerkung", text="Bemerkung")

# Spaltenbreite festlegen
treeview.column("Bewerbung Datum", width=100)
treeview.column("Firma", width=150)
treeview.column("Ansprechpartner", width=150)
treeview.column("Stellenbezeichnung", width=150)
treeview.column("Reaktion", width=100)
treeview.column("Reaktion Datum", width=100)
treeview.column("Bemerkung", width=250)

# Treeview einfügen
treeview.pack(padx=10, pady=10)

# Buttons zum Löschen und Exportieren
loeschen_button = Button(root, text="Bewerbung und Reaktion löschen", command=bewerbung_loeschen)
loeschen_button.pack(padx=10, pady=10)

export_button = Button(root, text="Daten als PDF exportieren", command=export_pdf)
export_button.pack(padx=10, pady=10)

# Fenster starten
root.mainloop()

# Verbindung schließen
conn.close()
