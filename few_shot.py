import sqlite3


class FewShotPosts:
    def __init__(self, db_path="linkedin_gen.db"):
        self.db_path = db_path

    def get_tags(self):
        """Fetches all unique tags stored in the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Select all tags, then we split them in Python since they are stored as CSV
        cursor.execute("SELECT tags FROM posts")
        rows = cursor.fetchall()
        conn.close()

        unique_tags = set()
        for row in rows:
            if row[0]:  # Ensure the tag string isn't empty
                tags = row[0].split(",")
                unique_tags.update(tags)

        return sorted(list(unique_tags))

    def get_filtered_posts(self, length, language, tag):
        """Fetches posts that match specific criteria using SQL queries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()

        # Using the LIKE operator to find the tag within the comma-separated string
        query = """
            SELECT text, language, length_type, tags 
            FROM posts 
            WHERE length_type = ? 
            AND language = ? 
            AND tags LIKE ?
        """

        # %tag% ensures we find the tag anywhere in the string
        cursor.execute(query, (length, language, f"%{tag}%"))
        rows = cursor.fetchall()
        conn.close()

        # Convert sqlite3.Row objects to standard dictionaries
        return [dict(row) for row in rows]


if __name__ == "__main__":
    fs = FewShotPosts()
    # Test: Get all tags
    print(f"Available Tags: {fs.get_tags()}")
    # Test: Get specific posts
    posts = fs.get_filtered_posts("Short", "English", "AI")
    print(f"Found {len(posts)} matching posts.")