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
print("Database created successfully!")
conn.close()