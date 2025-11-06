from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./inflation.db')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InflationRecord(Base):
    """Monthly inflation data"""
    __tablename__ = "inflation_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    
    # CPI and inflation rates
    cpi_index = Column(Float)
    monthly_rate = Column(Float)  # Month-over-month inflation %
    annual_rate = Column(Float)   # Year-over-year inflation %
    
    # Metadata
    data_source = Column(String, default='alphacast')
    updated_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully!")


def save_inflation_data(records: list):
    """Save inflation records to database"""
    db = SessionLocal()
    
    try:
        for record in records:
            # Check if record exists
            existing = db.query(InflationRecord).filter(
                InflationRecord.date == datetime.strptime(record['date'], '%Y-%m-%d').date()
            ).first()
            
            if existing:
                # Update existing record
                existing.cpi_index = record['cpi_index']
                existing.monthly_rate = record['monthly_rate']
                existing.annual_rate = record['annual_rate']
                existing.updated_at = datetime.now(timezone.utc)
            else:
                # Create new record
                inflation_record = InflationRecord(
                    date=datetime.strptime(record['date'], '%Y-%m-%d').date(),
                    year=record['year'],
                    month=record['month'],
                    cpi_index=record['cpi_index'],
                    monthly_rate=record['monthly_rate'],
                    annual_rate=record['annual_rate']
                )
                db.add(inflation_record)
        
        db.commit()
        print(f"✓ Saved/updated {len(records)} inflation records")
        return True
    
    except Exception as e:
        db.rollback()
        print(f"✗ Error saving data: {e}")
        return False
    
    finally:
        db.close()


def get_cpi_for_date(target_date: datetime.date):
    """Get CPI index for a specific date, or closest available date if exact match not found"""
    db = SessionLocal()
    try:
        # Try exact date match first
        record = db.query(InflationRecord).filter(
            InflationRecord.date == target_date
        ).first()
        
        if record:
            return record.cpi_index
        
        # If exact date not found, try to find same month
        year_month = db.query(InflationRecord).filter(
            InflationRecord.year == target_date.year,
            InflationRecord.month == target_date.month
        ).first()
        
        if year_month:
            return year_month.cpi_index
        
        # If date is in the future, use the latest available CPI
        latest_record = db.query(InflationRecord).order_by(
            InflationRecord.date.desc()
        ).first()
        
        if latest_record and target_date > latest_record.date:
            print(f"⚠️ Requested date {target_date} is after latest available date {latest_record.date}. Using latest CPI.")
            return latest_record.cpi_index
        
        # If date is before first record, use first available CPI
        earliest_record = db.query(InflationRecord).order_by(
            InflationRecord.date.asc()
        ).first()
        
        if earliest_record and target_date < earliest_record.date:
            print(f"⚠️ Requested date {target_date} is before earliest available date {earliest_record.date}. Using earliest CPI.")
            return earliest_record.cpi_index
        
        return None
    
    finally:
        db.close()


def calculate_price_conversion(amount: float, from_date: datetime.date, to_date: datetime.date):
    """Calculate price conversion between two dates"""
    from_cpi = get_cpi_for_date(from_date)
    to_cpi = get_cpi_for_date(to_date)
    
    if from_cpi is None or to_cpi is None:
        raise ValueError("CPI data not available for one or both dates")
    
    # Formula: New Price = Old Price × (New CPI / Old CPI)
    multiplier = to_cpi / from_cpi
    converted_amount = amount * multiplier
    percentage_change = (multiplier - 1) * 100
    
    return {
        'original_amount': amount,
        'converted_amount': round(converted_amount, 2),
        'multiplier': round(multiplier, 4),
        'percentage_change': round(percentage_change, 2),
        'from_cpi': from_cpi,
        'to_cpi': to_cpi
    }


def get_inflation_summary():
    """Get summary statistics"""
    db = SessionLocal()
    try:
        # Get most recent record
        latest = db.query(InflationRecord).order_by(
            InflationRecord.date.desc()
        ).first()
        
        if not latest:
            return None
        
        # Get records from last 12 months
        from datetime import timedelta
        one_year_ago = latest.date - timedelta(days=365)
        
        last_12_months = db.query(InflationRecord).filter(
            InflationRecord.date >= one_year_ago
        ).all()
        
        avg_monthly = sum(r.monthly_rate for r in last_12_months) / len(last_12_months) if last_12_months else 0
        
        # Calculate total inflation since 1995
        first_record = db.query(InflationRecord).order_by(
            InflationRecord.date.asc()
        ).first()
        
        total_inflation = 0
        if first_record and latest:
            total_inflation = ((latest.cpi_index / first_record.cpi_index) - 1) * 100
        
        return {
            'current_monthly': latest.monthly_rate,
            'current_annual': latest.annual_rate,
            'avg_last_12_months': round(avg_monthly, 2),
            'total_inflation_since_start': round(total_inflation, 2),
            'last_updated': latest.date.isoformat()
        }
    
    finally:
        db.close()


# Initialize database on import
if __name__ == "__main__":
    init_db()