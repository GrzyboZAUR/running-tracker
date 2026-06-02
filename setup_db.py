import sqlite3

conn = sqlite3.connect('running.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    distance_km REAL,
    duration_min INTEGER,
    avg_pace TEXT,
    avg_speed REAL,
    calories INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    cadence INTEGER,
    performance REAL,
    vo2max REAL,
    recovery_time_h INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    temperature REAL,
    pressure INTEGER,
    humidity INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS wellbeing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES runs(id),
    headache INTEGER,
    energy_before INTEGER,
    energy_after INTEGER,
    notes TEXT
)
""")

conn.commit()
print("Database created!")

# testowy wpis
cursor.execute("""
INSERT INTO runs (date, distance_km, duration_min, avg_pace, avg_speed,
                  calories, avg_heart_rate, max_heart_rate, cadence,
                  performance, vo2max, recovery_time_h)
VALUES ('2025-05-01', 5.2, 38, '7:18', 8.2, 420, 158, 178, 172, 74, 42, 22)
""")

cursor.execute("""
INSERT INTO wellbeing (run_id, headache, energy_before, energy_after, notes)
VALUES (1, 0, 3, 4, 'First test entry, felt good')
""")

conn.commit()

print("\n=== RUNS ===")
for row in cursor.execute("SELECT * FROM runs"):
    print(row)

print("\n=== WELLBEING ===")
for row in cursor.execute("SELECT * FROM wellbeing"):
    print(row)

conn.close()