from .base import BaseDatabase

class ClubDatabase(BaseDatabase):
    def create_club_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS Clubs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)

    def save_club(self, club_id, name):
        self.execute_query("INSERT OR IGNORE INTO Clubs (id, name) VALUES (?, ?)", (club_id, name))

    def update_club(self, club_id, name):
        self.execute_query("UPDATE Clubs SET name = ? WHERE id = ?", (name, club_id))
