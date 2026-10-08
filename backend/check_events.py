import sqlite3
import collections

conn = sqlite3.connect('storage/db/app.db')
cursor = conn.cursor()
cursor.execute("SELECT description FROM events WHERE camera_id='camera_03'")
rows = cursor.fetchall()
counts = collections.Counter([r[0] for r in rows])
print(counts)
conn.close()
