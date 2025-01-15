import sqlite3

class BookClubDatabase:
    def __init__(self, db_name="bookclub.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Create Clubs table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS clubs (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """)
            # Create Members table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    number_of_books_read INTEGER DEFAULT 0
                );
            """)
            # Create ClubMembers table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS club_members (
                    club_id INTEGER,
                    member_id INTEGER,
                    FOREIGN KEY (club_id) REFERENCES clubs(id),
                    FOREIGN KEY (member_id) REFERENCES members(id),
                    PRIMARY KEY (club_id, member_id)
                );
            """)
            # Create Sessions table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    club_id INTEGER,
                    number INTEGER,
                    book_title TEXT,
                    book_author TEXT,
                    due_date TEXT,
                    default_channel INTEGER,
                    FOREIGN KEY (club_id) REFERENCES clubs(id)
                );
            """)
            # Create Discussions table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS discussions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    title TEXT,
                    date TEXT,
                    location TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
            """)

    def save_club(self, club):
        with self.conn:
            self.conn.execute("INSERT INTO clubs (id, name) VALUES (?, ?)", (club["id"], club["name"]))
            for member in club["members"]:
                self.conn.execute("""
                    INSERT OR IGNORE INTO members (id, name, points, number_of_books_read)
                    VALUES (?, ?, ?, ?)
                """, (member["id"], member["name"], member["points"], member["numberOfBooksRead"]))
                self.conn.execute("""
                    INSERT INTO club_members (club_id, member_id) VALUES (?, ?)
                """, (club["id"], member["id"]))
            if "activeSession" in club:
                self.save_session(club["id"], club["activeSession"])

    def save_session(self, club_id, session):
        with self.conn:
            self.conn.execute("""
                INSERT INTO sessions (id, club_id, number, book_title, book_author, due_date, default_channel)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session["id"], club_id, session["number"],
                session["book"]["title"], session["book"]["author"],
                session["dueDate"], session["defaultChannel"]
            ))
            for discussion in session["discussions"]:
                self.conn.execute("""
                    INSERT INTO discussions (id, session_id, title, date, location)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    discussion["id"], session["id"], discussion["title"],
                    discussion["date"], discussion["location"]
                ))

    def get_club(self, club_id):
        """Retrieve a club with its members and sessions."""
        with self.conn:
            club = self.conn.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)).fetchone()
            members = self.conn.execute("""
                SELECT members.* FROM members
                JOIN club_members ON members.id = club_members.member_id
                WHERE club_members.club_id = ?
            """, (club_id,)).fetchall()
            sessions = self.conn.execute("SELECT * FROM sessions WHERE club_id = ?", (club_id,)).fetchall()
            return {"club": club, "members": members, "sessions": sessions}

    def update_member_points(self, member_id, points):
        """Update a member's points."""
        with self.conn:
            self.conn.execute("UPDATE members SET points = ? WHERE id = ?", (points, member_id))

    def delete_club(self, club_id):
        """Delete a club and all associated data."""
        with self.conn:
            self.conn.execute("DELETE FROM club_members WHERE club_id = ?", (club_id,))
            self.conn.execute("DELETE FROM sessions WHERE club_id = ?", (club_id,))
            self.conn.execute("DELETE FROM clubs WHERE id = ?", (club_id,))

# Example usage
if __name__ == "__main__":
    db = BookClubDatabase()

    # Example JSON data
    default_data = {
        "id": 0,
        "name": "Quill's Bookclub",
        "members": [
            {"id": 0, "name": "@ivangarzab", "points": 0, "clubs": [0], "numberOfBooksRead": 0},
            {"id": 1, "name": "@chitho", "points": 0, "clubs": [0], "numberOfBooksRead": 0},
            {"id": 2, "name": "@ket092", "points": 0, "clubs": [0], "numberOfBooksRead": 0},
            {"id": 3, "name": "@.lngr.", "points": 0, "clubs": [0], "numberOfBooksRead": 0},
            {"id": 4, "name": "@zatiba", "points": 0, "clubs": [0], "numberOfBooksRead": 0},
        ],
        "activeSession": {
            "number": 0,
            "id": "1:0",
            "book": {
                "title": "Farenheit 451",
                "author": "Ray Bradbury",
                "edition": "",
                "year": 0,
                "ISBN": 0
            },
            "dueDate": "3/31/2025",
            "defaultChannel": 1327357851827572872,
            "discussions": [
                {"number": 0, "id": "1:0-0", "title": "First discussion", "date": "1/31/2025", "location": "virtual"}
            ]
        }
    }

    # Save the JSON data to the database
    db.save_club(default_data)

    # Update a member's points
    db.update_member_points(0, 10)

    # Retrieve and print the club data
    data = db.get_club(1)
    print(data)
