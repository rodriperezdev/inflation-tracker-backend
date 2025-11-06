import pandas as pd
from fredapi import Fred
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class InflationDataFetcher:
    """
    Fetch inflation data using hybrid approach:
    1. Historical data (1995-2016): From CSV file
    2. Recent data (2017-present): From FRED API
    """
    
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY', 'your_fred_api_key')
        self.fred = Fred(api_key=self.api_key)
        
        # FRED series for Argentina CPI (OECD data, 2017-present)
        # This series has monthly data and is actively updated
        self.cpi_series_id = 'ARGCPALTT01GYM'  # Year-over-year growth rate
        
    def load_historical_csv(self, filepath: str = 'argentina_cpi_historical.csv') -> pd.DataFrame:
        """
        Load historical CPI data from CSV file (1995-2016)
        CSV should have columns: date, cpi
        """
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                
                # Check if CSV has 'cpi' column (from fetch_historical_data.py) or 'cpi_index'
                if 'cpi' in df.columns:
                    # Rename 'cpi' to 'cpi_index' for consistency with rest of code
                    df = df.rename(columns={'cpi': 'cpi_index'})
                elif 'cpi_index' not in df.columns:
                    raise ValueError(f"CSV must have 'date' and either 'cpi' or 'cpi_index' column. Found: {list(df.columns)}")
                
                df['date'] = pd.to_datetime(df['date'])
                print(f"✓ Loaded historical data from {filepath}")
                print(f"   Records: {len(df)}, Date range: {df['date'].min()} to {df['date'].max()}")
                return df
            else:
                print(f"⚠️  Historical CSV file not found: {filepath}")
                print("   Creating sample data for demonstration...")
                return self.create_sample_data()
        except Exception as e:
            print(f"Error loading historical CSV: {e}")
            return pd.DataFrame()
    
    def create_sample_data(self) -> pd.DataFrame:
        """Create sample historical data for testing"""
        # Create monthly data from 1995-2016
        dates = pd.date_range(start='1995-01-01', end='2016-12-31', freq='MS')
        
        # Simulated CPI with realistic Argentine inflation patterns
        base_cpi = 100
        cpi_values = [base_cpi]
        
        for i in range(1, len(dates)):
            # Simulate high and variable inflation (realistic for Argentina)
            monthly_inflation = 0.01 + (0.03 * (i % 12) / 12)  # Variable monthly rate
            cpi_values.append(cpi_values[-1] * (1 + monthly_inflation))
        
        df = pd.DataFrame({
            'date': dates,
            'cpi': cpi_values
        })
        
        print("ℹ️  Using simulated data for 1995-2016")
        print("   To use real data, add 'argentina_cpi_historical.csv' file")
        return df
    
    def fetch_recent_fred_data(self, start_date: str = '2017-01-01') -> pd.DataFrame:
        """
        Fetch recent CPI data from FRED (2017-present)
        Uses OECD Argentina CPI series
        """
        try:
            print(f"Fetching recent data from FRED (series: {self.cpi_series_id})...")
            print(f"   From: {start_date} to present")
            
            # Get data up to current date (no end_date = gets all available)
            data = self.fred.get_series(
                self.cpi_series_id,
                observation_start=start_date,
                observation_end=None  # Get all available data up to today
            )
            
            if len(data) == 0:
                print("⚠️  No recent data from FRED")
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'date': data.index,
                'annual_growth_rate': data.values
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            df = df.dropna()
            
            # Reconstruct CPI index from growth rates
            # Start with a base value that connects to historical data
            df['cpi'] = 100.0
            for i in range(1, len(df)):
                # Convert annual growth rate to monthly multiplier
                annual_rate = df.loc[i, 'annual_growth_rate'] / 100
                monthly_multiplier = (1 + annual_rate) ** (1/12)
                df.loc[i, 'cpi'] = df.loc[i-1, 'cpi'] * monthly_multiplier
            
            print(f"✓ Fetched {len(df)} months from FRED")
            return df[['date', 'cpi']]
        
        except Exception as e:
            print(f"Error fetching from FRED: {e}")
            print("Using CSV data only")
            return pd.DataFrame()
    
    def combine_data_sources(self, start_year: int = 1995) -> pd.DataFrame:
        """
        Combine historical CSV and recent FRED data
        """
        # Load historical data (1995-2016)
        historical = self.load_historical_csv()
        
        # Get recent data from FRED (2017-present)
        recent = self.fetch_recent_fred_data('2017-01-01')
        
        if historical.empty and recent.empty:
            print("✗ No data available from any source")
            return pd.DataFrame()
        
        # Combine datasets
        if not historical.empty and not recent.empty:
            # Normalize recent CPI to connect with historical
            # Use 'cpi_index' for historical (from CSV) and 'cpi' for recent (from FRED)
            historical_cpi_col = 'cpi_index' if 'cpi_index' in historical.columns else 'cpi'
            last_historical_cpi = historical.iloc[-1][historical_cpi_col]
            first_recent_cpi = recent.iloc[0]['cpi']
            adjustment_factor = last_historical_cpi / first_recent_cpi
            recent['cpi'] = recent['cpi'] * adjustment_factor
            
            # Rename historical column to 'cpi' for consistency
            if historical_cpi_col == 'cpi_index':
                historical = historical.rename(columns={'cpi_index': 'cpi'})
            
            combined = pd.concat([historical, recent], ignore_index=True)
        elif not historical.empty:
            combined = historical
        else:
            combined = recent
        
        # Filter by start year
        combined = combined[combined['date'].dt.year >= start_year]
        combined = combined.sort_values('date').reset_index(drop=True)
        combined = combined.drop_duplicates(subset=['date'], keep='last')
        
        return combined
    
    def calculate_inflation_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate monthly and annual inflation rates"""
        if df.empty:
            return df
        
        df = df.sort_values('date').copy()
        
        # Monthly inflation (month-over-month)
        df['monthly_rate'] = df['cpi'].pct_change() * 100
        
        # Annual inflation (year-over-year, 12-month change)
        df['annual_rate'] = df['cpi'].pct_change(periods=12) * 100
        
        # Fill NaN
        df['monthly_rate'] = df['monthly_rate'].fillna(0)
        df['annual_rate'] = df['annual_rate'].fillna(0)
        
        return df
    
    def get_processed_data(self, start_year: int = 1995) -> List[Dict]:
        """Get fully processed inflation data ready for database"""
        df = self.combine_data_sources(start_year)
        
        if df.empty:
            return []
        
        df = self.calculate_inflation_rates(df)
        
        # Add year and month
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        # Convert to list of dicts
        records = []
        for _, row in df.iterrows():
            records.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'year': int(row['year']),
                'month': int(row['month']),
                'cpi_index': float(row['cpi']),
                'monthly_rate': float(row['monthly_rate']),
                'annual_rate': float(row['annual_rate'])
            })
        
        return records


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Inflation Data Fetcher")
    print("=" * 60)
    
    fetcher = InflationDataFetcher()
    
    print("\nFetching inflation data...")
    data = fetcher.get_processed_data(start_year=1995)
    
    if data:
        print(f"\n✓ Successfully processed {len(data)} months of data")
        print(f"✓ Date range: {data[0]['date']} to {data[-1]['date']}")
        print(f"✓ Total years: {len(data) // 12}")
        
        print("\nSample data (last 5 months):")
        print("-" * 80)
        print(f"{'Date':<12} {'CPI Index':<12} {'Monthly %':<12} {'Annual %':<12}")
        print("-" * 80)
        for record in data[-5:]:
            print(f"{record['date']:<12} {record['cpi_index']:<12.2f} "
                  f"{record['monthly_rate']:<12.2f} {record['annual_rate']:<12.2f}")
        print("-" * 80)
        print("\n✓ Data ready to use!")
        print("✓ Run 'python setup_data.py' to load into database")
    else:
        print("\n✗ No data fetched")
    
    print("\n" + "=" * 60)