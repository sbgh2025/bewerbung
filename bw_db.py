import sqlite3

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('Bewerbungsadressat.db')
c = conn.cursor()

# Tabelle 'Bewerbungen' erstellen
c.execute('''
CREATE TABLE IF NOT EXISTS Bewerbungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum DATE NOT NULL,
    firma TEXT NOT NULL,
    ansprechpartner TEXT,
    kontakt TEXT,
    stellenbezeichnung TEXT,
    stellenanzeige BLOB
)
''')

# Tabelle 'Reaktion' erstellen
c.execute('''
CREATE TABLE IF NOT EXISTS Reaktion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reaktion TEXT NOT NULL
)
''')

# Vorbefüllen der 'Reaktion' Tabelle mit den Standardwerten
reaktionen = ['Zusage', 'Absage', 'Telefonat', 'Vorstellungsgespräch']
for reaktion in reaktionen:
    c.execute('''
    INSERT OR IGNORE INTO Reaktion (reaktion)
    VALUES (?)
    ''', (reaktion,))

# Tabelle 'Reaktionen_Bewerbung' erstellen
c.execute('''
CREATE TABLE IF NOT EXISTS Reaktionen_Bewerbung (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum DATE NOT NULL,
    bewerbung_id INTEGER,
    reaktion_id INTEGER,
    bemerkung TEXT,
    FOREIGN KEY (reaktion_id) REFERENCES Reaktion(id),
    FOREIGN KEY (bewerbung_id) REFERENCES Bewerbungen(id)
)
''')

# Beispiel-Daten in die 'Bewerbungen' Tabelle einfügen
c.execute('''
INSERT INTO Bewerbungen (datum, firma, ansprechpartner, kontakt, stellenbezeichnung, stellenanzeige)
VALUES 
('2025-03-01', 'Firma A', 'Max Mustermann', 'max@firmaa.de', 'Softwareentwickler', NULL),
('2025-03-02', 'Firma B', 'Julia Müller', 'julia@firmaB.de', 'Marketing Manager', NULL);
''')

# Beispiel-Daten in die 'Reaktionen_Bewerbung' Tabelle einfügen
c.execute('''
INSERT INTO Reaktionen_Bewerbung (datum, bewerbung_id, reaktion_id, bemerkung)
VALUES 
('2025-03-03', 1, 1, 'Zusage für die Position'),
('2025-03-04', 2, 2, 'Absage aufgrund eines anderen Kandidaten');
''')

# Änderungen speichern
conn.commit()

# Verbindung schließen
conn.close()

print("Datenbank und Tabellen wurden erfolgreich erstellt, verknüpft und mit Beispieldaten befüllt.")
