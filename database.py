import sqlite3
import json

class Database:
    def __init__(self, db_name="bookclub.db"):
        try:
            # Initialize a connection to the SQLite database
            self.connection = sqlite3.connect(db_name)
            self.create_tables()  # Create necessary tables
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_tables(self):
        try:
            # Create tables for the schema if they don't already exist
            with self.connection:
                # Create 'Clubs' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS Clubs (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        defaultChannel INTEGER
                    );
                """)

                # Create 'Members' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS Members (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        points INTEGER DEFAULT 0,
                        numberOfBooksRead INTEGER DEFAULT 0
                    );
                """)

                # Create 'MemberClubs' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS MemberClubs (
                        memberId INTEGER,
                        clubId TEXT,
                        FOREIGN KEY(memberId) REFERENCES Members(id),
                        FOREIGN KEY(clubId) REFERENCES Clubs(id),
                        PRIMARY KEY (memberId, clubId)
                    );
                """)

                # Create 'Sessions' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS Sessions (
                        id TEXT PRIMARY KEY,
                        club_id TEXT NOT NULL,
                        book_id INTEGER,
                        dueDate TEXT,
                        FOREIGN KEY (club_id) REFERENCES Clubs(id)
                    );
                """)

                # Create 'Books' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS Books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        edition TEXT,
                        year INTEGER,
                        ISBN INTEGER
                    );
                """)

                # Create 'Discussions' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS Discussions (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        date TEXT NOT NULL,
                        location TEXT,
                        FOREIGN KEY (session_id) REFERENCES Sessions(id)
                    );
                """)

                # Create 'ShameList' table
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS ShameList (
                        session_id TEXT,
                        member_id INTEGER,
                        PRIMARY KEY (session_id, member_id),
                        FOREIGN KEY (session_id) REFERENCES Sessions(id),
                        FOREIGN KEY (member_id) REFERENCES Members(id)
                    );
                """)
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def save_club(self, data):
        with self.connection:
            # Insert club data
            self.connection.execute("INSERT OR IGNORE INTO Clubs (id, name, defaultChannel) VALUES (?, ?, ?)", (data['id'], data['name'], data['defaultChannel']))

            # Insert member data
            for member in data['members']:
                self.connection.execute("""
                    INSERT OR IGNORE INTO Members (id, name, points, numberOfBooksRead)
                    VALUES (?, ?, ?, ?)
                """, (member['id'], member['name'], member['points'], member['numberOfBooksRead']))

                # Link members to clubs in the MemberClubs table
                for club_id in member['clubs']:
                    self.connection.execute("INSERT OR IGNORE INTO MemberClubs (member_id, club_id) VALUES (?, ?)", (member['id'], club_id))

            # Insert book data and retrieve the auto-generated book ID
            book = data['activeSession']['book']
            book_id = self.connection.execute("""
                INSERT INTO Books (title, author, edition, year, ISBN)
                VALUES (?, ?, ?, ?, ?)
            """, (book['title'], book['author'], book['edition'], book['year'], book['ISBN'])).lastrowid

            # Insert session data
            session = data['activeSession']
            self.connection.execute("""
                INSERT OR IGNORE INTO Sessions (id, club_id, book_id, dueDate)
                VALUES (?, ?, ?, ?)
            """, (session['id'], session['club_id'], book_id, session['dueDate']))

            # Insert discussion data
            for discussion in session['discussions']:
                self.connection.execute("""
                    INSERT OR IGNORE INTO Discussions (id, session_id, title, date, location)
                    VALUES (?, ?, ?, ?, ?)
                """, (discussion['id'], session['id'], discussion['title'], discussion['date'], discussion['location']))

    def update_club(self, club_id, name, defaultChannel):
        """Update club details."""
        with self.connection:
            if name:
                self.connection.execute("UPDATE Clubs SET name = ? WHERE id = ?", (name, club_id))
            if defaultChannel:
                self.connection.execute("UPDATE Clubs SET defaultChannel = ? WHERE id = ?", (defaultChannel, club_id))

    def add_member(self, member_id, name, points, number_of_books_read, clubs):
        """Add a new member and associate them with clubs."""
        with self.connection:
            self.connection.execute("""
                INSERT OR IGNORE INTO Members (id, name, points, numberOfBooksRead)
                VALUES (?, ?, ?, ?)
            """, (member_id, name, points, number_of_books_read))
            for club_id in clubs:
                self.connection.execute("INSERT OR IGNORE INTO MemberClubs (member_id, club_id) VALUES (?, ?)", (member_id, club_id))

    def get_session_details(self, session_id):
        """Retrieve session details, including book and discussions."""
        with self.connection:
            session = self.connection.execute("SELECT * FROM Sessions WHERE id = ?", (session_id,)).fetchone()
            if not session:
                return None

            book = self.connection.execute("SELECT * FROM Books WHERE id = ?", (session[2],)).fetchone()
            discussions = self.connection.execute("SELECT * FROM Discussions WHERE session_id = ?", (session_id,)).fetchall()

            return {
                "id": session[0],
                "club_id": session[1],
                "book": {
                    "title": book[1],
                    "author": book[2],
                    "edition": book[3],
                    "year": book[4],
                    "ISBN": book[5]
                },
                "dueDate": session[3],
                "discussions": [
                    {
                        "id": discussion[0],
                        "title": discussion[2],
                        "date": discussion[3],
                        "location": discussion[4]
                    } for discussion in discussions
                ]
            }

    def add_to_shame_list(self, session_id, member_id):
        """Add a member to the shame list for a session."""
        with self.connection:
            self.connection.execute("INSERT OR IGNORE INTO ShameList (session_id, member_id) VALUES (?, ?)", (session_id, member_id))

    def update_session(self, session_id, club_id=None, book_id=None, dueDate=None):
        """Update session details."""
        with self.connection:
            if club_id:
                self.connection.execute("UPDATE Sessions SET club_id = ? WHERE id = ?", (club_id, session_id))
            if book_id:
                self.connection.execute("UPDATE Sessions SET book_id = ? WHERE id = ?", (book_id, session_id))
            if dueDate:
                self.connection.execute("UPDATE Sessions SET dueDate = ? WHERE id = ?", (dueDate, session_id))

    def update_discussion(self, discussion_id, session_id=None, title=None, date=None, location=None):
        """Update discussion details."""
        with self.connection:
            if session_id:
                self.connection.execute("UPDATE Discussions SET session_id = ? WHERE id = ?", (session_id, discussion_id))
            if title:
                self.connection.execute("UPDATE Discussions SET title = ? WHERE id = ?", (title, discussion_id))
            if date:
                self.connection.execute("UPDATE Discussions SET date = ? WHERE id = ?", (date, discussion_id))
            if location:
                self.connection.execute("UPDATE Discussions SET location = ? WHERE id = ?", (location, discussion_id))

    def update_member(self, member_id, name=None, points=None, numberOfBooksRead=None):
        """Update member details."""
        with self.connection:
            if name:
                self.connection.execute("UPDATE Members SET name = ? WHERE id = ?", (name, member_id))
            if points:
                self.connection.execute("UPDATE Members SET points = ? WHERE id = ?", (points, member_id))
            if numberOfBooksRead:
                self.connection.execute("UPDATE Members SET numberOfBooksRead = ? WHERE id = ?", (numberOfBooksRead, member_id))

    def get_club(self):
        with self.connection:
            # Fetch club details
            club = self.connection.execute("SELECT * FROM Clubs").fetchone()
            # Fetch all members
            members = self.connection.execute("SELECT * FROM Members").fetchall()
            # Fetch session details
            sessions = self.connection.execute("SELECT * FROM Sessions").fetchall()
            # Fetch books associated with sessions
            books = self.connection.execute("SELECT * FROM Books").fetchall()
            # Fetch discussions associated with sessions
            discussions = self.connection.execute("SELECT * FROM Discussions").fetchall()

        # Transform member data into the required format
        members_data = []
        for member in members:
            # Fetch all clubs the member belongs to
            clubs = self.connection.execute("SELECT club_id FROM MemberClubs WHERE member_id = ?", (member[0],)).fetchall()
            members_data.append({
                "id": member[0],
                "name": member[1],
                "points": member[2],
                "clubs": [club_id[0] for club_id in clubs],
                "numberOfBooksRead": member[3]
            })

        # Transform session data into the required format
        session_data = None
        if sessions:
            session = sessions[0]  # Assuming only one active session
            # Fetch book details for the session
            book = self.connection.execute("SELECT * FROM Books WHERE id = ?", (session[2],)).fetchone()
            # Fetch discussions for the session
            session_discussions = [
                {
                    "id": discussion[0],
                    "session_id": discussion[1],
                    "title": discussion[2],
                    "date": discussion[3],
                    "location": discussion[4]
                }
                for discussion in discussions if discussion[1] == session[0]
            ]

            session_data = {
                "id": session[0],
                "club_id": session[1],
                "book": {
                    "title": book[1],
                    "author": book[2],
                    "edition": book[3],
                    "year": book[4],
                    "ISBN": book[5]
                },
                "dueDate": session[3],
                "shameList": [],
                "discussions": session_discussions
            }

        # Return the full reconstructed club data
        return {
            "id": club[0],
            "name": club[1],
            "defaultChannel": club[2],
            "members": members_data,
            "activeSession": session_data,
            "pastSessions": []
        }

    def close_connection(self):
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    # JSON data provided by the user
    json_data = {
        "id": "0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3",
        "name": "Quill's Bookclub",
        "defaultChannel": 1327357851827572872,
        "members": [
            {
                "id": 0,
                "name": "@ivangarzab",
                "points": 0,
                "clubs": ["0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3"],
                "numberOfBooksRead": 0
            },
            {
                "id": 1,
                "name": "@chitho",
                "points": 0,
                "clubs": ["0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3"],
                "numberOfBooksRead": 0
            },
            {
                "id": 2,
                "name": "@ket092",
                "points": 0,
                "clubs": ["0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3"],
                "numberOfBooksRead": 0
            },
            {
                "id": 3,
                "name": "@.LNGR.",
                "points": 0,
                "clubs": ["0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3"],
                "numberOfBooksRead": 0
            },
            {
                "id": 4,
                "name": "@Zatiba",
                "points": 0,
                "clubs": ["0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3"],
                "numberOfBooksRead": 0
            }
        ],
        "activeSession": {
            "id": "cfae184f-8214-4e42-b763-52e25650d69a",
            "club_id": "0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3",
            "book": {
                "title": "Farenheit 451",
                "author": "Ray Bradbury",
                "edition": "",
                "year": 0,
                "ISBN": 0
            },
            "dueDate": "3/31/2025",
            "shameList": [],
            "discussions": [
                {
                    "id": "95a8f0dd-93eb-48f0-a1a3-8f513612b570",
                    "session_id": "cfae184f-8214-4e42-b763-52e25650d69a",
                    "title": "Frist discussion",
                    "date": "1/31/2025",
                    "location": "virtual"
                },
                {
                    "id": "1658184c-4a1d-4869-951f-e95869fd0cda",
                    "session_id": "cfae184f-8214-4e42-b763-52e25650d69a",
                    "title": "Second discussion",
                    "date": "2/28/2025",
                    "location": "virtual"
                },
                {
                    "id": "d6cfdd24-9242-4416-837b-f25d16814b61",
                    "session_id": "cfae184f-8214-4e42-b763-52e25650d69a",
                    "title": "Final discussion",
                    "date": "3/31/2025",
                    "location": "virtual"
                }
            ]
        },
        "pastSessions": []
    }

    db = Database()
    db.save_club(json_data)
    retrieved_data = db.get_club()
    print(json.dumps(retrieved_data, indent=4))
