# General API for centralized access to all database functionality
# Import all individual components
from .club import ClubDatabase
from .member import MemberDatabase
from .session import SessionDatabase
from .discussion import DiscussionDatabase

class BookClubDatabase:
    def __init__(self, db_name="bookclub.db"):
        # Initialize individual components with the same database
        self.club_db = ClubDatabase(db_name)
        self.member_db = MemberDatabase(db_name)
        self.session_db = SessionDatabase(db_name)
        self.discussion_db = DiscussionDatabase(db_name)

    # Club Operations
    def create_club(self, club_id, name):
        self.club_db.create_club_table()
        self.club_db.save_club(club_id, name)

    def update_club(self, club_id, name):
        self.club_db.update_club(club_id, name)

    def get_club(self, club_id):
        """Retrieve a club's details by its ID."""
        return self.club_db.fetch_one("SELECT * FROM Clubs WHERE id = ?", (club_id,))

    # Member Operations
    def create_member(self, member_id, name, points=0, number_of_books_read=0):
        self.member_db.create_member_table()
        self.member_db.add_member(member_id, name, points, number_of_books_read)

    def update_member(self, member_id, name=None, points=None, number_of_books_read=None):
        self.member_db.update_member(member_id, name, points, number_of_books_read)

    # Session Operations
    def create_session_table(self):
        self.session_db.create_session_table()

    def update_session(self, session_id, club_id=None, book_id=None, dueDate=None, defaultChannel=None):
        self.session_db.update_session(session_id, club_id, book_id, dueDate, defaultChannel)

    def get_session(self, session_id):
        """Retrieve a session's details by its ID."""
        return self.session_db.fetch_one("SELECT * FROM Sessions WHERE id = ?", (session_id,))

    # Discussion Operations
    def create_discussion_table(self):
        self.discussion_db.create_discussion_table()

    def update_discussion(self, discussion_id, session_id=None, title=None, date=None, location=None):
        self.discussion_db.update_discussion(discussion_id, session_id, title, date, location)

# Example usage
if __name__ == "__main__":
    api = BookClubDatabase()

    # Create tables
    api.create_club("0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3", "Quill's Bookclub")
    api.create_member(1, "@chitho", points=10, number_of_books_read=5)

    print("API setup complete. Use `api` to manage your database.")
