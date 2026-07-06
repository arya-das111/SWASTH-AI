import os
import sys
import uuid
import random
from datetime import datetime, date, timedelta
from passlib.hash import bcrypt

# Add backend API folder to path to import models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "apps", "api"))

import models
from database import engine, SessionLocal

# Clear and recreate database tables
print("Recreating database tables...")
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Seed constants
START_DATE = date.today() - timedelta(days=180)
END_DATE = date.today()
BLOCKS = ["Chinhat", "Mohanlalganj", "Kakori", "Malihabad", "Bakshi Ka Talab"]
MEDICINE_CATEGORIES = ["Analgesic", "Antibiotic", "Anti-malarial", "ORS/Nutrition", "Anti-diabetic", "Cardiovascular", "Respiratory"]

# Common medicines (SKU library)
MEDICINE_LIB = [
    {"name": "Paracetamol 500mg", "generic": "Paracetamol", "category": "Analgesic", "unit": "tablets"},
    {"name": "Amoxicillin 250mg", "generic": "Amoxicillin", "category": "Antibiotic", "unit": "tablets"},
    {"name": "ORS Powder 20.5g", "generic": "Oral Rehydration Salts", "category": "ORS/Nutrition", "unit": "sachets"},
    {"name": "Artesunate 60mg", "generic": "Artesunate", "category": "Anti-malarial", "unit": "vials"},
    {"name": "Metformin 500mg", "generic": "Metformin", "category": "Anti-diabetic", "unit": "tablets"},
    {"name": "Amlodipine 5mg", "generic": "Amlodipine", "category": "Cardiovascular", "unit": "tablets"},
    {"name": "Salbutamol Inhaler 100mcg", "generic": "Salbutamol", "category": "Respiratory", "unit": "inhalers"},
    {"name": "Azithromycin 500mg", "generic": "Azithromycin", "category": "Antibiotic", "unit": "tablets"},
    {"name": "Ibuprofen 400mg", "generic": "Ibuprofen", "category": "Analgesic", "unit": "tablets"},
    {"name": "Zinc Sulfate 20mg", "generic": "Zinc Sulfate", "category": "ORS/Nutrition", "unit": "tablets"},
    {"name": "Chloroquine 250mg", "generic": "Chloroquine Phosphate", "category": "Anti-malarial", "unit": "tablets"},
    {"name": "Glimepiride 2mg", "generic": "Glimepiride", "category": "Anti-diabetic", "unit": "tablets"},
    {"name": "Atorvastatin 10mg", "generic": "Atorvastatin", "category": "Cardiovascular", "unit": "tablets"},
    {"name": "Cetirizine 10mg", "generic": "Cetirizine", "category": "Respiratory", "unit": "tablets"},
]

# Add more items to reach ~50 distinct SKUs for diversity (mapped to 100 overall entries)
while len(MEDICINE_LIB) < 50:
    idx = len(MEDICINE_LIB)
    MEDICINE_LIB.append({
        "name": f"Essential Med {idx} 100mg",
        "generic": f"Generic Med {idx}",
        "category": random.choice(MEDICINE_CATEGORIES),
        "unit": "tablets"
    })

# Tests library
TESTS_LIB = [
    {"name": "Complete Blood Count (CBC)", "category": "Blood", "mandated": True},
    {"name": "Random Blood Sugar (RBS)", "category": "Blood", "mandated": True},
    {"name": "Urine Routine & Microscopy", "category": "Urine", "mandated": True},
    {"name": "Malaria Rapid Diagnostic Test", "category": "Blood", "mandated": True},
    {"name": "Dengue NS1 Antigen", "category": "Blood", "mandated": True},
    {"name": "Sputum for AFB (TB)", "category": "Sputum", "mandated": True},
    {"name": "HIV Rapid Test", "category": "Blood", "mandated": True},
    {"name": "Pregnancy Test (UPT)", "category": "Urine", "mandated": True},
    {"name": "Chest X-Ray", "category": "Imaging", "mandated": False},
    {"name": "Electrocardiogram (ECG)", "category": "Cardiography", "mandated": False},
]

print("1. Seeding Diagnostic Tests...")
db_tests = []
for t in TESTS_LIB:
    test = models.DiagnosticTest(
        test_name=t["name"],
        category=t["category"],
        is_mandated=t["mandated"]
    )
    db.add(test)
    db_tests.append(test)
db.commit()

# Create Facilities (25 facilities: 5 CHCs, 20 PHCs)
print("2. Seeding Facilities...")
db_facilities = []

