import sqlite3
conn = sqlite3.connect('storage/db/app.db')
c = conn.cursor()
c.execute("DELETE FROM events WHERE camera_id='camera_03'")
conn.commit()
conn.close()
print("Deleted camera_03 events.")
