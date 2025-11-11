"""
Script to manually add inflation data for missing months
Use this to add 2025 data or any other months that FRED doesn't have yet
"""

from database import SessionLocal, InflationRecord, get_cpi_for_date
from datetime import datetime, date, timezone
import sys

def get_latest_cpi():
    """Get the latest CPI value from database"""
    db = SessionLocal()
    try:
        latest = db.query(InflationRecord).order_by(
            InflationRecord.date.desc()
        ).first()
        
        if latest:
            return latest.cpi_index, latest.date
        return None, None
    finally:
        db.close()

def calculate_cpi_from_monthly_rate(previous_cpi, monthly_rate_percent):
    """Calculate new CPI from previous CPI and monthly inflation rate"""
    return previous_cpi * (1 + monthly_rate_percent / 100)

def estimate_annual_rate_from_monthly(monthly_rate, recent_trend=12):
    """
    Estimate annual rate from monthly rate
    
    This is a rough approximation. The actual annual rate compares
    the current month to the same month 12 months ago.
    
    Args:
        monthly_rate: Monthly inflation rate as percentage
        recent_trend: Number of recent months to consider (default 12)
    
    Returns:
        Estimated annual rate
    """
    # Simple approximation: multiply monthly rate by 12
    # This is rough but useful if you don't have exact year-over-year data
    return monthly_rate * 12

def get_annual_rate_from_database(year, month):
    """
    Try to get actual annual rate by comparing to same month 12 months ago
    Returns None if previous year's data not available
    """
    db = SessionLocal()
    try:
        # Get current month's CPI
        current_date = date(year, month, 1)
        current_record = db.query(InflationRecord).filter(
            InflationRecord.date == current_date
        ).first()
        
        if not current_record:
            return None
        
        # Get same month from previous year
        prev_year = year - 1
        prev_date = date(prev_year, month, 1)
        prev_record = db.query(InflationRecord).filter(
            InflationRecord.date == prev_date
        ).first()
        
        if not prev_record:
            return None
        
        # Calculate year-over-year inflation
        annual_rate = ((current_record.cpi_index / prev_record.cpi_index) - 1) * 100
        return annual_rate
        
    finally:
        db.close()

def add_monthly_data(year, month, monthly_rate, annual_rate=None, cpi_index=None):
    """
    Add a single month of inflation data
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        monthly_rate: Monthly inflation rate as percentage (e.g., 5.2 for 5.2%)
        annual_rate: Annual inflation rate as percentage (optional). If not provided:
                     - Will try to calculate from database (comparing to 12 months ago)
                     - If that fails, will estimate from monthly rate
        cpi_index: Optional CPI index. If not provided, will calculate from previous month
    """
    db = SessionLocal()
    
    try:
        record_date = date(year, month, 1)
        
        # Calculate annual_rate if not provided
        if annual_rate is None:
            print(f"   Calculating annual rate...")
            calculated_annual = get_annual_rate_from_database(year, month)
            if calculated_annual is not None:
                annual_rate = calculated_annual
                print(f"   [OK] Calculated annual rate from database: {annual_rate:.2f}%")
            else:
                # Estimate from monthly rate (rough approximation)
                annual_rate = estimate_annual_rate_from_monthly(monthly_rate)
                print(f"   [WARNING] Could not calculate from database. Estimated: {annual_rate:.2f}%")
                print(f"      (Note: This is approximate. Actual annual rate compares to 12 months ago)")
        
        # Check if record already exists
        existing = db.query(InflationRecord).filter(
            InflationRecord.date == record_date
        ).first()
        
        if existing:
            print(f"[WARNING] Record for {record_date} already exists. Updating...")
            existing.monthly_rate = monthly_rate
            existing.annual_rate = annual_rate
            
            # Calculate or update CPI
            if cpi_index:
                existing.cpi_index = cpi_index
            else:
                # Calculate CPI from previous month
                prev_month = month - 1
                prev_year = year
                if prev_month == 0:
                    prev_month = 12
                    prev_year = year - 1
                
                prev_date = date(prev_year, prev_month, 1)
                prev_cpi = get_cpi_for_date(prev_date)
                
                if prev_cpi:
                    existing.cpi_index = calculate_cpi_from_monthly_rate(prev_cpi, monthly_rate)
                    print(f"   Calculated CPI from previous month: {existing.cpi_index:.2f}")
                else:
                    print(f"[WARNING] Could not find previous month's CPI. Using latest CPI.")
                    latest_cpi, latest_date = get_latest_cpi()
                    if latest_cpi:
                        # Estimate months between latest and current
                        months_diff = (year - latest_date.year) * 12 + (month - latest_date.month)
                        if months_diff > 0:
                            existing.cpi_index = latest_cpi * ((1 + monthly_rate / 100) ** months_diff)
                        else:
                            existing.cpi_index = calculate_cpi_from_monthly_rate(latest_cpi, monthly_rate)
                        print(f"   Estimated CPI from latest data: {existing.cpi_index:.2f}")
                    else:
                        print(f"[ERROR] Could not calculate CPI. Please provide cpi_index manually.")
                        return False
            
            existing.updated_at = datetime.now(timezone.utc)
        else:
            # Calculate CPI if not provided
            if not cpi_index:
                prev_month = month - 1
                prev_year = year
                if prev_month == 0:
                    prev_month = 12
                    prev_year = year - 1
                
                prev_date = date(prev_year, prev_month, 1)
                prev_cpi = get_cpi_for_date(prev_date)
                
                if prev_cpi:
                    cpi_index = calculate_cpi_from_monthly_rate(prev_cpi, monthly_rate)
                    print(f"   Calculated CPI from previous month: {cpi_index:.2f}")
                else:
                    print(f"[WARNING] Could not find previous month's CPI. Using latest CPI.")
                    latest_cpi, latest_date = get_latest_cpi()
                    if latest_cpi:
                        # Estimate months between latest and new date
                        months_diff = (year - latest_date.year) * 12 + (month - latest_date.month)
                        cpi_index = latest_cpi * ((1 + monthly_rate / 100) ** months_diff)
                        print(f"   Estimated CPI from latest data: {cpi_index:.2f}")
                    else:
                        print(f"[ERROR] Could not calculate CPI. Please provide cpi_index manually.")
                        return False
            
            # Create new record
            new_record = InflationRecord(
                date=record_date,
                year=year,
                month=month,
                cpi_index=cpi_index,
                monthly_rate=monthly_rate,
                annual_rate=annual_rate
            )
            db.add(new_record)
        
        db.commit()
        
        # Get final CPI value for display (either from existing or calculated)
        final_cpi = existing.cpi_index if existing else cpi_index
        if final_cpi is None:
            # Should not happen, but handle gracefully
            final_cpi = 0.0
        
        print(f"[OK] Added/updated {record_date}: Monthly={monthly_rate}%, Annual={annual_rate:.2f}%, CPI={final_cpi:.2f}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error adding data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def add_multiple_months(data_list):
    """
    Add multiple months of data at once
    
    Args:
        data_list: List of dicts with keys: year, month, monthly_rate, annual_rate, cpi_index (optional)
                  Example: [
                      {'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0},
                      {'year': 2025, 'month': 4, 'monthly_rate': 5.0, 'annual_rate': 185.0, 'cpi_index': 3150000.0}
                  ]
    """
    print("=" * 70)
    print("Adding Multiple Months of Data")
    print("=" * 70)
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, data in enumerate(data_list, 1):
        print(f"\n[{i}/{len(data_list)}] Processing {data['year']}-{data['month']:02d}...")
        
        result = add_monthly_data(
            year=data['year'],
            month=data['month'],
            monthly_rate=data['monthly_rate'],
            annual_rate=data['annual_rate'],
            cpi_index=data.get('cpi_index')
        )
        
        if result:
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"[OK] Successfully added: {success_count}")
    if fail_count > 0:
        print(f"[ERROR] Failed: {fail_count}")
    print()

