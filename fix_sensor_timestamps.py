# fix_sensor_timestamps.py
from database import SessionLocal, SensorReading
from datetime import datetime

db = SessionLocal()

try:
    readings = db.query(SensorReading).all()
    print(f"Found {len(readings)} sensor readings to update.")

    for r in readings:
        if r.created_at and (not r.timestamp or r.timestamp == 0):
            r.timestamp = int(r.created_at.timestamp())
    db.commit()
    print("✅ Backfilled timestamp column from created_at for all existing rows.")

except Exception as e:
    db.rollback()
    print("❌ Error updating timestamps:", e)

finally:
    db.close()
