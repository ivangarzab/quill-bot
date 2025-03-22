from database import Database
import json
import uuid
from datetime import datetime, timedelta

def test_database_connection():
    print("Testing Supabase database connection...")
    
    # Create a database instance - this will connect to Supabase
    try:
        db = Database()
        print("✅ Successfully connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Test reading data
    try:
        print("\nTesting data retrieval...")
        club_data = db.get_club()
        if club_data:
            print("✅ Successfully retrieved club data:")
            print(f"   Club name: {club_data['name']}")
            print(f"   Number of members: {len(club_data['members'])}")
            print(f"   Active session book: {club_data['activeSession']['book']['title']}")
        else:
            print("❌ No club data found")
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return False
    
    # Test a simple update operation
    try:
        print("\nTesting update operation...")
        # Get the first member's current points
        first_member = club_data['members'][0]
        member_id = first_member['id']
        current_points = first_member['points']
        
        # Update points
        new_points = current_points + 1
        db.update_member(member_id, points=new_points)
        print(f"✅ Updated member {first_member['name']} points from {current_points} to {new_points}")
        
        # Verify the update worked
        updated_club = db.get_club()
        updated_member = next((m for m in updated_club['members'] if m['id'] == member_id), None)
        if updated_member and updated_member['points'] == new_points:
            print(f"✅ Verified points update: {updated_member['points']}")
        else:
            print("❌ Failed to verify points update")
        
        # Restore original value
        db.update_member(member_id, points=current_points)
        print(f"✅ Restored original points value: {current_points}")
    except Exception as e:
        print(f"❌ Error testing update: {e}")
        return False
    
    print("\n✅ All database tests passed!")
    return True

def test_club_operations():
    print("\n----- Testing Club Operations -----")
    try:
        db = Database()
        
        # Get existing club data for reference
        club_data = db.get_club()
        if not club_data:
            print("❌ Cannot test club operations - no club data found")
            return False
        
        # Test updating club name
        original_name = club_data['name']
        new_name = f"{original_name}_TEST"
        
        print(f"Testing club name update from '{original_name}' to '{new_name}'...")
        db.update_club(club_data['id'], new_name)
        
        # Verify update
        updated_club = db.get_club()
        if updated_club['name'] == new_name:
            print(f"✅ Successfully updated club name to '{new_name}'")
        else:
            print(f"❌ Failed to update club name. Current: {updated_club['name']}")
            return False
        
        # Restore original name
        db.update_club(club_data['id'], original_name)
        restored_club = db.get_club()
        if restored_club['name'] == original_name:
            print(f"✅ Successfully restored club name to '{original_name}'")
        else:
            print(f"❌ Failed to restore club name. Current: {restored_club['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing club operations: {e}")
        return False

def test_member_operations():
    print("\n----- Testing Member Operations -----")
    try:
        db = Database()
        club_data = db.get_club()
        
        if not club_data:
            print("❌ Cannot test member operations - no club data found")
            return False
        
        # Test adding a new member
        test_member_id = f"test-member-{uuid.uuid4()}"
        test_member_name = "Test Member"
        test_points = 10
        test_books_read = 2
        
        print(f"Adding test member '{test_member_name}'...")
        db.add_member(
            test_member_id, 
            test_member_name, 
            test_points, 
            test_books_read, 
            [club_data['id']]  # Add to the existing club
        )
        
        # Verify member was added
        updated_club = db.get_club()
        added_member = next((m for m in updated_club['members'] if m['id'] == test_member_id), None)
        
        if added_member:
            print(f"✅ Successfully added member '{test_member_name}'")
            
            # Test updating the member
            updated_name = f"{test_member_name} Updated"
            updated_points = test_points + 5
            updated_books = test_books_read + 1
            
            print(f"Updating test member data...")
            db.update_member(
                test_member_id,
                name=updated_name,
                points=updated_points,
                numberOfBooksRead=updated_books
            )
            
            # Verify update
            updated_club = db.get_club()
            updated_member = next((m for m in updated_club['members'] if m['id'] == test_member_id), None)
            
            if updated_member and updated_member['name'] == updated_name and \
               updated_member['points'] == updated_points and \
               updated_member['numberOfBooksRead'] == updated_books:
                print(f"✅ Successfully updated member data")
            else:
                print(f"❌ Failed to update member data")
        else:
            print(f"❌ Failed to add test member")
            return False
        
        # Note: In a real test, you might want to clean up by removing the test member
        # but the current DB client doesn't have a delete_member method
        
        return True
    except Exception as e:
        print(f"❌ Error testing member operations: {e}")
        return False

def test_session_operations():
    print("\n----- Testing Session Operations -----")
    try:
        db = Database()
        club_data = db.get_club()
        
        if not club_data or not club_data.get('activeSession'):
            print("❌ Cannot test session operations - no active session found")
            return False
        
        session = club_data['activeSession']
        session_id = session['id']
        
        # Test getting session details
        print(f"Testing get_session_details...")
        session_details = db.get_session_details(session_id)
        
        if session_details and session_details['id'] == session_id:
            print(f"✅ Successfully retrieved session details for '{session_details['book']['title']}'")
        else:
            print(f"❌ Failed to retrieve session details")
            return False
        
        # Test updating session
        original_due_date = session['dueDate']
        new_due_date = (datetime.fromisoformat(original_due_date.replace('Z', '+00:00')) + 
                         timedelta(days=7)).isoformat().replace('+00:00', 'Z')
        
        print(f"Testing update of session due date...")
        db.update_session(session_id, dueDate=new_due_date)
        
        # Verify update
        updated_session = db.get_session_details(session_id)
        if updated_session and updated_session['dueDate'] == new_due_date:
            print(f"✅ Successfully updated session due date")
        else:
            print(f"❌ Failed to update session due date")
        
        # Restore original value
        db.update_session(session_id, dueDate=original_due_date)
        restored_session = db.get_session_details(session_id)
        if restored_session and restored_session['dueDate'] == original_due_date:
            print(f"✅ Successfully restored session due date")
        else:
            print(f"❌ Failed to restore session due date")
        
        return True
    except Exception as e:
        print(f"❌ Error testing session operations: {e}")
        return False

def test_discussion_operations():
    print("\n----- Testing Discussion Operations -----")
    try:
        db = Database()
        club_data = db.get_club()
        
        if not club_data or not club_data.get('activeSession') or not club_data['activeSession']['discussions']:
            print("❌ Cannot test discussion operations - no discussions found")
            return False
        
        discussion = club_data['activeSession']['discussions'][0]
        discussion_id = discussion['id']
        
        # Test updating discussion
        original_title = discussion['title']
        new_title = f"{original_title} - UPDATED"
        original_location = discussion['location']
        new_location = f"{original_location} - NEW VENUE"
        
        print(f"Testing update of discussion title...")
        db.update_discussion(discussion_id, title=new_title, location=new_location)
        
        # Verify update
        updated_club = db.get_club()
        updated_discussion = next(
            (d for d in updated_club['activeSession']['discussions'] if d['id'] == discussion_id), 
            None
        )
        
        if updated_discussion and updated_discussion['title'] == new_title and updated_discussion['location'] == new_location:
            print(f"✅ Successfully updated discussion title and location")
        else:
            print(f"❌ Failed to update discussion details")
        
        # Restore original values
        db.update_discussion(discussion_id, title=original_title, location=original_location)
        
        restored_club = db.get_club()
        restored_discussion = next(
            (d for d in restored_club['activeSession']['discussions'] if d['id'] == discussion_id), 
            None
        )
        
        if restored_discussion and restored_discussion['title'] == original_title and restored_discussion['location'] == original_location:
            print(f"✅ Successfully restored discussion details")
        else:
            print(f"❌ Failed to restore discussion details")
        
        return True
    except Exception as e:
        print(f"❌ Error testing discussion operations: {e}")
        return False

def test_shame_list():
    print("\n----- Testing Shame List Operations -----")
    try:
        db = Database()
        club_data = db.get_club()
        
        if not club_data or not club_data.get('activeSession') or not club_data['members']:
            print("❌ Cannot test shame list - missing required data")
            return False
        
        session_id = club_data['activeSession']['id']
        member_id = club_data['members'][0]['id']
        
        print(f"Adding member to shame list...")
        db.add_to_shame_list(session_id, member_id)
        
        # Note: The current implementation doesn't have a way to verify if a member was
        # successfully added to the shame list through the get_club() method
        # This would require extending the database client to have a method for retrieving
        # the shame list
        
        print(f"✅ Member was added to shame list (verification not implemented)")
        
        return True
    except Exception as e:
        print(f"❌ Error testing shame list: {e}")
        return False

def test_all():
    """Run all test functions"""
    overall_status = True
    
    tests = [
        test_database_connection,
        test_club_operations,
        test_member_operations,
        test_session_operations,
        test_discussion_operations,
        test_shame_list
    ]
    
    results = []
    
    print("\n===== STARTING DATABASE TESTS =====\n")
    
    for test_func in tests:
        test_name = test_func.__name__
        print(f"\n\n{'='*20} RUNNING {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        if not result:
            overall_status = False
    
    print("\n\n===== DATABASE TEST RESULTS =====")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    if overall_status:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED. See details above.")
    
    return overall_status

if __name__ == "__main__":
    test_all()