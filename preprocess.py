import json
import sqlite3
import time
from pydantic import BaseModel, Field
from llm_helper import llm


# Pydantic schema — used with .with_structured_output() to guarantee
# the LLM returns valid, typed JSON instead of free-form text.
class PostMetadata(BaseModel):
    line_count: str = Field(description="Length of post: Short, Medium, or Long")
    language: str = Field(description="The language the post is written in")
    tags: list[str] = Field(description="Max 2 relevant professional tags")


def process_posts(raw_file_path, db_path="linkedin_gen.db"):
    """
    Reads raw posts from a JSON file, extracts metadata via the LLM,
    and stores everything in SQLite for use as few-shot examples.

    Run this once whenever you add new raw posts. The table is rebuilt
    from scratch each time so you never have stale data.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS posts")
    cursor.execute("""
        CREATE TABLE posts (
            id          INTEGER PRIMARY KEY,
            text        TEXT,
            language    TEXT,
            length_type TEXT,
            tags        TEXT
        )
    """)

    structured_llm = llm.with_structured_output(PostMetadata)

    with open(raw_file_path, encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Processing {len(posts)} posts...")

    for i, post in enumerate(posts):
        try:
            metadata = structured_llm.invoke(
                f"Extract metadata from this LinkedIn post:\n\n{post['text']}"
            )

            tags_str = ",".join(metadata.tags)
            cursor.execute(
                "INSERT INTO posts (text, language, length_type, tags) VALUES (?, ?, ?, ?)",
                (post["text"], metadata.language, metadata.line_count, tags_str),
            )
            conn.commit()  # Commit after each post so partial progress is saved

            print(f"[{i + 1}/{len(posts)}] OK — {post['text'][:40]}...")

            # Stay within free-tier rate limits (~15 RPM = 1 request per 4s)
            time.sleep(4.5)

        except Exception as e:
            print(f"Error on post {i + 1}: {e}")
            time.sleep(10)  # Longer pause to let the quota bucket reset

    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    process_posts("data/raw/raw_posts.json")