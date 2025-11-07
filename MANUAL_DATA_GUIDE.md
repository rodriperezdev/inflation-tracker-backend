# Manual Data Entry Guide

## How to Add Missing 2025 Data

### Option 1: Edit the Script (Recommended)

1. **Open `add_manual_data.py`** in the `inflation-tracker-backend/` directory

2. **Edit the `example_data` list** in the `main()` function:

```python
example_data = [
    {'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0},
    {'year': 2025, 'month': 4, 'monthly_rate': 5.0, 'annual_rate': 185.0},
    {'year': 2025, 'month': 5, 'monthly_rate': 5.5, 'annual_rate': 190.0},
    # Add more months as needed...
]
```

3. **Run the script**:
```bash
cd inflation-tracker-backend
python add_manual_data.py
```

### Option 2: Interactive Mode

Run the script in interactive mode to add data one month at a time:

```bash
python add_manual_data.py --interactive
```

The script will prompt you for:
- Year (e.g., 2025)
- Month (1-12)
- Monthly rate % (e.g., 4.5 for 4.5%)
- Annual rate % (e.g., 180.0 for 180%)
- CPI index (optional - will be calculated if not provided)

### Option 3: Python Script

You can also create a custom script:

```python
from add_manual_data import add_multiple_months

# Add your data
data = [
    {'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0},
    {'year': 2025, 'month': 4, 'monthly_rate': 5.0, 'annual_rate': 185.0},
    {'year': 2025, 'month': 5, 'monthly_rate': 5.5, 'annual_rate': 190.0},
    {'year': 2025, 'month': 6, 'monthly_rate': 6.0, 'annual_rate': 195.0},
    {'year': 2025, 'month': 7, 'monthly_rate': 6.5, 'annual_rate': 200.0},
    {'year': 2025, 'month': 8, 'monthly_rate': 7.0, 'annual_rate': 205.0},
    {'year': 2025, 'month': 9, 'monthly_rate': 7.5, 'annual_rate': 210.0},
    {'year': 2025, 'month': 10, 'monthly_rate': 8.0, 'annual_rate': 215.0},
    {'year': 2025, 'month': 11, 'monthly_rate': 8.5, 'annual_rate': 220.0},
    {'year': 2025, 'month': 12, 'monthly_rate': 9.0, 'annual_rate': 225.0},
]

add_multiple_months(data)
```

## Data Format

Each month requires:
- **year**: Year (e.g., 2025)
- **month**: Month number (1-12)
- **monthly_rate**: Monthly inflation rate as percentage (e.g., 4.5 for 4.5%)
- **annual_rate**: Annual inflation rate as percentage (e.g., 180.0 for 180%)
- **cpi_index**: (Optional) CPI index value. If not provided, it will be calculated automatically from the previous month

## CPI Calculation

If you don't provide `cpi_index`, the script will:
1. Look for the previous month's CPI in the database
2. Calculate new CPI using: `new_cpi = previous_cpi × (1 + monthly_rate / 100)`
3. If previous month not found, use the latest available CPI

## Where to Find Inflation Data

For Argentina inflation data, check:
- **INDEC (Instituto Nacional de Estadística y Censos)**: https://www.indec.gob.ar/
- **BCRA (Banco Central de la República Argentina)**: https://www.bcra.gob.ar/
- **Government economic reports**: Official monthly inflation announcements

## Example: Adding March 2025 Data

If INDEC reports:
- Monthly inflation: 4.5%
- Annual inflation: 180.0%

Add to script:
```python
{'year': 2025, 'month': 3, 'monthly_rate': 4.5, 'annual_rate': 180.0}
```

## After Adding Data

1. **Restart backend server** (if running):
   ```bash
   # Stop current server (Ctrl+C)
   python main.py
   ```

2. **Refresh frontend**:
   - Hard refresh browser (Ctrl+Shift+R)
   - Check graph shows new months

3. **Test price converter**:
   - Try converting with dates in 2025
   - Should work with new data

## Notes

- The script will **update** existing records if the date already exists
- CPI is calculated automatically if not provided
- All months are validated before saving
- Database is updated in real-time



