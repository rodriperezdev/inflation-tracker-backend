"""
Safe script to reload database with new CSV data
This will:
1. Check if backend is running
2. Delete old database
3. Verify CSV file exists
4. Run setup_data.py to reload everything
"""

import os
import sys
from pathlib import Path

def check_backend_running():
    """Check if backend server might be running"""
    print("⚠️  Make sure the backend server is STOPPED before proceeding!")
    print("   If it's running, press Ctrl+C to stop it now.")
    print()
    
    response = input("Is the backend server stopped? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n✗ Please stop the backend server first!")
        print("   Then run this script again.")
        sys.exit(1)

def delete_database():
    """Delete the old database file"""
    db_file = Path('inflation.db')
    
    if db_file.exists():
        try:
            db_file.unlink()
            print("✓ Deleted old database: inflation.db")
            return True
        except Exception as e:
            print(f"✗ Error deleting database: {e}")
            print("   Make sure the backend server is stopped!")
            return False
    else:
        print("ℹ️  No existing database found (this is OK for first-time setup)")
        return True

def verify_csv():
    """Verify CSV file exists and has correct format"""
    csv_file = Path('argentina_cpi_historical.csv')
    
    if not csv_file.exists():
        print(f"\n✗ CSV file not found: {csv_file}")
        print("   Make sure 'argentina_cpi_historical.csv' is in the current directory")
        print("   Run 'python fetch_historical_data.py' first to create it")
        return False
    
    print(f"✓ Found CSV file: {csv_file}")
    
    # Quick check of file format
    try:
        import pandas as pd
        df = pd.read_csv(csv_file, nrows=5)
        
        if 'date' not in df.columns or 'cpi' not in df.columns:
            print(f"\n✗ CSV file has wrong format!")
            print(f"   Expected columns: date, cpi")
            print(f"   Found columns: {list(df.columns)}")
            return False
        
        print(f"✓ CSV format looks correct")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Sample dates: {df['date'].head().tolist()}")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Could not verify CSV format: {e}")
        print("   Proceeding anyway...")
        return True

def main():
    print("=" * 70)
    print("Database Reload Script")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Delete the old database (inflation.db)")
    print("  2. Load historical data from CSV (1995-2016)")
    print("  3. Fetch recent data from FRED API (2017-present)")
    print("  4. Combine and save everything to a fresh database")
    print()
    
    # Check if backend is stopped
    check_backend_running()
    
    # Delete old database
    print("\n1. Deleting old database...")
    if not delete_database():
        sys.exit(1)
    
    # Verify CSV exists
    print("\n2. Verifying CSV file...")
    if not verify_csv():
        sys.exit(1)
    
    # Run setup
    print("\n3. Running setup_data.py...")
    print("-" * 70)
    
    try:
        from setup_data import setup_initial_data
        setup_initial_data()
        
        print("\n" + "=" * 70)
        print("✓ Database reload complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Start the backend: python main.py")
        print("  2. Verify data: http://localhost:8002/inflation/data?limit=10")
        print("  3. Check the graph in the frontend")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Reload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


