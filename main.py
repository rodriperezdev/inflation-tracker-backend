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
        print("Initializing database...")
        init_db()  # Create tables
        
        print("Checking if data exists...")
        from database import SessionLocal, InflationRecord
        db = SessionLocal()
        count = db.query(InflationRecord).count()
        db.close()
        
        if count == 0:
            print("No data found, populating database...")
            from fred_fetcher import InflationDataFetcher
            from database import save_inflation_data
            
            fetcher = InflationDataFetcher()
            data = fetcher.get_processed_data(start_year=1995)
            
            if data:
                save_inflation_data(data)
                print(f"Populated {len(data)} records!")
            else:
                print("Could not fetch data - using empty database")
        else:
            print(f"Database already has {count} records")
            
    except Exception as e:
        print(f"Startup error: {e}")

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