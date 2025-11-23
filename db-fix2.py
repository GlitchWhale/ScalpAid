from sqlalchemy import text
from database import engine

# Step 1: Add timestamp column if it doesn't exist
with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE sensor_readings
        ADD COLUMN IF NOT EXISTS timestamp BIGINT NULL;
    """))
    conn.commit()
print("✅ timestamp column ensured in sensor_readings table")

# Step 2: Backfill existing rows with UNIX timestamp from created_at
with engine.connect() as conn:
    conn.execute(text("""
        UPDATE sensor_readings
        SET timestamp = UNIX_TIMESTAMP(created_at)
        WHERE timestamp IS NULL;
    """))
    conn.commit()
print("✅ Existing rows backfilled with timestamp")