# Generate 5 CHCs (Community Health Centres)
for i in range(5):
    block = BLOCKS[i]
    chc = models.Facility(
        hfr_id=f"CHC-LKO-{block.upper()[:3]}-01",
        name=f"{block} CHC",
        type="CHC",
        district="Lucknow",
        block=block,
        state="Uttar Pradesh",
        latitude=26.8467 + random.uniform(-0.1, 0.1),
        longitude=80.9462 + random.uniform(-0.1, 0.1),
        total_bed_capacity=30,
        default_language=random.choice(["hi", "en"])
    )
    db.add(chc)
    db_facilities.append(chc)

# Generate 20 PHCs (Primary Health Centres) - 4 per block
for i in range(20):
    block = BLOCKS[i % 5]
    phc_num = (i // 5) + 1
    phc = models.Facility(
        hfr_id=f"PHC-LKO-{block.upper()[:3]}-0{phc_num}",
        name=f"{block} PHC {phc_num}",
        type="PHC",
        district="Lucknow",
        block=block,
        state="Uttar Pradesh",
        latitude=26.8467 + random.uniform(-0.15, 0.15),
        longitude=80.9462 + random.uniform(-0.15, 0.15),
        total_bed_capacity=random.choice([6, 10]),
        default_language=random.choice(["hi", "en"])
    )
    db.add(phc)
    db_facilities.append(phc)

db.commit()

# Seed Staff and Users
print("3. Seeding Staff and Users...")
db_staff = []
db_users = []

# Default password for all seed users
hashed_password = bcrypt.hash("password123")

# Seed District Health Officer (DHO)
dho_staff = models.Staff(
    facility_id=db_facilities[0].facility_id,  # Map DHO to first CHC for relationship, but they represent district
    name="Dr. Anil Kumar",
    role="dho",
    phone="9876543210",
    email="dho.lucknow@swasth.gov.in",
    language_pref="en"
)
db.add(dho_staff)
db.commit()

dho_user = models.User(
    staff_id=dho_staff.staff_id,
    username="dho_lucknow",
    password_hash=hashed_password,
    role="dho",
    facility_id=None,
    district="Lucknow",
    state="Uttar Pradesh",
    language_pref="en"
)
db.add(dho_user)
db.commit()

# Seed System Admin
admin_staff = models.Staff(
    facility_id=db_facilities[0].facility_id,
    name="System Admin",
    role="system_admin",
    phone="9999999999",
    email="admin@swasth.gov.in"
)
db.add(admin_staff)
db.commit()

admin_user = models.User(
    staff_id=admin_staff.staff_id,
    username="admin",
    password_hash=hashed_password,
    role="system_admin",
    facility_id=None,
    district=None,
    state=None
)
db.add(admin_user)
db.commit()

# Seed staff per facility
first_phc_id = None
facility_staff_map = {} # facility_id -> list of staff

for f in db_facilities:
    facility_staff_map[f.facility_id] = []
    
    # Standard facility staff
    # 1. Medical Officer (MO)
    mo = models.Staff(
        facility_id=f.facility_id,
        name=f"Dr. Rajesh {f.name.split()[0]}",
        role="medical_officer",
        phone=f"9000{random.randint(100000, 999999)}",
        email=f"mo.{f.name.lower().replace(' ', '')}@swasth.gov.in",
        language_pref=f.default_language
    )
    db.add(mo)
    
    # 2. Pharmacist
    pharmacist = models.Staff(
        facility_id=f.facility_id,
        name=f"Suresh Sharma ({f.name.split()[0]})",
        role="pharmacist",
        phone=f"9111{random.randint(100000, 999999)}",
        email=f"pharma.{f.name.lower().replace(' ', '')}@swasth.gov.in",
        language_pref=f.default_language
    )
    db.add(pharmacist)
    
    # 3. Nurse
    nurse = models.Staff(
        facility_id=f.facility_id,
        name=f"Sister Geeta ({f.name.split()[0]})",
        role="nurse",
        phone=f"9222{random.randint(100000, 999999)}",
        email=f"nurse.{f.name.lower().replace(' ', '')}@swasth.gov.in",
        language_pref=f.default_language
    )
    db.add(nurse)
    
    # 4. Ward Clerk / Store Clerk (Extra staff)
    clerk = models.Staff(
        facility_id=f.facility_id,
        name=f"Amit Verma ({f.name.split()[0]})",
        role="store_clerk" if random.choice([True, False]) else "ward_clerk",
        phone=f"9333{random.randint(100000, 999999)}",
        email=f"clerk.{f.name.lower().replace(' ', '')}@swasth.gov.in",
        language_pref=f.default_language
    )
    db.add(clerk)

    db.commit()
    db_staff.extend([mo, pharmacist, nurse, clerk])
    facility_staff_map[f.facility_id].extend([mo, pharmacist, nurse, clerk])
    
    # Seed explicit credentials for the FIRST facility for easy logins
    if first_phc_id is None and f.type == "PHC":
        first_phc_id = f.facility_id
        
        # User for Medical Officer
        mo_user = models.User(
            staff_id=mo.staff_id,
            username="mo_phc1",
            password_hash=hashed_password,
            role="medical_officer",
            facility_id=f.facility_id,
            district=f.district,
            state=f.state,
            language_pref=f.default_language
        )
        db.add(mo_user)
        
        # User for Nurse
        nurse_user = models.User(
            staff_id=nurse.staff_id,
            username="nurse_phc1",
            password_hash=hashed_password,
            role="nurse",
            facility_id=f.facility_id,
            district=f.district,
            state=f.state,
            language_pref=f.default_language
        )
        db.add(nurse_user)

        # User for Pharmacist
        pharmacist_user = models.User(
            staff_id=pharmacist.staff_id,
            username="pharmacist_phc1",
            password_hash=hashed_password,
            role="pharmacist",
            facility_id=f.facility_id,
            district=f.district,
            state=f.state,
            language_pref=f.default_language
        )
        db.add(pharmacist_user)
        db.commit()

# Seed Stock Items
print("4. Seeding Stock Items...")
db_stock_items = []
facility_stock_map = {} # facility_id -> list of stock items

for f in db_facilities:
    facility_stock_map[f.facility_id] = []
    # Seed 100 SKUs per facility (selected randomly from library of 50 items, modifying batch numbers to simulate multiple stock items)
    # We want around 100 stock items per facility
    skus_added = set()
    for j in range(100):
        lib_item = random.choice(MEDICINE_LIB)
        sku_key = (lib_item["name"], f"BATCH-{random.randint(100, 199)}")
        
        if sku_key in skus_added:
            continue
        skus_added.add(sku_key)
        
        # Determine quantity and thresholds
        min_t = random.choice([50, 100, 200])
        max_t = min_t * random.choice([5, 8, 10])
        
        # Set some items as low or stock-out initially
        qty = random.randint(min_t // 2, max_t)
        if random.random() < 0.08:  # 8% chance of stock-out scenario
            qty = random.randint(0, int(min_t * 0.15))
            
        stock_item = models.StockItem(
            facility_id=f.facility_id,
            medicine_name=lib_item["name"],
            generic_name=lib_item["generic"],
            category=lib_item["category"],
            unit=lib_item["unit"],
            batch_no=sku_key[1],
            quantity=qty,
            expiry_date=date.today() + timedelta(days=random.randint(-30, 720)), # some batches expired
            min_threshold=min_t,
            max_threshold=max_t
        )
        db.add(stock_item)
        db_stock_items.append(stock_item)
        facility_stock_map[f.facility_id].append(stock_item)
        
db.commit()

# Seed Stock Movements (25,000+ total)
print("5. Seeding Stock Movements...")
# To reach 25,000+ movements, we need about 1,000 movements per facility, spread over 180 days.
# That is ~5 movements per day per facility.
movements = []

# To speed up insertion, compile mappings
movement_mappings = []

for f in db_facilities:
    facility_staff = facility_staff_map[f.facility_id]
    pharmacists = [s for s in facility_staff if s.role == 'pharmacist']
    ph_staff_id = pharmacists[0].staff_id if pharmacists else facility_staff[0].staff_id
    
    facility_stock = facility_stock_map[f.facility_id]
    if not facility_stock:
        continue
        
    # Simulate historical log
    for d in range(180):
        current_date = START_DATE + timedelta(days=d)
        dt = datetime.combine(current_date, datetime.min.time())
        
        # Generate 4-7 movements per day
        num_movs = random.randint(4, 7)
        for _ in range(num_movs):
            item = random.choice(facility_stock)
            
            # 80% out (dispensed), 20% in (receive stock)
            is_out = random.random() < 0.8
            if is_out:
                mov_type = "out"
                qty = random.randint(5, 30)
                # Ensure we don't go below zero during generation (we just log it)
                item.quantity = max(0, item.quantity - qty)
            else:
                mov_type = "in"
                qty = random.choice([100, 200, 500])
                item.quantity += qty
                
            movement_mappings.append({
                "movement_id": str(uuid.uuid4()),
                "sku_id": item.sku_id,
                "facility_id": f.facility_id,
                "movement_type": mov_type,
                "quantity": qty,
                "batch_no": item.batch_no,
                "reference_note": f"Daily dispensing log" if mov_type == 'out' else "Stock delivery check-in",
                "user_id": ph_staff_id,
                "timestamp": dt + timedelta(hours=random.randint(9, 17), minutes=random.randint(0, 59))
            })

print(f"Bulk inserting {len(movement_mappings)} stock movements...")
db.bulk_insert_mappings(models.StockMovement, movement_mappings)
db.commit()

# Seed Patient Footfall (4,500+ records)
# 25 facilities * 180 days = 4,500 records
print("6. Seeding Patient Footfall Records...")
footfall_mappings = []

for f in db_facilities:
    facility_staff = facility_staff_map[f.facility_id]
    nurses = [s for s in facility_staff if s.role == 'nurse']
    nurse_staff_id = nurses[0].staff_id if nurses else facility_staff[0].staff_id
    
    # Establish baseline footfall (CHCs higher than PHCs)
    base_opd = 80 if f.type == "CHC" else 30
    base_ipd = 10 if f.type == "CHC" else 2
    
    for d in range(180):
        current_date = START_DATE + timedelta(days=d)
        
        # Seasonality - Monsoon spikes (July, Aug, Sep)
        # Months 6, 7, 8 (June, July, August) in 180-day window
        monsoon_multiplier = 1.0
        if current_date.month in [7, 8, 9]:
            monsoon_multiplier = 1.4  # 40% increase in cases
            
        # Sunday pattern - drastically lower
        is_sunday = current_date.weekday() == 6
        if is_sunday:
            opd = random.randint(2, int(base_opd * 0.2))
            ipd = random.randint(0, int(base_ipd * 0.3))
        else:
            opd = int(random.randint(int(base_opd * 0.7), int(base_opd * 1.3)) * monsoon_multiplier)
            ipd = int(random.randint(int(base_ipd * 0.5), int(base_ipd * 1.5)) * monsoon_multiplier)
            
        footfall_mappings.append({
            "record_id": str(uuid.uuid4()),
            "facility_id": f.facility_id,
            "department": "General",
            "record_date": current_date,
            "opd_count": opd,
            "ipd_count": ipd,
            "source": "manual",
            "recorded_by": nurse_staff_id
        })

print(f"Inserting {len(footfall_mappings)} footfall records...")
db.bulk_insert_mappings(models.FootfallRecord, footfall_mappings)
db.commit()

# Seed Bed Status (750+ records)
# We will do daily snapshots for 180 days. 25 facilities * 180 = 4,500 status records overall.
print("7. Seeding Bed Status Records...")
bed_mappings = []

for f in db_facilities:
    facility_staff = facility_staff_map[f.facility_id]
    nurses = [s for s in facility_staff if s.role == 'nurse']
    nurse_staff_id = nurses[0].staff_id if nurses else facility_staff[0].staff_id
    
    wards = ["General", "Maternity"]
    if f.type == "CHC":
        wards.extend(["Pediatric", "ICU"])
        
    for w in wards:
        # Determine bed capacity per ward
        if w == "General":
            total_beds = int(f.total_bed_capacity * 0.6)
        elif w == "Maternity":
            total_beds = int(f.total_bed_capacity * 0.3)
        elif w == "Pediatric":
            total_beds = int(f.total_bed_capacity * 0.2)
        else:  # ICU
            total_beds = max(2, int(f.total_bed_capacity * 0.1))
            
        # Daily logs
        occupied = int(total_beds * random.uniform(0.1, 0.5))
        for d in range(180):
            current_date = START_DATE + timedelta(days=d)
            dt = datetime.combine(current_date, datetime.min.time())
            
            # Occupancy fluctuates daily
            change = random.choice([-2, -1, 0, 1, 2])
            occupied = max(0, min(total_beds, occupied + change))
            
            bed_mappings.append({
                "status_id": str(uuid.uuid4()),
                "facility_id": f.facility_id,
                "ward_type": w,
                "total_beds": total_beds,
                "occupied_beds": occupied,
                "updated_by": nurse_staff_id,
                "timestamp": dt + timedelta(hours=random.randint(8, 20))
            })

print(f"Inserting {len(bed_mappings)} bed status entries...")
db.bulk_insert_mappings(models.BedStatus, bed_mappings)
db.commit()

# Seed Attendance Records (27,000+)
# 150 staff * 180 days = 27,000 records
print("8. Seeding Attendance Records...")
attendance_mappings = []

# Intentional underperforming facilities (higher absenteeism)
underperforming_facilities = [db_facilities[3].facility_id, db_facilities[7].facility_id]

for f in db_facilities:
    facility_staff = facility_staff_map[f.facility_id]
    is_underperforming = f.facility_id in underperforming_facilities
    
    for s in facility_staff:
        for d in range(180):
            current_date = START_DATE + timedelta(days=d)
            
            # Sundays: scheduled=False for most staff except emergency nurses/MOs
            is_sunday = current_date.weekday() == 6
            scheduled = True
            
            if is_sunday:
                if s.role not in ["nurse", "medical_officer"]:
                    scheduled = False
                elif random.random() < 0.5: # 50% schedule chance for medical staff on Sundays
                    scheduled = False
                    
            if not scheduled:
                continue
                
            # Determine status
            rand = random.random()
            
            # Baseline absent rates: 15-20% for underperforming, 2-5% for normal
            absent_threshold = 0.18 if is_underperforming else 0.04
            late_threshold = absent_threshold + 0.10
            leave_threshold = late_threshold + 0.03
            
            if rand < absent_threshold:
                status_str = "absent"
                check_in = None
                check_out = None
            elif rand < late_threshold:
                status_str = "late"
                check_in = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=9, minutes=random.randint(15, 60))
                check_out = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=17)
            elif rand < leave_threshold:
                status_str = "leave"
                check_in = None
                check_out = None
            else:
                status_str = "present"
                check_in = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=8, minutes=random.randint(30, 59))
                check_out = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=17, minutes=random.randint(0, 30))
                
            attendance_mappings.append({
                "record_id": str(uuid.uuid4()),
                "facility_id": f.facility_id,
                "staff_id": s.staff_id,
                "role": s.role,
                "scheduled": True,
                "check_in_at": check_in,
                "check_out_at": check_out,
                "status": status_str,
                "attendance_date": current_date,
                "source": "app"
            })

