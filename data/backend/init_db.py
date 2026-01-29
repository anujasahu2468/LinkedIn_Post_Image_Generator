import sqlite3
import json
import os


def reset_and_init():
    db_path = "../../linkedin_gen.db"
    json_path = "../processed/processed_posts.json"

    # 1. Delete the old SQLite file if it exists to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed old database: {db_path}")

    # 2. Connect to SQLite (This creates the file automatically)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. Create the table structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            language TEXT,
            length_type TEXT,
            tags TEXT
        )
    ''')

    # 4. Load JSON and Insert into SQLite
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            posts = json.load(f)

        for post in posts:
            # We join the tags list into a string separated by commas
            tags_str = ",".join(post.get('tags', []))
            cursor.execute('''
                INSERT INTO posts (text, language, length_type, tags)
                VALUES (?, ?, ?, ?)
            ''', (post['text'], post['language'], post['length'], tags_str))

        conn.commit()
        print(f"✅ Success! Indexed {len(posts)} posts into {db_path}")
    else:
        print(f"❌ Error: {json_path} not found.")

    conn.close()


if __name__ == "__main__":
    reset_and_init()