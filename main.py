from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uvicorn
from database import (
    get_db, 
    InflationRecord, 
    calculate_price_conversion,
    get_inflation_summary,
    get_cpi_for_date,
    init_db,
    SessionLocal,
    save_inflation_data
)
from sqlalchemy.orm import Session

app = FastAPI(
    title="Argentine Inflation Tracker API",
    description="Track Argentine inflation rates and convert prices across time periods",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    try:
        print("[INFO] Initializing database...")
        init_db()
        
        print("[INFO] Checking if data exists...")
        db = SessionLocal()
        count = db.query(InflationRecord).count()
        
        # Initial population if database is empty
        if count == 0:
            print("[INFO] No data found, populating database...")
            from fred_fetcher import InflationDataFetcher
            
            fetcher = InflationDataFetcher()
            data = fetcher.get_processed_data(start_year=1995)
            
            if data:
                save_inflation_data(data)
                print(f"[OK] Populated {len(data)} records!")
            else:
                print("[WARNING] Could not fetch data")
                db.close()
                return
        else:
            print(f"[OK] Database has {count} records")
        
        # UPDATE RECENT DATA - Same logic as update_recent_data.py
        print("\n[INFO] Checking for missing recent months...")
        latest = db.query(InflationRecord).order_by(InflationRecord.date.desc()).first()
        
        if not latest:
            print("[WARNING] No data in database")
            db.close()
            return
        
        latest_date = latest.date
        current_date = date.today()
        months_diff = (current_date.year - latest_date.year) * 12 + (current_date.month - latest_date.month)
        
        print(f"   Latest date in DB: {latest_date}")
        print(f"   Current date: {current_date}")
        print(f"   Months behind: {months_diff}")
        
        if months_diff > 0:
            print(f"\n[INFO] Fetching {months_diff} missing month(s) from FRED...")
            
            # Fetch recent data from FRED (2017 onwards to ensure we get everything)
            from fred_fetcher import InflationDataFetcher
            fetcher = InflationDataFetcher()
            start_year = latest_date.year if latest_date.year >= 2017 else 2017
            all_data = fetcher.get_processed_data(start_year=start_year)
            
            if all_data:
                # Filter to only new records
                latest_str = latest_date.strftime('%Y-%m-%d')
                new_records = [r for r in all_data if r['date'] > latest_str]
                
                if new_records:
                    print(f"   Found {len(new_records)} new month(s) from FRED")
                    
                    # Save new records
                    for record in new_records:
                        record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
                        
                        # Check if already exists
                        existing = db.query(InflationRecord).filter(
                            InflationRecord.date == record_date
                        ).first()
                        
                        if not existing:
                            new_record = InflationRecord(
                                date=record_date,
                                year=record['year'],
                                month=record['month'],
                                cpi_index=record['cpi_index'],
                                monthly_rate=record['monthly_rate'],
                                annual_rate=record['annual_rate']
                            )
                            db.add(new_record)
                    
                    db.commit()
                    print(f"   [OK] Added {len(new_records)} month(s) from FRED!")
                    
                    # Update latest_date after FRED update
                    latest = db.query(InflationRecord).order_by(InflationRecord.date.desc()).first()
                    latest_date = latest.date
                    months_diff = (current_date.year - latest_date.year) * 12 + (current_date.month - latest_date.month)
                    print(f"   New latest date: {latest_date}")
                else:
                    print("   No new data from FRED")
            else:
                print("   [WARNING] Could not fetch from FRED")
        
        # ADD HARDCODED DATA FOR VERY RECENT MONTHS (FRED doesn't have yet)
        if months_diff > 0:
            print(f"\n[INFO] FRED data not available for last {months_diff} month(s)")
            print("   Adding hardcoded recent data...")
            
            # Hardcoded most recent months (update these with real data!)
            # Get these values from: https://www.indec.gob.ar/ or https://tradingeconomics.com/argentina/inflation-cpi
            very_recent_data = [
                {'year': 2025, 'month': 1, 'monthly_rate': 2.2, 'annual_rate': 84.5},
                {'year': 2025, 'month': 2, 'monthly_rate': 2.4, 'annual_rate': 66.9},
                {'year': 2025, 'month': 3, 'monthly_rate': 3.7, 'annual_rate': 55.9},
                {'year': 2025, 'month': 4, 'monthly_rate': 2.8, 'annual_rate': 47.3},
                {'year': 2025, 'month': 5, 'monthly_rate': 1.5, 'annual_rate': 43.5},
                {'year': 2025, 'month': 6, 'monthly_rate': 1.6, 'annual_rate': 39.4},
                {'year': 2025, 'month': 7, 'monthly_rate': 1.9, 'annual_rate': 37.0},
                {'year': 2025, 'month': 8, 'monthly_rate': 1.9, 'annual_rate': 33.6},
                {'year': 2025, 'month': 9, 'monthly_rate': 2.1, 'annual_rate': 31.8},
            ]
            
            # Only add months after latest_date
            latest_str = latest_date.strftime('%Y-%m-%d')
            current_cpi = latest.cpi_index
            added_count = 0
            
            for month_data in very_recent_data:
                month_date_str = f"{month_data['year']}-{month_data['month']:02d}-01"
                
                # Only add if this month is after latest in DB and not in future
                month_date = datetime.strptime(month_date_str, '%Y-%m-%d').date()
                if month_date > latest_date and month_date <= current_date:
                    # Calculate CPI from previous month
                    current_cpi = current_cpi * (1 + month_data['monthly_rate'] / 100)
                    
                    # Check if already exists
                    existing = db.query(InflationRecord).filter(
                        InflationRecord.date == month_date
                    ).first()
                    
                    if not existing:
                        new_record = InflationRecord(
                            date=month_date,
                            year=month_data['year'],
                            month=month_data['month'],
                            cpi_index=current_cpi,
                            monthly_rate=month_data['monthly_rate'],
                            annual_rate=month_data['annual_rate']
                        )
                        db.add(new_record)
                        added_count += 1
                        print(f"   Added {month_date}: {month_data['monthly_rate']}% monthly")
            
            if added_count > 0:
                db.commit()
                print(f"   [OK] Added {added_count} hardcoded month(s)!")
            else:
                print("   [OK] All months up to date!")
        else:
            print("\n[OK] Database is fully up to date!")
        
        # Show final status
        final_latest = db.query(InflationRecord).order_by(InflationRecord.date.desc()).first()
        print(f"\n[STATUS] Final database status:")
        print(f"   Total records: {db.query(InflationRecord).count()}")
        print(f"   Latest month: {final_latest.date}")
        print(f"   Latest monthly rate: {final_latest.monthly_rate}%")
        print(f"   Latest annual rate: {final_latest.annual_rate}%")
        
        db.close()
            
    except Exception as e:
        print(f"[ERROR] Startup error: {e}")
        import traceback
        traceback.print_exc()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://perezrodri.vercel.app",  # Your production frontend
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response models
class InflationData(BaseModel):
    year: int
    month: int
    date: str
    monthly_rate: float
    annual_rate: float
    cpi_index: float

class PriceConversion(BaseModel):
    original_amount: float
    original_date: str
    target_date: str
    converted_amount: float
    inflation_rate: float
    percentage_change: float

class InflationSummary(BaseModel):
    current_monthly: float
    current_annual: float
    avg_last_12_months: float
    total_inflation_since_1995: float
    last_updated: str

@app.get("/")
def read_root():
    return {
        "message": "Argentine Inflation Tracker API",
        "version": "1.0.0",
        "description": "Track inflation rates and convert prices across time periods in Argentina",
        "endpoints": {
            "/inflation/data": "Get historical inflation data",
            "/inflation/current": "Get current inflation statistics",
            "/inflation/convert": "Convert prices between dates",
            "/inflation/range": "Get inflation for a date range",
            "/inflation/annual": "Get annual inflation rates"
        },
        "data_source": "INDEC via Alphacast",
        "coverage": "1995-present"
    }

@app.head("/")
def read_root_head():
    return {}

@app.get("/inflation/data", response_model=List[InflationData])
async def get_inflation_data(
    start_year: int = Query(1990, ge=1990),
    end_year: Optional[int] = None,
    limit: int = Query(1000, le=10000),  # Increased default limit
    db: Session = Depends(get_db)
):
    """Get historical inflation data from database"""
    query = db.query(InflationRecord).filter(InflationRecord.year >= start_year)
    
    if end_year:
        query = query.filter(InflationRecord.year <= end_year)
    
    # Order by date ascending (oldest first) and limit
    # If limit is 1000 or more, don't apply limit (get all records)
    if limit >= 1000:
        records = query.order_by(InflationRecord.date.asc()).all()
    else:
        records = query.order_by(InflationRecord.date.asc()).limit(limit).all()
    
    if not records:
        raise HTTPException(
            status_code=404, 
            detail="No inflation data found. Please run setup_data.py to populate the database."
        )
    
    # Convert to response format
    result = [
        InflationData(
            year=record.year,
            month=record.month,
            date=record.date.isoformat(),
            monthly_rate=record.monthly_rate,
            annual_rate=record.annual_rate,
            cpi_index=record.cpi_index
        )
        for record in records
    ]
    
    return result

@app.get("/inflation/current", response_model=InflationSummary)
async def get_current_inflation(db: Session = Depends(get_db)):
    """Get current inflation summary from database"""
    summary = get_inflation_summary()
    
    if not summary:
        raise HTTPException(
            status_code=404,
            detail="No inflation data found. Please run setup_data.py to populate the database."
        )
    
    return InflationSummary(
        current_monthly=summary['current_monthly'],
        current_annual=summary['current_annual'],
        avg_last_12_months=summary['avg_last_12_months'],
        total_inflation_since_1995=summary['total_inflation_since_start'],
        last_updated=summary['last_updated']
    )

@app.get("/inflation/convert", response_model=PriceConversion)
async def convert_price(
    amount: float = Query(..., gt=0, description="Amount to convert"),
    from_date: str = Query(..., description="Original date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Convert a price from one date to another based on inflation using actual CPI data"""
    try:
        # Parse dates
        original_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        target_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        
        # Calculate conversion using database
        result = calculate_price_conversion(amount, original_date, target_date)
        
        return PriceConversion(
            original_amount=amount,
            original_date=from_date,
            target_date=to_date,
            converted_amount=result['converted_amount'],
            inflation_rate=result['multiplier'],
            percentage_change=result['percentage_change']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error calculating conversion: {str(e)}. Make sure CPI data exists for both dates."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )

@app.get("/inflation/range")
async def get_inflation_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get total inflation between two dates"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # TODO: Calculate from database
        total_inflation = 234.5  # Sample
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_inflation_percent": total_inflation,
            "multiplier": 1 + (total_inflation / 100),
            "years": (end - start).days / 365.25
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@app.get("/inflation/annual")
async def get_annual_inflation(
    start_year: int = Query(1995, ge=1995),
    end_year: Optional[int] = None
):
    """Get annual inflation rates"""
    if end_year is None:
        end_year = datetime.now().year
    
    # TODO: Calculate from database
    sample_annual = [
        {"year": 2024, "rate": 117.8},
        {"year": 2023, "rate": 211.4},
        {"year": 2022, "rate": 94.8},
        {"year": 2021, "rate": 50.9}
    ]
    
    return {
        "start_year": start_year,
        "end_year": end_year,
        "data": sample_annual
    }

@app.post("/admin/update-data")
async def trigger_data_update():
    """Manually trigger data update from Alphacast"""
    # TODO: Implement data fetching
    return {
        "status": "success",
        "message": "Data update triggered",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)