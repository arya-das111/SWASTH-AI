from sqlalchemy.orm import Session
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models

def log_action(
    db: Session,
    table_name: str,
    record_id: str,
    action: str,
    old_value: dict = None,
    new_value: dict = None,
    user_id: str = None,
    ip_address: str = "127.0.0.1"
):
    try:
        log_entry = models.AuditLog(
            table_name=table_name,
            record_id=str(record_id),
            action=action,
            old_value=old_value,
            new_value=new_value,
            user_id=user_id,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # Don't break main flow if auditing logs fail (fail-safe audit pattern)
        db.rollback()
        print(f"FAILED TO WRITE AUDIT LOG: {e}")
