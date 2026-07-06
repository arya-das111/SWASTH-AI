import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Numeric, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Facility(Base):
    __tablename__ = "facilities"

    facility_id = Column(String(36), primary_key=True, default=generate_uuid)
    hfr_id = Column(String(50), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)  # 'PHC' or 'CHC'
    district = Column(String(100), nullable=False)
    block = Column(String(100), nullable=True)
    state = Column(String(100), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    total_bed_capacity = Column(Integer, default=0)
    default_language = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    staff_members = relationship("Staff", back_populates="facility")
    stock_items = relationship("StockItem", back_populates="facility")
    footfall_records = relationship("FootfallRecord", back_populates="facility")
    bed_statuses = relationship("BedStatus", back_populates="facility")
    attendance_records = relationship("AttendanceRecord", back_populates="facility")
    diagnostic_audits = relationship("DiagnosticAudit", back_populates="facility")
    alerts = relationship("Alert", back_populates="facility")

class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # pharmacist, nurse, medical_officer, dho, state_admin, etc.
    phone = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    language_pref = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    facility = relationship("Facility", back_populates="staff_members")
    user = relationship("User", back_populates="staff", uselist=False)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    staff_id = Column(String(36), ForeignKey("staff.staff_id"), unique=True, nullable=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    language_pref = Column(String(10), default="en")
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff = relationship("Staff", back_populates="user")

class StockItem(Base):
    __tablename__ = "stock_items"

    sku_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=False)  # tablets, ml, vials, etc.
    batch_no = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=True)
    min_threshold = Column(Integer, nullable=False, default=0)
    max_threshold = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    facility = relationship("Facility", back_populates="stock_items")
    movements = relationship("StockMovement", back_populates="stock_item")

class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id = Column(String(36), primary_key=True, default=generate_uuid)
    sku_id = Column(String(36), ForeignKey("stock_items.sku_id"), nullable=False)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    movement_type = Column(String(10), nullable=False)  # 'in', 'out', 'transfer', 'expired', 'wastage'
    quantity = Column(Integer, nullable=False)
    batch_no = Column(String(100), nullable=True)
    reference_note = Column(String(500), nullable=True)
    user_id = Column(String(36), ForeignKey("staff.staff_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    stock_item = relationship("StockItem", back_populates="movements")

class FootfallRecord(Base):
    __tablename__ = "footfall_records"

    record_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    department = Column(String(100), default="General")
    record_date = Column(Date, nullable=False)
    opd_count = Column(Integer, nullable=False, default=0)
    ipd_count = Column(Integer, nullable=False, default=0)
    source = Column(String(20), default="manual")  # 'manual', 'forecast', 'system'
    recorded_by = Column(String(36), ForeignKey("staff.staff_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    facility = relationship("Facility", back_populates="footfall_records")

class BedStatus(Base):
    __tablename__ = "bed_status"

    status_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    ward_type = Column(String(50), nullable=False)  # 'General', 'Maternity', 'ICU', 'HDU', 'Pediatric', 'Emergency'
    total_beds = Column(Integer, nullable=False, default=0)
    occupied_beds = Column(Integer, nullable=False, default=0)
    updated_by = Column(String(36), ForeignKey("staff.staff_id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    facility = relationship("Facility", back_populates="bed_statuses")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    record_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    staff_id = Column(String(36), ForeignKey("staff.staff_id"), nullable=False)
    role = Column(String(50), nullable=False)
    scheduled = Column(Boolean, default=True)
    check_in_at = Column(DateTime(timezone=True), nullable=True)
    check_out_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="absent")  # 'present', 'absent', 'late', 'half_day', 'leave'
    attendance_date = Column(Date, nullable=False)
    source = Column(String(20), default="app")  # 'app', 'sms', 'ussd', 'manual'
    check_in_lat = Column(Float, nullable=True)
    check_in_lon = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    facility = relationship("Facility", back_populates="attendance_records")

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    test_id = Column(String(36), primary_key=True, default=generate_uuid)
    test_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  # 'Blood', 'Urine', 'Imaging', etc.
    is_mandated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DiagnosticAudit(Base):
    __tablename__ = "diagnostic_audits"

    audit_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    test_id = Column(String(36), ForeignKey("diagnostic_tests.test_id"), nullable=False)
    status = Column(String(20), nullable=False)  # 'available', 'unavailable', 'limited'
    reagent_stock = Column(Integer, default=0)
    audit_date = Column(Date, nullable=False)
    auditor_id = Column(String(36), ForeignKey("staff.staff_id"), nullable=False)
    notes = Column(String(500), nullable=True)
    attachment_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    facility = relationship("Facility", back_populates="diagnostic_audits")

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # 'stock_out', 'stock_low', 'stock_expiry', etc.
    severity = Column(String(10), nullable=False)  # 'low', 'medium', 'high', 'critical'
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="active")  # 'active', 'acknowledged', 'resolved', 'dismissed'
    routed_to_role = Column(String(50), nullable=True)
    routed_to_user = Column(String(36), ForeignKey("staff.staff_id"), nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    facility = relationship("Facility", back_populates="alerts")

class Recommendation(Base):
    __tablename__ = "recommendations"

    rec_id = Column(String(36), primary_key=True, default=generate_uuid)
    source_facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    target_facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'medicine', 'bed', 'staff', 'equipment'
    resource_id = Column(String(36), nullable=True)
    quantity = Column(Integer, nullable=True)
    rationale = Column(String(1000), nullable=False)
    urgency_score = Column(Numeric(5, 2), nullable=True)  # 0–100
    distance_km = Column(Numeric(8, 2), nullable=True)
    status = Column(String(20), default="pending")  # 'pending', 'accepted', 'rejected', 'expired'
    decided_by = Column(String(36), ForeignKey("staff.staff_id"), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    extra_metadata = Column(JSON, nullable=True)

class FacilityScore(Base):
    __tablename__ = "facility_scores"

    score_id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.facility_id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    stock_reliability = Column(Numeric(5, 2), nullable=True)
    attendance_rate = Column(Numeric(5, 2), nullable=True)
    bed_turnover = Column(Numeric(5, 2), nullable=True)
    test_availability = Column(Numeric(5, 2), nullable=True)
    composite_score = Column(Numeric(5, 2), nullable=True)
    is_flagged = Column(Boolean, default=False)
    flag_reasons = Column(JSON, nullable=True)  # Stored as list of strings
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(String(36), primary_key=True, default=generate_uuid)
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(36), nullable=False)
    action = Column(String(10), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
