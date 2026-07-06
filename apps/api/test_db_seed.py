import os
import sys
from sqlalchemy import text

# Add backend API folder to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "apps", "api"))

from database import SessionLocal
import models

def test_database_counts():
    db = SessionLocal()
    
    print("\n=== SWASTH AI - SEED DATA VERIFICATION ===")
    
    # Query row counts
    counts = {
        "facilities": db.query(models.Facility).count(),
        "staff": db.query(models.Staff).count(),
        "users": db.query(models.User).count(),
        "stock_items": db.query(models.StockItem).count(),
        "stock_movements": db.query(models.StockMovement).count(),
        "footfall_records": db.query(models.FootfallRecord).count(),
        "bed_status": db.query(models.BedStatus).count(),
        "attendance_records": db.query(models.AttendanceRecord).count(),
        "diagnostic_tests": db.query(models.DiagnosticTest).count(),
        "diagnostic_audits": db.query(models.DiagnosticAudit).count(),
        "alerts": db.query(models.Alert).count(),
        "recommendations": db.query(models.Recommendation).count(),
        "facility_scores": db.query(models.FacilityScore).count()
    }
    
    # Print findings
    for table, count in counts.items():
        print(f"Table: {table:<25} | Records: {count}")
        
    print("\nRunning assertions...")
    
    # Assertions
    assert counts["facilities"] == 25, f"Expected 25 facilities, found {counts['facilities']}"
    assert counts["staff"] == 102, f"Expected 102 staff, found {counts['staff']}"
    assert counts["users"] == 5, f"Expected 5 user accounts, found {counts['users']}"  # Admin, DHO, 3 facility staff
    assert counts["stock_items"] > 2400, f"Expected ~2500 stock items, found {counts['stock_items']}"
    assert counts["stock_movements"] >= 24000, f"Expected 24000+ movements, found {counts['stock_movements']}"
    assert counts["footfall_records"] == 4500, f"Expected 4500 footfall records, found {counts['footfall_records']}"
    assert counts["bed_status"] == 10800, f"Expected 10800 bed status entries, found {counts['bed_status']}"
    assert counts["attendance_records"] >= 15000, f"Expected 15000+ attendance records, found {counts['attendance_records']}"
    assert counts["diagnostic_tests"] == 10, f"Expected 10 diagnostic tests, found {counts['diagnostic_tests']}"
    assert counts["diagnostic_audits"] == 1500, f"Expected 1500 diagnostic audits, found {counts['diagnostic_audits']}"
    assert counts["alerts"] == 10, f"Expected 10 alerts, found {counts['alerts']}"
    assert counts["recommendations"] == 2, f"Expected 2 recommendations, found {counts['recommendations']}"
    assert counts["facility_scores"] == 25, f"Expected 25 scores, found {counts['facility_scores']}"
    
    print("\nALL SEED ASSERTIONS PASSED SUCCESSFULLY!")
    
    # Display test samples
    print("\nSample DHO User:")
    dho = db.query(models.User).filter(models.User.role == "dho").first()
    print(f"  Username: {dho.username} | Role: {dho.role} | District: {dho.district}")
    
    print("\nSample Stock Items (first 3):")
    items = db.query(models.StockItem).limit(3).all()
    for it in items:
        print(f"  Medicine: {it.medicine_name:<25} | Qty: {it.quantity:<5} | Min: {it.min_threshold:<5} | Max: {it.max_threshold:<5}")
        
    db.close()

if __name__ == "__main__":
    try:
        test_database_counts()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
