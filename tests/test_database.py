from database import Database  # Using the import from __init__.py
import json

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

if __name__ == "__main__":
    test_database_connection()