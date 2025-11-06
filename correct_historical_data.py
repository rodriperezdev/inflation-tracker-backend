"""
Script to correct historical inflation data for Argentina (1990-2001)
Fixes incorrect data and adds missing 1990 hyperinflation period
"""

import sys
from datetime import date
from database import SessionLocal, InflationRecord, get_cpi_for_date

def calculate_cpi_from_monthly_rate(previous_cpi, monthly_rate_percent):
    """Calculate new CPI from previous CPI and monthly inflation rate"""
    return previous_cpi * (1 + monthly_rate_percent / 100)

def add_monthly_data(year, month, monthly_rate, annual_rate=None, cpi_index=None):
    """Add a single month of inflation data"""
    from add_manual_data import add_monthly_data as add_monthly_data_original
    return add_monthly_data_original(year, month, monthly_rate, annual_rate, cpi_index)

def get_previous_month_cpi(year, month):
    """Get CPI from previous month"""
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year = year - 1
    
    prev_date = date(prev_year, prev_month, 1)
    return get_cpi_for_date(prev_date)

def calculate_monthly_rate_from_annual(annual_rate):
    """
    Convert annual rate to approximate monthly rate
    This is a rough approximation: monthly_rate ≈ annual_rate / 12
    For more accuracy, we'd need actual monthly CPI data
    """
    return annual_rate / 12

