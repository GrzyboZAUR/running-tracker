import sqlite3

conn = sqlite3.connect('running.db')
conn.execute("""
    UPDATE wellbeing SET energy_before = 4 where id = 3
""")
conn.commit()
print("Gotowe!")
conn.close()