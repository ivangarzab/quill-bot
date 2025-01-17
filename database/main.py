from database.club import ClubDatabase
from database.member import MemberDatabase
from database.session import SessionDatabase
from database.discussion import DiscussionDatabase

def main():
    club_db = ClubDatabase()
    member_db = MemberDatabase()
    session_db = SessionDatabase()
    discussion_db = DiscussionDatabase()

    # Example usage
    club_db.create_club_table()
    member_db.create_member_table()
    session_db.create_session_table()
    discussion_db.create_discussion_table()

    club_db.save_club("0f01ad5e-0665-4f02-8cdd-8d55ecb26ac3", "Quill's Bookclub")
    member_db.add_member(1, "@chitho", 10, 5)

if __name__ == "__main__":
    main()
