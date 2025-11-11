"""
Script to update missing recent months in the database
This will fetch the latest data from FRED and add any missing months
"""

from fred_fetcher import InflationDataFetcher
from database import SessionLocal, InflationRecord, init_db
from datetime import datetime, date
import sys

def get_latest_date_in_db():
    """Get the latest date in the database"""
    db = SessionLocal()
    try:
        latest = db.query(InflationRecord).order_by(
            InflationRecord.date.desc()
        ).first()
        
        if latest:
            return latest.date
        return None
    finally:
        db.close()

def save_new_records(records):
    """Save new records to database, skipping duplicates"""
    db = SessionLocal()
    
    try:
        new_count = 0
        updated_count = 0
        
        for record in records:
            # Check if record exists
            record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
            existing = db.query(InflationRecord).filter(
                InflationRecord.date == record_date
            ).first()
            
            if existing:
                # Update existing record
                existing.cpi_index = record['cpi_index']
                existing.monthly_rate = record['monthly_rate']
                existing.annual_rate = record['annual_rate']
                existing.year = record['year']
                existing.month = record['month']
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new record
                inflation_record = InflationRecord(
                    date=record_date,
                    year=record['year'],
                    month=record['month'],
                    cpi_index=record['cpi_index'],
                    monthly_rate=record['monthly_rate'],
                    annual_rate=record['annual_rate']
                )
                db.add(inflation_record)
                new_count += 1
        
        db.commit()
        
        print(f"[OK] Added {new_count} new records")
        print(f"[OK] Updated {updated_count} existing records")
        return True
    
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error saving data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

def main():
    print("=" * 70)
    print("Update Recent Inflation Data")
    print("=" * 70)
    print()
    
    # Check latest date in database
    latest_date = get_latest_date_in_db()
    
    if latest_date:
        print(f"Latest date in database: {latest_date}")
        print(f"Current date: {date.today()}")
        
        # Calculate how many months are missing
        current_date = date.today()
        months_diff = (current_date.year - latest_date.year) * 12 + (current_date.month - latest_date.month)
        
        if months_diff <= 0:
            print("\n[OK] Database is up to date!")
            print("   No new data needed.")
            return
        
        print(f"\nMissing approximately {months_diff} month(s) of data")
    else:
        print("[WARNING] No data found in database")
        print("   Run setup_data.py first to initialize the database")
        sys.exit(1)
    
    print("\n1. Fetching latest data from FRED API...")
    print("-" * 70)
    
    # Fetch recent data (last 2 years to ensure we get everything)
    fetcher = InflationDataFetcher()
    
    # Get data from the year of the latest date to present
    start_year = latest_date.year if latest_date else 2023
    data = fetcher.get_processed_data(start_year=start_year)
    
    if not data:
        print("\n[ERROR] Failed to fetch data from FRED")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify FRED_API_KEY in .env file")
        print("  3. FRED API might have rate limits")
        sys.exit(1)
    
    print(f"\n[OK] Fetched {len(data)} months of data")
    
    # Filter to only include records after the latest date
    # Convert latest_date to YYYY-MM-DD format for comparison
    latest_date_str = latest_date.strftime('%Y-%m-%d')
    
    print(f"\n   Latest date in database: {latest_date_str}")
    print(f"   Total records fetched: {len(data)}")
    if data:
        print(f"   Date range in fetched data: {data[0]['date']} to {data[-1]['date']}")
    
    new_records = [
        record for record in data 
        if record['date'] > latest_date_str
    ]
    
    print(f"   Records after {latest_date_str}: {len(new_records)}")
    
    if not new_records:
        print("\n[OK] No new records found")
        print("   Database is already up to date!")
        return
    
    print(f"\n2. Found {len(new_records)} new month(s) to add:")
    print("-" * 70)
    for record in new_records:
        print(f"   {record['date']}: "
              f"Monthly: {record['monthly_rate']:>6.2f}%, "
              f"Annual: {record['annual_rate']:>7.2f}%, "
              f"CPI: {record['cpi_index']:>10.2f}")
    
    print("\n3. Saving to database...")
    print("-" * 70)
    
    success = save_new_records(new_records)
    
    if not success:
        print("\n[ERROR] Failed to save data")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("[OK] Update Complete!")
    print("=" * 70)
    print(f"\n[OK] Added {len(new_records)} new month(s) of data")
    print(f"[OK] Latest date now: {new_records[-1]['date']}")
    print("\nNext steps:")
    print("  1. Restart backend server (if running)")
    print("  2. Refresh frontend to see new data")
    print("  3. Check graph for updated time series")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ERROR] Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

