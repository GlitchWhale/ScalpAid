from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    # Add the timestamp column if it doesn't exist
    conn.execute(text("""
        ALTER TABLE sensor_readings
        ADD COLUMN IF NOT EXISTS timestamp BIGINT NULL;
    """))
    conn.commit()
    print("✅ timestamp column ensured in sensor_readings table")

    # Optional: backfill existing rows from created_at
    conn.execute(text("""
        UPDATE sensor_readings
        SET timestamp = UNIX_TIMESTAMP(created_at)
        WHERE timestamp IS NULL;
    """))
    conn.commit()
    print("✅ Existing rows backfilled with timestamp")
