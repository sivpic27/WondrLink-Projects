import sys
import os

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from supabase_client import get_supabase_client

def check_schema():
    print("Checking schema...")
    client = get_supabase_client()
    try:
        # Try to select one row
        res = client.table('pdf_chunks').select('*').limit(1).execute()
        if res.data:
            print("Columns in first row:", res.data[0].keys())
        else:
            print("No data in pdf_chunks, but query succeeded.")
            
        # Also check profile update logic imports
        print("Checking logic imports...")
        from llm_utils import extract_profile_updates_from_query
        print("Imports successful.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