print(f"Inserting {len(attendance_mappings)} attendance records...")
# Batch inserting attendance records in chunks to prevent memory blowup or SQLite statement limits
chunk_size = 5000
for i in range(0, len(attendance_mappings), chunk_size):
    chunk = attendance_mappings[i:i+chunk_size]
    db.bulk_insert_mappings(models.AttendanceRecord, chunk)
    db.commit()

# Seed Diagnostic Audits (2,250+)
# 25 facilities * 6 months * 10 tests = 1,500 audit entries
print("9. Seeding Diagnostic Audits...")
audit_mappings = []

for f in db_facilities:
    facility_staff = facility_staff_map[f.facility_id]
    nurses = [s for s in facility_staff if s.role == 'nurse']
    auditor_id = nurses[0].staff_id if nurses else facility_staff[0].staff_id
    
    # 6 monthly audit cycles
    for m in range(6):
        audit_date = START_DATE + timedelta(days=m*30 + 15)
        
        for test in db_tests:
            # PHCs don't support Chest X-Ray and ECG
            if f.type == "PHC" and test.test_name in ["Chest X-Ray", "Electrocardiogram (ECG)"]:
                status_str = "unavailable"
                reagent = 0
            else:
                # 90% available, 10% limited/unavailable
                rand = random.random()
                if rand < 0.05:
                    status_str = "unavailable"
                    reagent = 0
                elif rand < 0.12:
                    status_str = "limited"
                    reagent = random.randint(1, 10)
                else:
                    status_str = "available"
                    reagent = random.randint(50, 500)
                    
            audit_mappings.append({
                "audit_id": str(uuid.uuid4()),
                "facility_id": f.facility_id,
                "test_id": test.test_id,
                "status": status_str,
                "reagent_stock": reagent,
                "audit_date": audit_date,
                "auditor_id": auditor_id,
                "notes": "Monthly quality check" if status_str == 'available' else "Reagent shortage",
                "attachment_url": f"https://s3.ap-south-1.amazonaws.com/swasth-ai-audits/audit_{f.hfr_id}_{audit_date.isoformat()}.jpg" if status_str == 'available' else None
            })

