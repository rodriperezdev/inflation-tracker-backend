"""
Quick script to verify data in the database
Shows latest dates and data quality
"""

from database import SessionLocal, InflationRecord
from datetime import date

def verify_data():
    """Check what data is in the database"""
    db = SessionLocal()
    
    try:
        # Get total count
        total = db.query(InflationRecord).count()
        
        # Get date range
        first = db.query(InflationRecord).order_by(InflationRecord.date.asc()).first()
        latest = db.query(InflationRecord).order_by(InflationRecord.date.desc()).first()
        
        # Get 2025 data
        data_2025 = db.query(InflationRecord).filter(
            InflationRecord.year == 2025
        ).order_by(InflationRecord.date.asc()).all()
        
        print("=" * 70)
        print("Database Verification")
        print("=" * 70)
        print(f"\n[OK] Total records: {total}")
        print(f"[OK] Date range: {first.date} to {latest.date}")
        print(f"[OK] Total years: {latest.year - first.year + 1}")
        
        if data_2025:
            print(f"\n[OK] 2025 data: {len(data_2025)} months")
            print("\n2025 months in database:")
            print("-" * 70)
            for record in data_2025:
                print(f"  {record.date}: Monthly={record.monthly_rate:.2f}%, "
                      f"Annual={record.annual_rate:.2f}%, CPI={record.cpi_index:.2f}")
            print("-" * 70)
        else:
            print("\n[WARNING] No 2025 data found")
        
        # Check for gaps
        print("\nChecking for data gaps...")
        all_records = db.query(InflationRecord).order_by(InflationRecord.date.asc()).all()
        gaps = []
        for i in range(len(all_records) - 1):
            current = all_records[i].date
            next_date = all_records[i + 1].date
            # Calculate expected next month
            if current.month == 12:
                expected_next = date(current.year + 1, 1, 1)
            else:
                expected_next = date(current.year, current.month + 1, 1)
            
            if next_date != expected_next:
                gaps.append((current, expected_next, next_date))
        
        if gaps:
            print(f"[WARNING] Found {len(gaps)} gap(s):")
            for gap_start, expected, actual in gaps[:5]:  # Show first 5
                print(f"  Gap after {gap_start}: Expected {expected}, got {actual}")
        else:
            print("[OK] No gaps found - data is continuous")
        
        print("\n" + "=" * 70)
        print("[OK] Database is ready!")
        print("=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()






