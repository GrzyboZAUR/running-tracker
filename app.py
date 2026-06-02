from flask import Flask, render_template, request, redirect
import sqlite3
import requests

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('running.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_weather(date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 52.23,
        "longitude": 21.01,
        "start_date": date,
        "end_date": date,
        "daily": "temperature_2m_max",
        "hourly": "relativehumidity_2m,surface_pressure",
        "timezone": "Europe/Warsaw"
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        d = r.json()
        temperature = d["daily"]["temperature_2m_max"][0]
        humidity = d["hourly"]["relativehumidity_2m"][12]
        pressure = round(d["hourly"]["surface_pressure"][12])
        return temperature, pressure, humidity
    except:
        return None, None, None

@app.route('/')
def index():
    db = get_db()
    runs = db.execute("""
        SELECT r.*, w.headache, w.energy_before, w.energy_after, w.notes,
               p.temperature, p.pressure, p.humidity
        FROM runs r
        LEFT JOIN wellbeing w ON w.run_id = r.id
        LEFT JOIN weather p ON p.date = r.date
        ORDER BY r.date DESC
    """).fetchall()
    return render_template('index.html', runs=runs)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        db = get_db()

        db.execute("""
            INSERT INTO runs (date, distance_km, duration_min, avg_pace, avg_speed,
                calories, avg_heart_rate, max_heart_rate, cadence,
                performance, vo2max, recovery_time_h)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form['date'],
            request.form['distance_km'],
            request.form['duration_min'],
            request.form['avg_pace'],
            request.form['avg_speed'],
            request.form['calories'],
            request.form['avg_heart_rate'],
            request.form['max_heart_rate'],
            request.form['cadence'],
            request.form['performance'],
            request.form['vo2max'],
            request.form['recovery_time_h'],
        ))
        run_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        db.execute("""
            INSERT INTO wellbeing (run_id, headache, energy_before, energy_after, notes)
            VALUES (?,?,?,?,?)
        """, (
            run_id,
            request.form['headache'],
            request.form['energy_before'],
            request.form['energy_after'],
            request.form.get('notes', '')
        ))

        date = request.form['date']
        temperature, pressure, humidity = fetch_weather(date)
        if temperature is not None:
            db.execute("""
                INSERT OR IGNORE INTO weather (date, temperature, pressure, humidity)
                VALUES (?,?,?,?)
            """, (date, temperature, pressure, humidity))

        db.commit()
        return redirect('/')

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)