print(f"Inserting {len(audit_mappings)} diagnostic audits...")
db.bulk_insert_mappings(models.DiagnosticAudit, audit_mappings)
db.commit()

# Seed alerts
print("10. Seeding Initial Alerts...")
# Generate some active alerts for our dashboard demo
for f in db_facilities[:5]:  # Generate alerts for first 5 facilities
    alert1 = models.Alert(
        facility_id=f.facility_id,
        alert_type="stock_out",
        severity="critical",
        title="Critical Medicine Stockout",
        message="Paracetamol 500mg has run out at this facility. Current stock: 0.",
        status="active",
        routed_to_role="pharmacist",
        extra_metadata={"sku_name": "Paracetamol 500mg", "deficit": 200}
    )
    db.add(alert1)
    
    alert2 = models.Alert(
        facility_id=f.facility_id,
        alert_type="attendance_gap",
        severity="high",
        title="Staff Absenteeism Alert",
        message="Medical Officer has not checked in today.",
        status="active",
        routed_to_role="medical_officer"
    )
    db.add(alert2)

db.commit()

# Seed Recommendations
print("11. Seeding Sample Recommendations...")
# Seed a few stock redistribution recommendations
rec1 = models.Recommendation(
    source_facility_id=db_facilities[0].facility_id,  # CHC with surplus
    target_facility_id=db_facilities[5].facility_id,  # PHC with deficit
    resource_type="medicine",
    resource_id=db_stock_items[0].sku_id,
    quantity=500,
    rationale="Chinhat CHC has an excess surplus of Paracetamol 500mg (2000 units), while Chinhat PHC 1 is projected to stock out in 2 days. Distance between facilities is 4.5 km.",
    urgency_score=85.50,
    distance_km=4.50,
    status="pending"
)
db.add(rec1)

