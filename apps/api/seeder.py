import os
import uuid
import random
from datetime import datetime, date, timedelta
from passlib.hash import bcrypt

import models
from database import engine, SessionLocal

def seed_database_if_empty():
    db = SessionLocal()
    try:
        # Check if database has users
        if db.query(models.User).count() > 0:
            print("Database already contains users. Skipping auto-seed.")
            return
            
        print("Database is empty. Initiating automatic database seeding...")
        
        # 1. Seed Diagnostic Tests
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
        
        # 2. Seed Facilities (25 facilities: 5 CHCs, 20 PHCs)
        BLOCKS = ["Chinhat", "Mohanlalganj", "Kakori", "Malihabad", "Bakshi Ka Talab"]
        db_facilities = []
        
        # 5 CHCs
        for i in range(5):
            block = BLOCKS[i]
            chc = models.Facility(
                hfr_id=f"CHC-LKO-{block.upper()[:3]}-01",
                name=f"{block} CHC",
                type="CHC",
                district="Lucknow",
                block=block,
                state="Uttar Pradesh",
                latitude=26.8467 + random.uniform(-0.05, 0.05),
                longitude=80.9462 + random.uniform(-0.05, 0.05),
                total_bed_capacity=30,
                default_language=random.choice(["hi", "en"])
            )
            db.add(chc)
            db_facilities.append(chc)
            
        # 20 PHCs
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
                latitude=26.8467 + random.uniform(-0.08, 0.08),
                longitude=80.9462 + random.uniform(-0.08, 0.08),
                total_bed_capacity=random.choice([6, 10]),
                default_language=random.choice(["hi", "en"])
            )
            db.add(phc)
            db_facilities.append(phc)
        db.commit()
        
        # 3. Seed Staff and Users
        hashed_password = bcrypt.hash("password123")
        
        # Seed District Health Officer (DHO)
        dho_staff = models.Staff(
            facility_id=db_facilities[0].facility_id,
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
        
        # Seed standard staff and users
        facility_staff_map = {}
        first_phc_id = None
        
        for f in db_facilities:
            facility_staff_map[f.facility_id] = []
            
            # MO
            mo = models.Staff(
                facility_id=f.facility_id,
                name=f"Dr. Rajesh {f.name.split()[0]}",
                role="medical_officer",
                phone=f"9000{random.randint(100000, 999999)}",
                email=f"mo.{f.name.lower().replace(' ', '')}@swasth.gov.in",
                language_pref=f.default_language
            )
            db.add(mo)
            
            # Pharmacist
            pharmacist = models.Staff(
                facility_id=f.facility_id,
                name=f"Suresh Sharma ({f.name.split()[0]})",
                role="pharmacist",
                phone=f"9111{random.randint(100000, 999999)}",
                email=f"pharma.{f.name.lower().replace(' ', '')}@swasth.gov.in",
                language_pref=f.default_language
            )
            db.add(pharmacist)
            
            # Nurse
            nurse = models.Staff(
                facility_id=f.facility_id,
                name=f"Sister Geeta ({f.name.split()[0]})",
                role="nurse",
                phone=f"9222{random.randint(100000, 999999)}",
                email=f"nurse.{f.name.lower().replace(' ', '')}@swasth.gov.in",
                language_pref=f.default_language
            )
            db.add(nurse)
            
            # Clerk
            clerk = models.Staff(
                facility_id=f.facility_id,
                name=f"Amit Verma ({f.name.split()[0]})",
                role="store_clerk",
                phone=f"9333{random.randint(100000, 999999)}",
                email=f"clerk.{f.name.lower().replace(' ', '')}@swasth.gov.in",
                language_pref=f.default_language
            )
            db.add(clerk)
            
            db.commit()
            facility_staff_map[f.facility_id].extend([mo, pharmacist, nurse, clerk])
            
            # Seed explicit credentials for first PHC
            if first_phc_id is None and f.type == "PHC":
                first_phc_id = f.facility_id
                
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
                
                ph_user = models.User(
                    staff_id=pharmacist.staff_id,
                    username="pharmacist_phc1",
                    password_hash=hashed_password,
                    role="pharmacist",
                    facility_id=f.facility_id,
                    district=f.district,
                    state=f.state,
                    language_pref=f.default_language
                )
                db.add(ph_user)
                
        db.commit()
        
        # 4. Seed Stock Items (SKU Library)
        MEDICINE_LIB = [
            {"name": "Paracetamol 500mg", "generic": "Paracetamol", "category": "Analgesic", "unit": "tablets"},
            {"name": "Amoxicillin 250mg", "generic": "Amoxicillin", "category": "Antibiotic", "unit": "tablets"},
            {"name": "ORS Powder 20.5g", "generic": "Oral Rehydration Salts", "category": "ORS/Nutrition", "unit": "sachets"},
            {"name": "Artesunate 60mg", "generic": "Artesunate", "category": "Anti-malarial", "unit": "vials"},
            {"name": "Metformin 500mg", "generic": "Metformin", "category": "Anti-diabetic", "unit": "tablets"},
            {"name": "Amlodipine 5mg", "generic": "Amlodipine", "category": "Cardiovascular", "unit": "tablets"},
            {"name": "Salbutamol Inhaler 100mcg", "generic": "Salbutamol", "category": "Respiratory", "unit": "inhalers"},
        ]
        
        db_stock_items = []
        for f in db_facilities:
            for item in MEDICINE_LIB:
                stock_item = models.StockItem(
                    facility_id=f.facility_id,
                    medicine_name=item["name"],
                    generic_name=item["generic"],
                    category=item["category"],
                    unit=item["unit"],
                    batch_no=f"BAT-{random.randint(100, 999)}",
                    quantity=random.randint(100, 800),
                    expiry_date=date.today() + timedelta(days=random.randint(100, 500)),
                    min_threshold=150,
                    max_threshold=1000
                )
                db.add(stock_item)
                db_stock_items.append(stock_item)
        db.commit()
        
        # 5. Seed Patient Footfall (to ensure Outbreak Predictor works)
        START_DATE = date.today() - timedelta(days=15)
        footfall_records = []
        for f in db_facilities:
            nurse_staff_id = facility_staff_map[f.facility_id][2].staff_id
            for d in range(15):
                current_date = START_DATE + timedelta(days=d)
                
                # Baseline
                base_opd = 60 if f.type == "CHC" else 25
                opd = random.randint(base_opd - 10, base_opd + 10)
                ipd = random.randint(1, 5)
                
                # Create a local spike for Kakori and Mohanlalganj to trigger Outbreak alerts
                if d >= 10:
                    if "Kakori" in f.name:
                        opd = int(opd * 2.5)
                    elif "Mohanlalganj" in f.name:
                        opd = int(opd * 2.0)
                        
                rec = models.FootfallRecord(
                    facility_id=f.facility_id,
                    department="General",
                    record_date=current_date,
                    opd_count=opd,
                    ipd_count=ipd,
                    source="manual",
                    recorded_by=nurse_staff_id
                )
                db.add(rec)
        db.commit()
        
        # 6. Seed Attendance Records (past 7 days + today)
        print("Auto-seeding Attendance & Roster logs...")
        for f in db_facilities:
            staff_list = facility_staff_map[f.facility_id]
            for d in range(7):
                current_date = date.today() - timedelta(days=d)
                for s in staff_list:
                    # Let's simulate some absences
                    status = "present"
                    # Create absenteeism warning: Sister Geeta has > 3 absences
                    if s.name.startswith("Sister Geeta") and d in [1, 3, 5]:
                        status = "absent"
                    # Create Doctor Coverage Gap today (d=0) for Mohanlalganj PHC 1
                    elif s.role == "medical_officer" and d == 0 and "Mohanlalganj PHC" in f.name:
                        status = "absent"
                    
                    att = models.AttendanceRecord(
                        facility_id=f.facility_id,
                        staff_id=s.staff_id,
                        attendance_date=current_date,
                        role=s.role,
                        status=status,
                        check_in_at=datetime.now() - timedelta(hours=random.randint(8, 12)) if status == "present" else None,
                        check_out_at=datetime.now() - timedelta(hours=random.randint(1, 4)) if status == "present" else None,
                        source="app"
                    )
                    db.add(att)
        db.commit()

        # 7. Seed Bed Status snapshots
        print("Auto-seeding Wards & Bed logs...")
        for f in db_facilities:
            wards = ["General", "Maternity"]
            if f.type == "CHC":
                wards.extend(["Pediatric", "ICU"])
            
            for w in wards:
                tot_beds = 15 if w == "General" else 8
                if f.type == "PHC":
                    tot_beds = 5 if w == "General" else 2
                
                occupied = random.randint(1, tot_beds - 1)
                # Create a bed turnover spike warning for Chinhat CHC General Ward
                if f.name == "Chinhat CHC" and w == "General":
                    occupied = tot_beds - 1
                    
                bs = models.BedStatus(
                    facility_id=f.facility_id,
                    ward_type=w,
                    total_beds=tot_beds,
                    occupied_beds=occupied,
                    timestamp=datetime.now() - timedelta(hours=random.randint(2, 6))
                )
                db.add(bs)
        db.commit()

        # 8. Seed Diagnostics Test Availability
        print("Auto-seeding Diagnostics Test Availability...")
        for f in db_facilities:
            for t in db_tests:
                # Randomly mark some mandated tests as unavailable to trigger compliance gaps
                avail = "available"
                reagent = random.randint(20, 200)
                if t.is_mandated and random.random() < 0.15:
                    avail = "unavailable"
                    reagent = 0
                    
                da = models.DiagnosticAudit(
                    facility_id=f.facility_id,
                    test_id=t.test_id,
                    status=avail,
                    reagent_stock=reagent,
                    audit_date=date.today() - timedelta(days=random.randint(0, 2)),
                    auditor_id=facility_staff_map[f.facility_id][2].staff_id
                )
                db.add(da)
        db.commit()

        # 9. Seed AI Stock Redistribution Recommendations
        print("Auto-seeding AI Stock Redistribution suggestions...")
        # We need surplus items
        chinhat_chc = next(x for x in db_facilities if x.name == "Chinhat CHC")
        kakori_phc = next(x for x in db_facilities if x.name == "Kakori PHC 1")
        
        # Retrieve or find matching medicine
        para_sku = db.query(models.StockItem).filter(
            models.StockItem.facility_id == chinhat_chc.facility_id,
            models.StockItem.medicine_name == "Paracetamol 500mg"
        ).first()
        
        if para_sku:
            reco = models.Recommendation(
                source_facility_id=chinhat_chc.facility_id,
                target_facility_id=kakori_phc.facility_id,
                resource_type="medicine",
                resource_id=para_sku.sku_id,
                quantity=200,
                rationale="Chinhat CHC has surplus Paracetamol stock (850 units) projecting 400+ days supply. Kakori PHC 1 is below safety threshold (42 units) with projected stockout in 6 days.",
                distance_km=18.4,
                status="pending",
                created_at=datetime.now() - timedelta(hours=4)
            )
            db.add(reco)
            
        # Seed another recommendation for ORS
        ors_sku = db.query(models.StockItem).filter(
            models.StockItem.facility_id == chinhat_chc.facility_id,
            models.StockItem.medicine_name == "ORS Powder 20.5g"
        ).first()
        if ors_sku:
            reco2 = models.Recommendation(
                source_facility_id=chinhat_chc.facility_id,
                target_facility_id=kakori_phc.facility_id,
                resource_type="medicine",
                resource_id=ors_sku.sku_id,
                quantity=150,
                rationale="Chinhat CHC holds surplus ORS sachets (620 units). Kakori PHC 1 has high footfall load with near stockout status.",
                distance_km=18.4,
                status="pending",
                created_at=datetime.now() - timedelta(hours=2)
            )
            db.add(reco2)
        db.commit()
        print("Auto-seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during auto-seeding: {e}")
    finally:
        db.close()
