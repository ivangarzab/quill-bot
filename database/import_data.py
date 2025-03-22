import json
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

def import_to_supabase(json_path="database_export.json"):
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing Supabase credentials in .env file")
        return
    
    print(f"Connecting to Supabase at {supabase_url[:20]}...")
    
    # Connect to Supabase
    supabase = create_client(supabase_url, supabase_key)
    
    # Load exported data
    print(f"Loading data from {json_path}...")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        print(f"Successfully loaded data with tables: {', '.join(data.keys())}")
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return
    
    # Tables in order (respecting foreign keys)
    table_order = ["Clubs", "Members", "Books", "MemberClubs", "Sessions", "Discussions", "ShameList"]
    
    # Import each table
    for table in table_order:
        if table in data and data[table]:
            print(f"Importing {len(data[table])} rows into {table}...")
            
            # For debugging: print the first row
            if data[table]:
                print(f"First row sample: {json.dumps(data[table][0], indent=2)}")
            
            # Insert data
            try:
                response = supabase.table(table).insert(data[table]).execute()
                
                # Check response
                if hasattr(response, 'data') and response.data:
                    print(f"Successfully imported {len(response.data)} rows into {table}")
                else:
                    error_info = getattr(response, 'error', 'Unknown error')
                    status = getattr(response, 'status_code', 'Unknown status')
                    print(f"Error response: Status {status}, Error: {error_info}")
                    
            except Exception as e:
                print(f"Exception while importing {table}: {str(e)}")
    
    print("Import process completed!")

# Run the import
if __name__ == "__main__":
    import_to_supabase()