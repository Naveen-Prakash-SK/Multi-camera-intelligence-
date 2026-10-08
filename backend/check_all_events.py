import sqlite3
import collections

conn = sqlite3.connect('storage/db/app.db')
cursor = conn.cursor()
cursor.execute("SELECT camera_id, description FROM events")
rows = cursor.fetchall()
counts = collections.Counter([(r[0], r[1]) for r in rows])
print(counts)
conn.close()
