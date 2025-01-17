from .base import BaseDatabase

class MemberDatabase(BaseDatabase):
    def create_member_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS Members (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                numberOfBooksRead INTEGER DEFAULT 0
            );
        """)

    def add_member(self, member_id, name, points, number_of_books_read):
        self.execute_query("""
            INSERT OR IGNORE INTO Members (id, name, points, numberOfBooksRead)
            VALUES (?, ?, ?, ?)
        """, (member_id, name, points, number_of_books_read))

    def update_member(self, member_id, name=None, points=None, numberOfBooksRead=None):
        if name:
            self.execute_query("UPDATE Members SET name = ? WHERE id = ?", (name, member_id))
        if points:
            self.execute_query("UPDATE Members SET points = ? WHERE id = ?", (points, member_id))
        if numberOfBooksRead:
            self.execute_query("UPDATE Members SET numberOfBooksRead = ? WHERE id = ?", (numberOfBooksRead, member_id))
