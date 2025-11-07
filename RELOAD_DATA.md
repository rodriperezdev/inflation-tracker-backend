# Reload Data Guide

## Steps to Replace Database with New CSV Data

### 1. Stop the Backend Server
If the backend is running, stop it first:
- Press `Ctrl+C` in the terminal where it's running

### 2. Delete the Old Database
```bash
cd inflation-tracker-backend
del inflation.db
```
Or on Linux/Mac:
```bash
rm inflation.db
```

### 3. Verify CSV File Exists
Make sure `argentina_cpi_historical.csv` is in the `inflation-tracker-backend/` directory:
```bash
dir argentina_cpi_historical.csv
```

The CSV should have this format:
```csv
date,cpi
1995-01-01,100.0
1995-02-01,101.5
...
```

### 4. Run Setup Script
```bash
python setup_data.py
```

This will:
- ✅ Create a fresh database
- ✅ Load historical data from `argentina_cpi_historical.csv` (1995-2016)
- ✅ Fetch recent data from FRED API (2017-present)
- ✅ Combine both datasets
- ✅ Calculate inflation rates
- ✅ Save everything to the database

### 5. Verify Data Loaded
Check the output - you should see:
- ✓ Number of months saved
- ✓ Date range (should be 1995-2025)
- ✓ Sample of recent data

### 6. Restart Backend Server
```bash
python main.py
```

The server should start on port 8002 (or check your .env file)

### 7. Test the API
- Visit: `http://localhost:8002/inflation/data?limit=10`
- Should show data from oldest to newest
- Check the graph in the frontend

## Troubleshooting

### "No such file: inflation.db"
- This is normal after deleting - setup_data.py will create a new one

### "CSV file not found"
- Make sure `argentina_cpi_historical.csv` is in the same directory as `setup_data.py`
- Check the file name (case-sensitive on Linux/Mac)

### "Database locked" error
- Make sure the backend server is stopped
- Close any database viewers or tools
- Try deleting the database again

### Data looks wrong
- Check the CSV format - should have `date,cpi` columns
- Verify dates are in YYYY-MM-DD format
- Check that CPI values are reasonable (should increase over time)

## Expected Results

After running `setup_data.py`, you should have:
- ✅ Fresh database with all data
- ✅ Historical data from CSV (1995-2016)
- ✅ Recent data from FRED (2017-2025)
- ✅ ~350+ months of data
- ✅ Accurate price conversions
- ✅ Complete time series graph



