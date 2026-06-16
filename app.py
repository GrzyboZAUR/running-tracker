from flask import Flask, render_template, request, redirect
import sqlite3
import requests
from dotenv import load_dotenv
import os
from functools import wraps
from flask import session
from rich.traceback import install
install(show_locals=False)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-fallback-key')
DATABASE = os.getenv('DATABASE', 'running.db')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/add')
        error = 'Wrong password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def get_db():
    conn = sqlite3.connect(DATABASE)
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
@login_required
def add():
    if request.method == 'POST':
        db = get_db()

        db.execute("""
            INSERT INTO runs (date, distance_km, duration_min, avg_pace, avg_speed,
                calories, avg_heart_rate, max_heart_rate, cadence,
                training_effect, vo2max, recovery_time_h)
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
            request.form['training_effect'],
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


@app.route('/stats')
def stats():
    db = get_db()

    summary = db.execute("""
        SELECT 
            COUNT(*) as total_runs,
            ROUND(SUM(distance_km), 1) as total_distance,
            ROUND(AVG(distance_km), 1) as avg_distance,
            ROUND(AVG(avg_heart_rate), 0) as avg_hr,
            ROUND(AVG(vo2max), 1) as avg_vo2max,
            ROUND(AVG(calories), 0) as avg_calories
        FROM runs
    """).fetchone()

    runs_over_time = db.execute("""
        SELECT date, distance_km, avg_heart_rate, avg_speed, vo2max,
               recovery_time_h, calories
        FROM runs
        ORDER BY date ASC
    """).fetchall()

    weather_vs_hr = db.execute("""
        SELECT r.date, r.avg_heart_rate, w.temperature, w.humidity,
               s.headache
        FROM runs r
        LEFT JOIN weather w ON w.date = r.date
        LEFT JOIN wellbeing s ON s.run_id = r.id
        ORDER BY r.date ASC
    """).fetchall()

    headache_stats = db.execute("""
        SELECT 
            s.headache,
            COUNT(*) as count,
            ROUND(AVG(w.temperature), 1) as avg_temp,
            ROUND(AVG(w.humidity), 1) as avg_humidity,
            ROUND(AVG(r.max_heart_rate), 0) as avg_hr,
            ROUND(AVG(r.training_effect), 1) as training_effect
        FROM wellbeing s
        JOIN runs r ON r.id = s.run_id
        LEFT JOIN weather w ON w.date = r.date
        GROUP BY s.headache
    """).fetchall()

    wellbeing_over_time = db.execute("""
        SELECT r.date, s.energy_before, s.energy_after, s.headache, s.notes
        FROM runs r
        JOIN wellbeing s ON s.run_id = r.id
        ORDER BY r.date ASC
    """).fetchall()

    return render_template('stats.html',
                           summary=summary,
                           runs_over_time=[dict(r) for r in runs_over_time],
                           weather_vs_hr=[dict(r) for r in weather_vs_hr],
                           headache_stats=[dict(r) for r in headache_stats],
                           wellbeing_over_time=[dict(r) for r in wellbeing_over_time]
                           )

if __name__ == '__main__':
    app.run(debug=True)