import sqlite3
import json

def init_db(processed_json_path):
    conn = sqlite3.connect("../../linkedin_gen.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts 
                      (id INTEGER PRIMARY KEY, text TEXT, tags TEXT, engagement INTEGER)''')

    # Load your processed posts into SQLite
    with open(processed_json_path, 'r') as f:
        posts = json.load(f)
        for p in posts:
            cursor.execute("INSERT INTO posts (text, tags, engagement) VALUES (?, ?, ?)",
                           (p['text'], ",".join(p['tags']), p.get('engagement', 0)))
    conn.commit()
    conn.close()