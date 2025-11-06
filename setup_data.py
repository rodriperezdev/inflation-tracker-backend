"""
Initial setup script to fetch and store historical inflation data
Run this once after database initialization
"""

from fred_fetcher import InflationDataFetcher
from database import init_db, save_inflation_data
import sys

def setup_initial_data():
    """Fetch and store initial inflation data from 1995 to present"""
    
    print("=" * 60)
    print("Argentine Inflation Tracker - Initial Data Setup")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    
    # Fetch data
    print("\n2. Fetching inflation data...")
    print("   Using hybrid approach:")
    print("   - Historical (1995-2016): CSV file or simulated data")
    print("   - Recent (2017-present): FRED API")
    print()
    
    fetcher = InflationDataFetcher()
    data = fetcher.get_processed_data(start_year=1995)
    
    if not data:
        print("\n✗ ERROR: Failed to fetch data")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Get FREE FRED API key from: https://fred.stlouisfed.org/")
        print("  3. Add to .env: FRED_API_KEY=your_key")
        print("  4. Or add historical CSV file: 'argentina_cpi_historical.csv'")
        sys.exit(1)
    
    print(f"\n   ✓ Successfully fetched {len(data)} months of data")
    print(f"   Date range: {data[0]['date']} to {data[-1]['date']}")
    
    # Save to database
    print("\n3. Saving data to database...")
    success = save_inflation_data(data)
    
    if not success:
        print("\n✗ ERROR: Failed to save data to database")
        sys.exit(1)
    
    # Show summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"\n✓ {len(data)} months of inflation data saved")
    print(f"✓ Coverage: {data[0]['date']} to {data[-1]['date']}")
    print(f"✓ Total years: {len(data) // 12} years")
    
    # Show recent data
    print("\nRecent data (last 5 months):")
    print("-" * 60)
    for record in data[-5:]:
        print(f"  {record['date']}: "
              f"Monthly: {record['monthly_rate']:>6.2f}%, "
              f"Annual: {record['annual_rate']:>7.2f}%, "
              f"CPI: {record['cpi_index']:>10.2f}")
    print("-" * 60)
    
    print("\n✓ API ready to start!")
    print("✓ Run: python main.py")
    print("✓ Visit: http://localhost:8001")
    print()

if __name__ == "__main__":
    try:
        setup_initial_data()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)