def interactive_add():
    """Interactive mode to add data one month at a time"""
    print("=" * 70)
    print("Interactive Data Entry")
    print("=" * 70)
    print("\nEnter inflation data for each month.")
    print("Press Enter with empty values to finish.\n")
    
    months = []
    month_num = 1
    
    while True:
        print(f"\nMonth {month_num}:")
        try:
            year_input = input("  Year (e.g., 2025): ").strip()
            if not year_input:
                break
            year = int(year_input)
            
            month_input = input("  Month (1-12): ").strip()
            if not month_input:
                break
            month = int(month_input)
            
            if month < 1 or month > 12:
                print("  [ERROR] Invalid month. Must be 1-12.")
                continue
            
            monthly_input = input("  Monthly rate % (e.g., 5.2): ").strip()
            if not monthly_input:
                break
            monthly_rate = float(monthly_input)
            
            annual_input = input("  Annual rate % (optional, press Enter to calculate): ").strip()
            annual_rate = float(annual_input) if annual_input else None
            
            cpi_input = input("  CPI index (optional, press Enter to calculate): ").strip()
            cpi_index = float(cpi_input) if cpi_input else None
            
            months.append({
                'year': year,
                'month': month,
                'monthly_rate': monthly_rate,
                'annual_rate': annual_rate,
                'cpi_index': cpi_index
            })
            
            month_num += 1
            
        except ValueError as e:
            print(f"  [ERROR] Invalid input: {e}")
            continue
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            return
    
    if months:
        print(f"\n[OK] Adding {len(months)} month(s) of data...")
        add_multiple_months(months)
    else:
        print("\nNo data entered.")

def main():
    """Main function with example data"""
    print("=" * 70)
    print("Manual Data Entry for Inflation Tracker")
    print("=" * 70)
    print()
    
    # Example: Add March 2025 data
    # You can modify this section to add your own data
    example_data = [
        # Example format:
        # {'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0},
        # {'year': 2025, 'month': 4, 'monthly_rate': 5.0, 'annual_rate': 185.0},
        # Add more months as needed
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_add()
    elif example_data:
        print("Using example data from script...")
        add_multiple_months(example_data)
    else:
        print("No data provided. Use one of these methods:")
        print("\n1. Edit this script and add data to the 'example_data' list")
        print("2. Run with --interactive flag: python add_manual_data.py --interactive")
        print("\nExample data format:")
        print("  {'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0}")
        print("  {'year': 2025, 'month': 4, 'monthly_rate': 5.0, 'annual_rate': 185.0, 'cpi_index': 3200000.0}")
        print("\nNote: If you don't provide cpi_index, it will be calculated from previous month.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

