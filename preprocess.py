import json
import sqlite3
import time
from pydantic import BaseModel, Field
from llm_helper import llm


# 1. Define a Pydantic Schema for 100% JSON Reliability
class PostMetadata(BaseModel):
    line_count: str = Field(description="Length of post: Short, Medium, or Long")
    language: str = Field(description="The language the post is written in")
    tags: list[str] = Field(description="Max 2 relevant professional tags")


def process_posts(raw_file_path, db_path="linkedin_gen.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Ensure table matches our new schema
    cursor.execute("DROP TABLE IF EXISTS posts")
    cursor.execute('''CREATE TABLE posts 
                      (id INTEGER PRIMARY KEY, text TEXT, language TEXT, length_type TEXT, tags TEXT)''')

    # Prepare the structured LLM
    # In 2026, we use .with_structured_output() instead of a manual Parser
    structured_llm = llm.with_structured_output(PostMetadata)

    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)

        st_progress = f"Processing {len(posts)} posts..."
        print(st_progress)

        for i, post in enumerate(posts):
            try:
                # 2. Optimized Extraction
                metadata = structured_llm.invoke(f"Extract metadata from this post: {post['text']}")

                tags_str = ",".join(metadata.tags)
                cursor.execute("INSERT INTO posts (text, language, length_type, tags) VALUES (?, ?, ?, ?)",
                               (post['text'], metadata.language, metadata.line_count, tags_str))

                # 3. 2026 Quota Management
                # Free tier is approx 15 RPM. 4 seconds is safer than 3.
                print(f"[{i + 1}/{len(posts)}] Processed: {post['text'][:30]}...")
                time.sleep(4.5)

            except Exception as e:
                print(f"❌ Error on post {i}: {e}")
                time.sleep(10)  # Longer wait on error to reset quota bucket

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    process_posts("data/raw/raw_posts.json")