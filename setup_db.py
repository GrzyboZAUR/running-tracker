import sqlite3

conn = sqlite3.connect('running.db')
cursor = conn.cursor()

# Tabela treningów
cursor.execute("""
CREATE TABLE IF NOT EXISTS treningi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    dystans_km REAL,
    czas_min INTEGER,
    srednie_tempo TEXT,
    srednia_predkosc REAL,
    kalorie INTEGER,
    srednie_tetno INTEGER,
    max_tetno INTEGER,
    kadencja INTEGER,
    wydajnosc REAL,
    vo2max REAL,
    czas_regeneracji_h INTEGER
)
""")

# Tabela pogody
cursor.execute("""
CREATE TABLE IF NOT EXISTS pogoda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE UNIQUE,
    temperatura REAL,
    cisnienie INTEGER,
    wilgotnosc INTEGER
)
""")

# Tabela samopoczucia
cursor.execute("""
CREATE TABLE IF NOT EXISTS samopoczucie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trening_id INTEGER REFERENCES treningi(id),
    bol_glowy INTEGER,
    energia_przed INTEGER,
    energia_po INTEGER,
    notatka TEXT
)
""")

print("Baza danych utworzona!")

# --- testowy wpis ---
cursor.execute("""
INSERT INTO treningi (data, dystans_km, czas_min, srednie_tempo, srednia_predkosc, 
                      kalorie, srednie_tetno, max_tetno, kadencja, wydajnosc, vo2max, czas_regeneracji_h)
VALUES ('2025-05-01', 5.2, 38, '7:18', 8.2, 420, 158, 178, 172, 74, 42, 22)
""")

cursor.execute("""
INSERT INTO samopoczucie (trening_id, bol_glowy, energia_przed, energia_po, notatka)
VALUES (1, 0, 3, 4, 'Pierwszy test bazy, czułem się nieźle')
""")

conn.commit()

# --- sprawdzenie ---
print("\n=== TRENINGI ===")
for row in cursor.execute("SELECT * FROM treningi"):
    print(row)

print("\n=== SAMOPOCZUCIE ===")
for row in cursor.execute("SELECT * FROM samopoczucie"):
    print(row)

conn.close()