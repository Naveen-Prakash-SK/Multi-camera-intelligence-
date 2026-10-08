import time
import requests
import sqlite3

def wait_for_server():
    print("Waiting for server to start...")
    while True:
        try:
            r = requests.get("http://localhost:8000/api/cameras")
            if r.status_code == 200:
                print("Server is up!")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)

def process_all():
    print("Triggering process-all...")
    r = requests.post("http://localhost:8000/api/process-all")
    print("Process-all response:", r.json())
    time.sleep(5) # Give it time to finish

def verify_db():
    conn = sqlite3.connect('storage/db/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT camera_id, description FROM events")
    rows = cursor.fetchall()
    import collections
    counts = collections.Counter([(r[0], r[1]) for r in rows])
    for k, v in counts.items():
        print(f"{k}: {v} events")
    conn.close()

if __name__ == "__main__":
    wait_for_server()
    # Delete all old events first
    conn = sqlite3.connect('storage/db/app.db')
    c = conn.cursor()
    c.execute("DELETE FROM events")
    conn.commit()
    conn.close()
    print("Deleted all stale events.")
    
    process_all()
    verify_db()
