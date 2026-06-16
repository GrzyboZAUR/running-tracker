import sqlite3
import requests

conn = sqlite3.connect('running.db')

# nowa tabela na ciśnienie z dnia poprzedniego
conn.execute("""
    CREATE TABLE IF NOT EXISTS weather_prev (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE UNIQUE,
        pressure_prev INTEGER
    )
""")
conn.commit()

# pobierz daty wszystkich biegów
runs = conn.execute("SELECT date FROM runs ORDER BY date").fetchall()

for (date,) in runs:
    # oblicz dzień poprzedni
    from datetime import datetime, timedelta
    prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')

    # sprawdź czy już mamy
    existing = conn.execute("SELECT 1 FROM weather_prev WHERE date = ?", (date,)).fetchone()
    if existing:
        print(f"{date} — już mamy")
        continue

    # pobierz z Open-Meteo
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 51.1,
        "longitude": 17.03,
        "start_date": prev_date,
        "end_date": prev_date,
        "hourly": "surface_pressure",
        "timezone": "Europe/Warsaw"
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        d = r.json()
        pressure = round(d["hourly"]["surface_pressure"][12])
        conn.execute("INSERT OR IGNORE INTO weather_prev (date, pressure_prev) VALUES (?, ?)", (date, pressure))
        conn.commit()
        print(f"{date} — ciśnienie poprzedniego dnia: {pressure} hPa")
    except Exception as e:
        print(f"{date} — błąd: {e}")

# pokaż różnice
print("\n=== ZMIANA CIŚNIENIA ===")
rows = conn.execute("""
    SELECT r.date, w.pressure, wp.pressure_prev,
           w.pressure - wp.pressure_prev as pressure_change,
           s.headache
    FROM runs r
    LEFT JOIN weather w ON w.date = r.date
    LEFT JOIN weather_prev wp ON wp.date = r.date
    LEFT JOIN wellbeing s ON s.run_id = r.id
    ORDER BY r.date
""").fetchall()

for row in rows:
    headache = '🤕' if row[4] == 1 else '✅'
    print(f"{row[0]} | ciśnienie: {row[1]} | poprzedni dzień: {row[2]} | zmiana: {row[3]} | {headache}")

conn.close()