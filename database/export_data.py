import sqlite3
import json
import os

def export_sqlite_data(db_path="bookclub.db"):
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for database at: {os.path.abspath(db_path)}")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file '{db_path}' not found!")
        return
    
    # Connect to your database
    try:
        conn = sqlite3.connect(db_path)
        print("Successfully connected to database")
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Found tables: {tables}")
        
        # Dictionary to store all data
        all_data = {}
        
        # Export each table
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            table_data = []
            for row in rows:
                table_data.append({key: row[key] for key in row.keys()})
            
            all_data[table] = table_data
            print(f"Exported {len(table_data)} rows from table '{table}'")
        
        conn.close()
        
        # Save to a JSON file
        output_path = "database_export.json"
        with open(output_path, "w") as f:
            json.dump(all_data, f, indent=4)
        
        print(f"Exported data to: {os.path.abspath(output_path)}")
        return all_data
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Run the export function
if __name__ == "__main__":
    export_sqlite_data()