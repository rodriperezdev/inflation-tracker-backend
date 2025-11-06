# Data Setup Guide for Inflation Tracker

## Issues Fixed

1. ✅ **Price Converter**: Now uses actual CPI data from database instead of hardcoded 50% rate
2. ✅ **Time Series Data**: Endpoints now pull from database instead of sample data
3. ✅ **Database Integration**: All endpoints connected to database

## How to Get Real Inflation Data

### Option 1: Using FRED API (Recommended - Free)

FRED (Federal Reserve Economic Data) provides free access to Argentine CPI data.

#### Steps:

1. **Get a FREE FRED API Key**:
   - Go to: https://fred.stlouisfed.org/
   - Sign up for a free account
   - Go to: https://fred.stlouisfed.org/docs/api/api_key.html
   - Create an API key (it's free!)

2. **Add API Key to Environment**:
   - Create or edit `.env` file in `inflation-tracker-backend/`
   - Add: `FRED_API_KEY=your_api_key_here`

3. **Run Setup Script**:
   ```bash
   cd inflation-tracker-backend
   python setup_data.py
   ```

   This will:
   - Fetch historical data (1995-2016) - creates sample data if CSV not found
   - Fetch recent data (2017-present) from FRED API
   - Calculate inflation rates
   - Save everything to database

### Option 2: Using Historical CSV File

If you have historical CPI data in CSV format:

1. **Create CSV file** named `argentina_cpi_historical.csv` in `inflation-tracker-backend/`
   
   Format should be:
   ```csv
   date,cpi
   1995-01-01,100.0
   1995-02-01,101.5
   1995-03-01,103.2
   ...
   ```

2. **Run Setup Script**:
   ```bash
   python setup_data.py
   ```

### Option 3: Using Alphacast API (Alternative)

The code includes an Alphacast fetcher. To use it:

1. Get Alphacast API key from: https://www.alphacast.io/
2. Add to `.env`: `ALPHACAST_API_KEY=your_key`
3. Modify `setup_data.py` to use Alphacast instead of FRED

## Data Sources Available

### FRED Series for Argentina:
- **ARGCPALTT01GYM**: Year-over-year CPI growth (OECD data)
- **ARGCPALTT01IXOBM**: Month-over-month CPI growth
- Covers 2017-present

### Historical Data (1995-2016):
- Can be provided via CSV file
- Or use simulated data for testing (already included)

## After Setup

Once you've run `setup_data.py`:

1. **Restart the backend server**:
   ```bash
   python main.py
   ```

2. **Verify data**:
   - Check: `http://localhost:8002/inflation/data?limit=10`
   - Should show real data instead of sample data

3. **Test price converter**:
   - Try converting 1000 pesos from 2020 to 2024
   - Should show realistic inflation (around 500-800% for Argentina)

## Troubleshooting

### "No inflation data found" error:
- Run `python setup_data.py` first
- Make sure database file `inflation.db` exists
- Check that data was saved successfully

### FRED API not working:
- Verify API key is correct in `.env`
- Check internet connection
- FRED might have rate limits (try again later)

### Data looks incorrect:
- Check that CPI values are reasonable (should be increasing over time)
- Verify date ranges are correct
- Historical data might need adjustment if using CSV

## Updating Data

To update with latest data:

```bash
python setup_data.py
```

This will:
- Fetch new data from FRED
- Update existing records
- Add any missing months

## Expected Results

After setup, you should have:
- ✅ **~350+ months** of data (1995-2024)
- ✅ **Accurate price conversions** (e.g., 1000 pesos in 2020 ≈ 5000-8000 pesos in 2024)
- ✅ **Real inflation rates** (monthly and annual)
- ✅ **Complete time series** for graphs