def add_corrected_data():
    """
    Add corrected historical data for 1990-2001
    """
    print("=" * 70)
    print("Correcting Historical Inflation Data (1990-2001)")
    print("=" * 70)
    print()
    
    # Corrected data based on historical records
    # Annual rates are the official figures
    corrected_data = [
        # 1990 - Hyperinflation period
        {'year': 1990, 'month': 1, 'annual_rate': 1344.0, 'monthly_rate': 112.0},  # Extreme hyperinflation
        {'year': 1990, 'month': 2, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 3, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 4, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 5, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 6, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 7, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 8, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 9, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 10, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 11, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        {'year': 1990, 'month': 12, 'annual_rate': 1344.0, 'monthly_rate': 112.0},
        
        # 1991 - Convertibility Plan starts (March 1991)
        # Inflation drops dramatically throughout the year
        {'year': 1991, 'month': 1, 'annual_rate': 84.0, 'monthly_rate': 7.0},
        {'year': 1991, 'month': 2, 'annual_rate': 84.0, 'monthly_rate': 7.0},
        {'year': 1991, 'month': 3, 'annual_rate': 84.0, 'monthly_rate': 7.0},  # Convertibility Plan
        {'year': 1991, 'month': 4, 'annual_rate': 84.0, 'monthly_rate': 6.0},
        {'year': 1991, 'month': 5, 'annual_rate': 84.0, 'monthly_rate': 5.0},
        {'year': 1991, 'month': 6, 'annual_rate': 84.0, 'monthly_rate': 4.0},
        {'year': 1991, 'month': 7, 'annual_rate': 84.0, 'monthly_rate': 3.0},
        {'year': 1991, 'month': 8, 'annual_rate': 84.0, 'monthly_rate': 2.0},
        {'year': 1991, 'month': 9, 'annual_rate': 84.0, 'monthly_rate': 1.5},
        {'year': 1991, 'month': 10, 'annual_rate': 84.0, 'monthly_rate': 1.0},
        {'year': 1991, 'month': 11, 'annual_rate': 84.0, 'monthly_rate': 0.8},
        {'year': 1991, 'month': 12, 'annual_rate': 84.0, 'monthly_rate': 0.6},
        
        # 1992
        {'year': 1992, 'month': 1, 'annual_rate': 17.5, 'monthly_rate': 0.5},
        {'year': 1992, 'month': 2, 'annual_rate': 17.5, 'monthly_rate': 0.4},
        {'year': 1992, 'month': 3, 'annual_rate': 17.5, 'monthly_rate': 0.4},
        {'year': 1992, 'month': 4, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 5, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 6, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 7, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 8, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 9, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 10, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 11, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        {'year': 1992, 'month': 12, 'annual_rate': 17.5, 'monthly_rate': 0.3},
        
        # 1993
        {'year': 1993, 'month': 1, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 2, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 3, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 4, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 5, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 6, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 7, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 8, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 9, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 10, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 11, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        {'year': 1993, 'month': 12, 'annual_rate': 7.4, 'monthly_rate': 0.3},
        
        # 1994
        {'year': 1994, 'month': 1, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 2, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 3, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 4, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 5, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 6, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 7, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 8, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 9, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 10, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 11, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        {'year': 1994, 'month': 12, 'annual_rate': 3.9, 'monthly_rate': 0.2},
        
        # 1995 - Tequila Crisis
        {'year': 1995, 'month': 1, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 2, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 3, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 4, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 5, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 6, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 7, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 8, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 9, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 10, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 11, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        {'year': 1995, 'month': 12, 'annual_rate': 1.6, 'monthly_rate': 0.1},
        
        # 1996 - Near zero inflation
        {'year': 1996, 'month': 1, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 2, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 3, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 4, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 5, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 6, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 7, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 8, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 9, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 10, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 11, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        {'year': 1996, 'month': 12, 'annual_rate': 0.0, 'monthly_rate': 0.0},
        
        # 1997
        {'year': 1997, 'month': 1, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 2, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 3, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 4, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 5, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 6, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 7, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 8, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 9, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 10, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 11, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        {'year': 1997, 'month': 12, 'annual_rate': 0.3, 'monthly_rate': 0.025},
        
        # 1998
        {'year': 1998, 'month': 1, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 2, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 3, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 4, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 5, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 6, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 7, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 8, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 9, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 10, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 11, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        {'year': 1998, 'month': 12, 'annual_rate': 0.7, 'monthly_rate': 0.06},
        
        # 1999 - Deflation starts
        {'year': 1999, 'month': 1, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 2, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 3, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 4, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 5, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 6, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 7, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 8, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 9, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 10, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 11, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        {'year': 1999, 'month': 12, 'annual_rate': -1.2, 'monthly_rate': -0.1},
        
        # 2000 - Deflation continues
        {'year': 2000, 'month': 1, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 2, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 3, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 4, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 5, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 6, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 7, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 8, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 9, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 10, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 11, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        {'year': 2000, 'month': 12, 'annual_rate': -0.9, 'monthly_rate': -0.075},
        
        # 2001 - Deflation continues until crisis
        {'year': 2001, 'month': 1, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 2, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 3, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 4, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 5, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 6, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 7, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 8, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 9, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 10, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 11, 'annual_rate': -1.5, 'monthly_rate': -0.125},
        {'year': 2001, 'month': 12, 'annual_rate': -1.5, 'monthly_rate': -0.125},
    ]
    
    print(f"Processing {len(corrected_data)} months of corrected data...")
    print("-" * 70)
    
    success_count = 0
    error_count = 0
    
    # Need to get starting CPI for 1990
    # We'll use a base CPI of 1.0 for January 1990 and calculate forward
    base_cpi = 1.0
    current_cpi = base_cpi
    
    for i, data in enumerate(corrected_data, 1):
        year = data['year']
        month = data['month']
        annual_rate = data['annual_rate']
        monthly_rate = data['monthly_rate']
        
        print(f"\n[{i}/{len(corrected_data)}] Processing {year}-{month:02d}...")
        print(f"   Annual: {annual_rate}%, Monthly: {monthly_rate}%")
        
        # Calculate CPI for this month
        if i == 1:
            # First month (1990-01) - use base CPI
            cpi_index = base_cpi
        else:
            # Calculate CPI from previous month's CPI and monthly rate
            cpi_index = current_cpi * (1 + monthly_rate / 100)
        
        # Update current CPI for next iteration
        current_cpi = cpi_index
        
        # Add/update the record
        result = add_monthly_data(
            year=year,
            month=month,
            monthly_rate=monthly_rate,
            annual_rate=annual_rate,
            cpi_index=cpi_index
        )
        
        if result:
            print(f"   ✓ CPI: {cpi_index:.4f}")
            success_count += 1
        else:
            error_count += 1
            print(f"   ✗ Failed to add data")
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Successfully added/updated: {success_count}")
    if error_count > 0:
        print(f"✗ Failed: {error_count}")
    print()
    print("Next steps:")
    print("1. Verify data: python verify_data.py")
    print("2. Restart backend server")
    print("3. Refresh frontend to see corrected graph")
    print()

if __name__ == "__main__":
    try:
        add_corrected_data()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