rec2 = models.Recommendation(
    source_facility_id=db_facilities[0].facility_id,
    target_facility_id=db_facilities[6].facility_id,
    resource_type="medicine",
    resource_id=db_stock_items[1].sku_id,
    quantity=1000,
    rationale="Chinhat CHC has an excess surplus of Amoxicillin 250mg (1500 units), while Chinhat PHC 2 has run out completely. Distance between facilities is 6.2 km.",
    urgency_score=95.00,
    distance_km=6.20,
    status="pending"
)
db.add(rec2)
db.commit()

# Seed Facility Scores
print("12. Seeding Facility Performance Scores...")
# Calculate and seed composite scores for the previous month
prev_month_start = date.today() - timedelta(days=30)
prev_month_end = date.today()

for f in db_facilities:
    is_underperforming = f.facility_id in underperforming_facilities
    
    if is_underperforming:
        stock_rel = random.uniform(50.0, 70.0)
        attn_rate = random.uniform(60.0, 75.0)
        bed_turn = random.uniform(40.0, 60.0)
        test_avail = random.uniform(50.0, 70.0)
        comp = (stock_rel * 0.35) + (attn_rate * 0.25) + (bed_turn * 0.20) + (test_avail * 0.20)
        flagged = True
        reasons = ["Low doctor attendance rates", "Frequent critical medicine stock-outs"]
    else:
        stock_rel = random.uniform(85.0, 98.0)
        attn_rate = random.uniform(90.0, 98.0)
        bed_turn = random.uniform(70.0, 90.0)
        test_avail = random.uniform(85.0, 95.0)
        comp = (stock_rel * 0.35) + (attn_rate * 0.25) + (bed_turn * 0.20) + (test_avail * 0.20)
        flagged = False
        reasons = []
        
    score = models.FacilityScore(
        facility_id=f.facility_id,
        period_start=prev_month_start,
        period_end=prev_month_end,
        stock_reliability=round(stock_rel, 2),
        attendance_rate=round(attn_rate, 2),
        bed_turnover=round(bed_turn, 2),
        test_availability=round(test_avail, 2),
        composite_score=round(comp, 2),
        is_flagged=flagged,
        flag_reasons=reasons
    )
    db.add(score)

db.commit()
db.close()

print("\nDatabase seeded successfully!")
print("Total Facilities: 25")
print("Total Staff: 102 (including DHO & Admin)")
print("Total Stock Items: ~2,500 (100 per facility)")
print("Total Stock Movements: 25,000+")
print("Total Footfall Records: 4,500 (1 per facility/day)")
print("Total Bed Status Records: ~10,000 (daily updates across general/maternity/pediatric/icu wards)")
print("Total Attendance Records: 18,000+")
print("Total Diagnostic Tests: 10")
print("Total Diagnostic Audits: 1,500")
