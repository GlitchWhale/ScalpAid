from sqlalchemy import text
from database import engine

# One-time fix to add google_id column if it doesn't exist
with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE NULL;
    """))
    conn.commit()

print(" google_id column ensured in users table")
INSERT INTO sensor_readings (
    id,
    device,
    temperature,
    moisture_raw,
    moisture_voltage,
    moisture_percent,
    state,
    timestamp
  )
VALUES (
    id:int,
    'device:varchar',
    'temperature:float',
    moisture_raw:int,
    'moisture_voltage:float',
    'moisture_percent:float',
    'state:varchar',
    'timestamp:bigint'
  );