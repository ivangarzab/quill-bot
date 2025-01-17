from .base import BaseDatabase

class DiscussionDatabase(BaseDatabase):
    def create_discussion_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS Discussions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT
            );
        """)

    def update_discussion(self, discussion_id, session_id=None, title=None, date=None, location=None):
        if session_id:
            self.execute_query("UPDATE Discussions SET session_id = ? WHERE id = ?", (session_id, discussion_id))
        if title:
            self.execute_query("UPDATE Discussions SET title = ? WHERE id = ?", (title, discussion_id))
        if date:
            self.execute_query("UPDATE Discussions SET date = ? WHERE id = ?", (date, discussion_id))
        if location:
            self.execute_query("UPDATE Discussions SET location = ? WHERE id = ?", (location, discussion_id))
