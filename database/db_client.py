# database/db_client.py
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        # Initialize connection to Supabase
        self.ENV = os.getenv("ENV")
        if self.ENV == "dev":
            supabase_url = os.getenv("DEV_SUPABASE_URL")
            supabase_key = os.getenv("DEV_SUPABASE_KEY")
        else:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
            
        self.supabase = create_client(supabase_url, supabase_key)
    
    def save_club(self, data):
        # Insert club data
        self.supabase.table("clubs").insert({
            "id": data['id'],
            "name": data['name']
        }).execute()
        
        # Insert member data
        for member in data['members']:
            self.supabase.table("members").insert({
                "id": member['id'],
                "name": member['name'],
                "points": member['points'],
                "numberOfBooksRead": member['numberOfBooksRead']
            }).execute()
            
            # Link members to clubs
            for club_id in member['clubs']:
                self.supabase.table("memberclubs").insert({
                    "member_id": member['id'],
                    "club_id": club_id
                }).execute()
        
        # Insert book data
        book = data['activeSession']['book']
        book_response = self.supabase.table("books").insert({
            "title": book['title'],
            "author": book['author'],
            "edition": book['edition'],
            "year": book['year'],
            "ISBN": book['ISBN']
        }).execute()
        
        # Get the book ID from the response
        book_id = book_response.data[0]['id']
        
        # Insert session data
        session = data['activeSession']
        self.supabase.table("sessions").insert({
            "id": session['id'],
            "club_id": session['club_id'],
            "book_id": book_id,
            "dueDate": session['dueDate'],
            "defaultChannel": session['defaultChannel']
        }).execute()
        
        # Insert discussion data
        for discussion in session['discussions']:
            self.supabase.table("discussions").insert({
                "id": discussion['id'],
                "session_id": session['id'],
                "title": discussion['title'],
                "date": discussion['date'],
                "location": discussion['location']
            }).execute()
    
    def update_club(self, club_id, name):
        """Update the name of a club."""
        self.supabase.table("clubs").update({"name": name}).eq("id", club_id).execute()

    def add_member(self, member_id, name, points, number_of_books_read, clubs):
        """Add a new member and associate them with clubs."""
        self.supabase.table("members").insert({
            "id": member_id,
            "name": name,
            "points": points,
            "numberOfBooksRead": number_of_books_read
        }).execute()
        
        for club_id in clubs:
            self.supabase.table("memberclubs").insert({
                "member_id": member_id,
                "club_id": club_id
            }).execute()

    def get_session_details(self, session_id):
        """Retrieve session details, including book and discussions."""
        # Get session details
        session_response = self.supabase.table("sessions").select("*").eq("id", session_id).execute()
        
        if not session_response.data:
            return None
            
        session = session_response.data[0]
        
        # Get book details
        book_response = self.supabase.table("books").select("*").eq("id", session["book_id"]).execute()
        book = book_response.data[0] if book_response.data else None
        
        # Get discussions
        discussions_response = self.supabase.table("discussions").select("*").eq("session_id", session_id).execute()
        
        return {
            "id": session["id"],
            "club_id": session["club_id"],
            "book": {
                "title": book["title"],
                "author": book["author"],
                "edition": book["edition"],
                "year": book["year"],
                "ISBN": book["ISBN"]
            },
            "dueDate": session["dueDate"],
            "defaultChannel": session["defaultChannel"],
            "discussions": [
                {
                    "id": discussion["id"],
                    "title": discussion["title"],
                    "date": discussion["date"],
                    "location": discussion["location"]
                } for discussion in discussions_response.data
            ]
        }

    def add_to_shame_list(self, session_id, member_id):
        """Add a member to the shame list for a session."""
        self.supabase.table("shamelist").insert({
            "session_id": session_id,
            "member_id": member_id
        }).execute()

    def update_session(self, session_id, club_id=None, book_id=None, dueDate=None, defaultChannel=None):
        """Update session details."""
        update_data = {}
        if club_id:
            update_data["club_id"] = club_id
        if book_id:
            update_data["book_id"] = book_id
        if dueDate:
            update_data["dueDate"] = dueDate
        if defaultChannel:
            update_data["defaultChannel"] = defaultChannel
            
        if update_data:
            self.supabase.table("sessions").update(update_data).eq("id", session_id).execute()

    def update_discussion(self, discussion_id, session_id=None, title=None, date=None, location=None):
        """Update discussion details."""
        update_data = {}
        if session_id:
            update_data["session_id"] = session_id
        if title:
            update_data["title"] = title
        if date:
            update_data["date"] = date
        if location:
            update_data["location"] = location
            
        if update_data:
            self.supabase.table("discussions").update(update_data).eq("id", discussion_id).execute()

    def update_member(self, member_id, name=None, points=None, numberOfBooksRead=None):
        """Update member details."""
        update_data = {}
        if name:
            update_data["name"] = name
        if points:
            update_data["points"] = points
        if numberOfBooksRead:
            update_data["numberOfBooksRead"] = numberOfBooksRead
            
        if update_data:
            self.supabase.table("members").update(update_data).eq("id", member_id).execute()

    # TODO: Stop fetching the first club, and instead fetch the club with the given ID
    def get_club(self):
        # Get club data
        club_response = self.supabase.table("clubs").select("*").execute()
        club = club_response.data[0] if club_response.data else None
        
        if not club:
            return None
            
        # Get all members
        members_response = self.supabase.table("members").select("*").execute()
        
        # Transform member data
        members_data = []
        for member in members_response.data:
            # Get clubs for this member
            member_clubs_response = self.supabase.table("memberclubs").select("club_id").eq("member_id", member["id"]).execute()
            club_ids = [item["club_id"] for item in member_clubs_response.data]
            
            members_data.append({
                "id": member["id"],
                "name": member["name"],
                "points": member["points"],
                "clubs": club_ids,
                "numberOfBooksRead": member["numberofbooksread"]
            })
        
        # Get session data
        sessions_response = self.supabase.table("sessions").select("*").execute()
        
        # Transform session data
        session_data = None
        if sessions_response.data:
            session = sessions_response.data[0]  # Assuming one active session
            
            # Get book for this session
            book_response = self.supabase.table("books").select("*").eq("id", session["book_id"]).execute()
            book = book_response.data[0] if book_response.data else None
            
            # Get discussions for this session
            discussions_response = self.supabase.table("discussions").select("*").eq("session_id", session["id"]).execute()
            
            session_data = {
                "id": session["id"],
                "club_id": session["club_id"],
                "book": {
                    "title": book["title"],
                    "author": book["author"],
                    "edition": book["edition"],
                    "year": book["year"],
                    "ISBN": book["isbn"]
                },
                "dueDate": session["duedate"],
                "defaultChannel": session["defaultchannel"],
                "shameList": [],
                "discussions": [
                    {
                        "id": discussion["id"],
                        "session_id": discussion["session_id"],
                        "title": discussion["title"],
                        "date": discussion["date"],
                        "location": discussion["location"]
                    } for discussion in discussions_response.data
                ]
            }
        
        # Return the full reconstructed club data
        return {
            "id": club["id"],
            "name": club["name"],
            "members": members_data,
            "activeSession": session_data,
            "pastSessions": []
        }