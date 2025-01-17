from .base import BaseDatabase

class SessionDatabase(BaseDatabase):
    def create_session_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS Sessions (
                id TEXT PRIMARY KEY,
                club_id TEXT NOT NULL,
                book_id INTEGER,
                dueDate TEXT,
                defaultChannel INTEGER
            );
        """)

    def update_session(self, session_id, club_id=None, book_id=None, dueDate=None, defaultChannel=None):
        if club_id:
            self.execute_query("UPDATE Sessions SET club_id = ? WHERE id = ?", (club_id, session_id))
        if book_id:
            self.execute_query("UPDATE Sessions SET book_id = ? WHERE id = ?", (book_id, session_id))
        if dueDate:
            self.execute_query("UPDATE Sessions SET dueDate = ? WHERE id = ?", (dueDate, session_id))
        if defaultChannel:
            self.execute_query("UPDATE Sessions SET defaultChannel = ? WHERE id = ?", (defaultChannel, session_id))
